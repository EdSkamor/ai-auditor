"""
Validation CLI for AI Auditor system.
Handles PDF↔POP validation with tie-breaker logic.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.base import BaseCLI, CLIError, ExitCode


class ValidateCLI(BaseCLI):
    """CLI for validation operations."""

    def __init__(self):
        super().__init__(
            name="validate",
            description="Validate PDF invoices against POP data with tie-breaker logic",
        )
        self._setup_validation_args()

    def _setup_validation_args(self) -> None:
        """Setup validation-specific arguments."""
        # Mode selection
        mode_group = self.parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "--demo", action="store_true", help="Demo mode: validate single file"
        )
        mode_group.add_argument(
            "--bulk", action="store_true", help="Bulk mode: validate multiple files"
        )

        # File inputs
        self.parser.add_argument(
            "--file", "-f", type=Path, help="Input file for demo mode (PDF or Excel)"
        )
        self.parser.add_argument(
            "--input-dir", "-i", type=Path, help="Input directory for bulk mode"
        )
        self.parser.add_argument(
            "--pop-file", type=Path, help="POP data file (Excel/CSV)"
        )

        # Validation options
        self.parser.add_argument(
            "--tiebreak-weight-fname",
            type=float,
            default=0.7,
            help="Tie-breaker weight for filename matching (default: 0.7)",
        )
        self.parser.add_argument(
            "--tiebreak-min-seller",
            type=float,
            default=0.4,
            help="Minimum seller similarity threshold (default: 0.4)",
        )
        self.parser.add_argument(
            "--amount-tol",
            type=float,
            default=0.01,
            help="Amount tolerance for matching (default: 0.01)",
        )
        self.parser.add_argument(
            "--confidence-threshold",
            type=float,
            default=0.8,
            help="Minimum confidence threshold for matches (default: 0.8)",
        )
        self.parser.add_argument(
            "--enable-ocr", action="store_true", help="Enable OCR for PDF processing"
        )
        self.parser.add_argument(
            "--max-file-size-mb",
            type=int,
            default=50,
            help="Maximum file size in MB (default: 50)",
        )

        # Output options
        self.parser.add_argument(
            "--output-format",
            choices=["json", "excel", "csv"],
            default="excel",
            help="Output format (default: excel)",
        )
        self.parser.add_argument(
            "--include-details",
            action="store_true",
            help="Include detailed validation results",
        )

    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate validation-specific arguments."""
        if args.demo:
            if not args.file:
                raise CLIError(
                    "--file is required for demo mode", ExitCode.INVALID_ARGS
                )
            if not args.file.exists():
                raise CLIError(
                    f"Input file not found: {args.file}", ExitCode.FILE_NOT_FOUND
                )

        elif args.bulk:
            if not args.input_dir:
                raise CLIError(
                    "--input-dir is required for bulk mode", ExitCode.INVALID_ARGS
                )
            if not args.input_dir.exists():
                raise CLIError(
                    f"Input directory not found: {args.input_dir}",
                    ExitCode.FILE_NOT_FOUND,
                )

        if args.pop_file and not args.pop_file.exists():
            raise CLIError(
                f"POP file not found: {args.pop_file}", ExitCode.FILE_NOT_FOUND
            )

        if not (0.0 <= args.confidence_threshold <= 1.0):
            raise CLIError(
                "Confidence threshold must be between 0.0 and 1.0",
                ExitCode.INVALID_ARGS,
            )

    def _run_impl(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Run validation logic."""
        try:
            if args.demo:
                return self._run_demo_validation(args, config)
            elif args.bulk:
                return self._run_bulk_validation(args, config)
            else:
                raise CLIError("No validation mode selected", ExitCode.INVALID_ARGS)

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return ExitCode.PROCESSING_ERROR.value

    def _run_demo_validation(
        self, args: argparse.Namespace, config: Dict[str, Any]
    ) -> int:
        """Run demo validation on single file."""
        self.logger.info(f"Starting demo validation of: {args.file}")

        if args.dry_run:
            self.logger.info("DRY RUN: Would validate file")
            return ExitCode.SUCCESS.value

        try:
            from core.data_processing import read_table
            from core.pdf_indexer import index_pdf
            from core.pop_matcher import match_invoice

            # Index the PDF
            self.logger.info("Indexing PDF file...")
            pdf_result = index_pdf(args.file)

            if pdf_result.error:
                self.logger.error(f"PDF indexing failed: {pdf_result.error}")
                return ExitCode.PROCESSING_ERROR.value

            # Load POP data if provided
            pop_data = None
            if args.pop_file:
                self.logger.info("Loading POP data...")
                with open(args.pop_file, "rb") as f:
                    file_bytes = f.read()
                data = read_table(file_bytes, args.pop_file.name)
                pop_data = data["df"]

            # Convert to dict for matching
            invoice_data = {
                "invoice_id": pdf_result.invoice_id,
                "issue_date": pdf_result.issue_date,
                "total_net": pdf_result.total_net,
                "seller_guess": pdf_result.seller_guess,
                "currency": pdf_result.currency,
            }

            # Match if POP data available
            if pop_data is not None:
                self.logger.info("Matching against POP data...")
                match_result = match_invoice(
                    invoice_data, pop_data, pdf_result.source_filename
                )

                self.logger.info(f"Match result: {match_result.status.value}")
                self.logger.info(f"Criteria: {match_result.criteria.value}")
                self.logger.info(f"Confidence: {match_result.confidence:.2f}")
            else:
                self.logger.info("No POP data provided - skipping matching")

            self.logger.info("Demo validation completed successfully")
            return ExitCode.SUCCESS.value

        except Exception as e:
            self.logger.error(f"Demo validation failed: {e}")
            return ExitCode.PROCESSING_ERROR.value

    def _run_bulk_validation(
        self, args: argparse.Namespace, config: Dict[str, Any]
    ) -> int:
        """Run bulk validation on multiple files."""
        self.logger.info(f"Starting bulk validation of directory: {args.input_dir}")

        if args.dry_run:
            self.logger.info("DRY RUN: Would process bulk validation")
            return ExitCode.SUCCESS.value

        try:
            from core.run_audit import run_audit

            # Check if POP file is provided
            if not args.pop_file:
                self.logger.error("POP file is required for bulk validation")
                return ExitCode.INVALID_ARGS.value

            # Run complete audit pipeline
            self.logger.info("Running complete audit pipeline...")
            summary = run_audit(
                pdf_source=args.input_dir,
                pop_file=args.pop_file,
                output_dir=args.output_dir,
                tiebreak_weight_fname=args.tiebreak_weight_fname,
                tiebreak_min_seller=args.tiebreak_min_seller,
                amount_tolerance=args.amount_tol,
            )

            self.logger.info("Audit completed successfully")
            self.logger.info(f"Total PDFs processed: {summary['total_pdfs_processed']}")
            self.logger.info(f"Total matches: {summary['total_matches']}")
            self.logger.info(f"Total unmatched: {summary['total_unmatched']}")
            self.logger.info(f"Output directory: {summary['output_directory']}")

            return ExitCode.SUCCESS.value

        except Exception as e:
            self.logger.error(f"Bulk validation failed: {e}")
            return ExitCode.PROCESSING_ERROR.value


def main():
    """Main entry point for validation CLI."""
    cli = ValidateCLI()
    cli.main()


if __name__ == "__main__":
    main()
