"""
Production audit pipeline runner.
Orchestrates the complete audit process from PDF indexing to final reports.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .data_processing import FileIngester
from .exceptions import FileProcessingError, ValidationError
from .export_final_xlsx import ExcelReportGenerator
from .pdf_indexer import InvoiceData, PDFIndexer
from .pop_matcher import MatchResult, POPMatcher


class AuditPipeline:
    """Production audit pipeline with comprehensive error handling and logging."""

    def __init__(
        self,
        tiebreak_weight_fname: float = 0.7,
        tiebreak_min_seller: float = 0.4,
        amount_tolerance: float = 0.01,
        max_file_size_mb: int = 50,
    ):
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.pdf_indexer = PDFIndexer(max_file_size_mb=max_file_size_mb)
        self.pop_matcher = POPMatcher(
            tiebreak_weight_fname=tiebreak_weight_fname,
            tiebreak_min_seller=tiebreak_min_seller,
            amount_tolerance=amount_tolerance,
        )
        self.file_ingester = FileIngester()
        self.excel_generator = ExcelReportGenerator()

        # Pipeline state
        self.pdf_results: List[InvoiceData] = []
        self.pop_data: Optional[pd.DataFrame] = None
        self.match_results: List[MatchResult] = []
        self.output_dir: Optional[Path] = None

    def run_complete_audit(
        self,
        pdf_source: Path,
        pop_file: Path,
        output_dir: Path,
        run_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run complete audit pipeline."""
        start_time = datetime.now()

        try:
            # Setup output directory
            self.output_dir = output_dir
            self.output_dir.mkdir(parents=True, exist_ok=True)

            if run_name is None:
                run_name = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.logger.info(f"Starting audit pipeline: {run_name}")
            self.logger.info(f"PDF source: {pdf_source}")
            self.logger.info(f"POP file: {pop_file}")
            self.logger.info(f"Output directory: {output_dir}")

            # Step 1: Index PDFs
            self.logger.info("Step 1: Indexing PDF files...")
            self._index_pdfs(pdf_source)

            # Step 2: Load POP data
            self.logger.info("Step 2: Loading POP data...")
            self._load_pop_data(pop_file)

            # Step 3: Match invoices
            self.logger.info("Step 3: Matching invoices...")
            self._match_invoices()

            # Step 4: Generate reports
            self.logger.info("Step 4: Generating reports...")
            report_paths = self._generate_reports(run_name)

            # Step 5: Create summary
            self.logger.info("Step 5: Creating summary...")
            summary = self._create_summary(start_time, report_paths)

            self.logger.info("Audit pipeline completed successfully")
            return summary

        except Exception as e:
            self.logger.error(f"Audit pipeline failed: {e}")
            raise FileProcessingError(f"Audit pipeline failed: {e}")

    def _index_pdfs(self, pdf_source: Path) -> None:
        """Index PDF files from source."""
        try:
            if pdf_source.is_file() and pdf_source.suffix.lower() == ".zip":
                # Process ZIP file
                self.logger.info(f"Processing ZIP file: {pdf_source}")
                self.pdf_results = self.pdf_indexer.index_zip(pdf_source)
            elif pdf_source.is_dir():
                # Process directory
                self.logger.info(f"Processing directory: {pdf_source}")
                self.pdf_results = self.pdf_indexer.index_directory(
                    pdf_source, recursive=True
                )
            else:
                raise FileProcessingError(f"Invalid PDF source: {pdf_source}")

            self.logger.info(f"Indexed {len(self.pdf_results)} PDF files")

            # Save raw results
            csv_path = self.output_dir / "All_invoices.csv"
            self.pdf_indexer.save_to_csv(self.pdf_results, csv_path)

        except Exception as e:
            raise FileProcessingError(f"PDF indexing failed: {e}")

    def _load_pop_data(self, pop_file: Path) -> None:
        """Load and validate POP data."""
        try:
            if not pop_file.exists():
                raise FileProcessingError(f"POP file not found: {pop_file}")

            # Read POP file
            with open(pop_file, "rb") as f:
                file_bytes = f.read()

            data = self.file_ingester.read_table(file_bytes, pop_file.name)
            self.pop_data = data["df"]

            self.logger.info(
                f"Loaded POP data: {self.pop_data.shape[0]} rows, {self.pop_data.shape[1]} columns"
            )

            # Validate required columns
            required_columns = ["numer", "data", "netto", "kontrahent"]
            missing_columns = []
            for col in required_columns:
                if not any(
                    col.lower() in str(c).lower() for c in self.pop_data.columns
                ):
                    missing_columns.append(col)

            if missing_columns:
                self.logger.warning(f"Missing expected columns: {missing_columns}")

        except Exception as e:
            raise FileProcessingError(f"POP data loading failed: {e}")

    def _match_invoices(self) -> None:
        """Match invoices against POP data."""
        try:
            if not self.pdf_results or self.pop_data is None:
                raise ValidationError("PDF results or POP data not available")

            self.match_results = []

            for i, pdf_result in enumerate(self.pdf_results, 1):
                self.logger.info(
                    f"Matching invoice {i}/{len(self.pdf_results)}: {pdf_result.source_filename}"
                )

                # Convert InvoiceData to dict for matching
                invoice_data = {
                    "invoice_id": pdf_result.invoice_id,
                    "issue_date": pdf_result.issue_date,
                    "total_net": pdf_result.total_net,
                    "seller_guess": pdf_result.seller_guess,
                    "currency": pdf_result.currency,
                }

                # Perform matching
                match_result = self.pop_matcher.match_invoice(
                    invoice_data, self.pop_data, pdf_result.source_filename
                )

                self.match_results.append(match_result)

            self.logger.info(
                f"Completed matching for {len(self.match_results)} invoices"
            )

        except Exception as e:
            raise FileProcessingError(f"Invoice matching failed: {e}")

    def _generate_reports(self, run_name: str) -> Dict[str, Path]:
        """Generate all reports."""
        try:
            report_paths = {}

            # Create verdicts DataFrame
            verdicts_data = []
            for i, (pdf_result, match_result) in enumerate(
                zip(self.pdf_results, self.match_results)
            ):
                verdict_data = {
                    "source_filename": pdf_result.source_filename,
                    "source_path": pdf_result.source_path,
                    "invoice_id": pdf_result.invoice_id,
                    "issue_date": (
                        pdf_result.issue_date.strftime("%Y-%m-%d")
                        if pdf_result.issue_date
                        else None
                    ),
                    "total_net": pdf_result.total_net,
                    "currency": pdf_result.currency,
                    "seller_guess": pdf_result.seller_guess,
                    "status": match_result.status.value,
                    "criteria": match_result.criteria.value,
                    "confidence": match_result.confidence,
                    "pop_row_index": match_result.pop_row_index,
                    "tie_breaker_score": match_result.tie_breaker_score,
                    "seller_similarity": match_result.seller_similarity,
                    "filename_hit": match_result.filename_hit,
                    "error": pdf_result.error,
                }

                # Add comparison flags
                for flag_name, flag_value in match_result.comparison_flags.items():
                    verdict_data[f"flag_{flag_name}"] = flag_value

                verdicts_data.append(verdict_data)

            verdicts_df = pd.DataFrame(verdicts_data)

            # Save verdicts JSONL
            verdicts_jsonl_path = self.output_dir / "verdicts.jsonl"
            with open(verdicts_jsonl_path, "w", encoding="utf-8") as f:
                for _, row in verdicts_df.iterrows():
                    json.dump(row.to_dict(), f, ensure_ascii=False, default=str)
                    f.write("\n")
            report_paths["verdicts_jsonl"] = verdicts_jsonl_path

            # Save verdicts summary
            summary_stats = {
                "total_invoices": len(verdicts_df),
                "matched_invoices": len(
                    verdicts_df[verdicts_df["status"] == "znaleziono"]
                ),
                "unmatched_invoices": len(verdicts_df[verdicts_df["status"] == "brak"]),
                "error_invoices": len(verdicts_df[verdicts_df["status"] == "error"]),
                "match_rate": (
                    len(verdicts_df[verdicts_df["status"] == "znaleziono"])
                    / len(verdicts_df)
                    if len(verdicts_df) > 0
                    else 0
                ),
                "average_confidence": verdicts_df["confidence"].mean(),
                "criteria_breakdown": verdicts_df["criteria"].value_counts().to_dict(),
                "run_name": run_name,
                "timestamp": datetime.now().isoformat(),
            }

            verdicts_summary_path = self.output_dir / "verdicts_summary.json"
            with open(verdicts_summary_path, "w", encoding="utf-8") as f:
                json.dump(summary_stats, f, ensure_ascii=False, indent=2)
            report_paths["verdicts_summary"] = verdicts_summary_path

            # Generate Excel report
            excel_path = self.output_dir / f"Audyt_koncowy_{run_name}.xlsx"
            self.excel_generator.generate_report(
                pd.DataFrame([r.__dict__ for r in self.pdf_results]),
                verdicts_df,
                summary_stats,
                excel_path,
            )
            report_paths["excel_report"] = excel_path

            # Generate Top 50 mismatches CSV
            mismatches = verdicts_df[verdicts_df["status"] == "brak"].head(50)
            if not mismatches.empty:
                mismatches_path = self.output_dir / "verdicts_top50_mismatches.csv"
                mismatches.to_csv(mismatches_path, index=False, encoding="utf-8")
                report_paths["top50_mismatches"] = mismatches_path

            return report_paths

        except Exception as e:
            raise FileProcessingError(f"Report generation failed: {e}")

    def _create_summary(
        self, start_time: datetime, report_paths: Dict[str, Path]
    ) -> Dict[str, Any]:
        """Create final summary."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "run_name": report_paths.get("excel_report", Path()).stem.replace(
                "Audyt_koncowy_", ""
            ),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_pdfs_processed": len(self.pdf_results),
            "total_matches": len(
                [r for r in self.match_results if r.status.value == "znaleziono"]
            ),
            "total_unmatched": len(
                [r for r in self.match_results if r.status.value == "brak"]
            ),
            "total_errors": len(
                [r for r in self.match_results if r.status.value == "error"]
            ),
            "reports_generated": list(report_paths.keys()),
            "output_directory": str(self.output_dir),
            "success": True,
        }

        # Save summary
        summary_path = self.output_dir / "audit_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        return summary


def run_audit(
    pdf_source: Path,
    pop_file: Path,
    output_dir: Path,
    tiebreak_weight_fname: float = 0.7,
    tiebreak_min_seller: float = 0.4,
    amount_tolerance: float = 0.01,
    run_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience function to run complete audit."""
    pipeline = AuditPipeline(
        tiebreak_weight_fname=tiebreak_weight_fname,
        tiebreak_min_seller=tiebreak_min_seller,
        amount_tolerance=amount_tolerance,
    )

    return pipeline.run_complete_audit(pdf_source, pop_file, output_dir, run_name)
