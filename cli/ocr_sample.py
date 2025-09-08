"""
OCR Sample CLI for AI Auditor system.
Handles OCR sampling and database operations.
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.base import BaseCLI, ExitCode, CLIError
from core.exceptions import FileProcessingError


class OCRSampleCLI(BaseCLI):
    """CLI for OCR sampling operations."""
    
    def __init__(self):
        super().__init__(
            name="ocr-sample",
            description="Sample OCR data from PDF files and manage OCR database"
        )
        self._setup_ocr_args()
    
    def _setup_ocr_args(self) -> None:
        """Setup OCR-specific arguments."""
        # Input options
        self.parser.add_argument(
            "--input", "-i",
            type=Path,
            required=True,
            help="Input PDF file or directory"
        )
        self.parser.add_argument(
            "--sample-size",
            type=int,
            default=10,
            help="Number of pages to sample (default: 10)"
        )
        self.parser.add_argument(
            "--random-sample",
            action="store_true",
            help="Use random sampling instead of first N pages"
        )
        
        # OCR options
        self.parser.add_argument(
            "--engine",
            choices=["tesseract", "easyocr", "paddleocr"],
            default="tesseract",
            help="OCR engine to use (default: tesseract)"
        )
        self.parser.add_argument(
            "--language",
            default="pol",
            help="OCR language (default: pol)"
        )
        self.parser.add_argument(
            "--gpu-enabled",
            action="store_true",
            help="Enable GPU acceleration for OCR"
        )
        self.parser.add_argument(
            "--confidence-threshold",
            type=float,
            default=0.7,
            help="Minimum OCR confidence threshold (default: 0.7)"
        )
        
        # Database options
        self.parser.add_argument(
            "--database", "-d",
            type=Path,
            help="OCR database file path"
        )
        self.parser.add_argument(
            "--update-database",
            action="store_true",
            help="Update existing database with new samples"
        )
        self.parser.add_argument(
            "--export-samples",
            action="store_true",
            help="Export samples to CSV/JSON"
        )
        
        # Output options
        self.parser.add_argument(
            "--output-format",
            choices=["json", "csv", "excel"],
            default="json",
            help="Output format for samples (default: json)"
        )
        self.parser.add_argument(
            "--include-images",
            action="store_true",
            help="Include extracted images in output"
        )
    
    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate OCR-specific arguments."""
        if not args.input.exists():
            raise CLIError(f"Input path not found: {args.input}", ExitCode.FILE_NOT_FOUND)
        
        if args.sample_size <= 0:
            raise CLIError("Sample size must be positive", ExitCode.INVALID_ARGS)
        
        if not (0.0 <= args.confidence_threshold <= 1.0):
            raise CLIError("Confidence threshold must be between 0.0 and 1.0", ExitCode.INVALID_ARGS)
    
    def _run_impl(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Run OCR sampling logic."""
        try:
            self.logger.info(f"Starting OCR sampling from: {args.input}")
            
            if args.dry_run:
                self.logger.info("DRY RUN: Would process OCR sampling")
                return ExitCode.SUCCESS.value
            
            # Import OCR processor
            from core.ocr_processor import OCRProcessor, extract_text_from_image
            
            # Initialize OCR processor
            ocr_processor = OCRProcessor(
                engine=args.engine,
                language=args.language,
                gpu_enabled=args.gpu_enabled
            )
            
            # Process files
            results = []
            for i, file_path in enumerate(files_to_process[:args.sample_size], 1):
                self.logger.info(f"Processing {i}/{min(len(files_to_process), args.sample_size)}: {file_path.name}")
                
                try:
                    # Extract text using OCR
                    ocr_result = ocr_processor.extract_text(file_path)
                    
                    # Extract invoice fields
                    invoice_fields = ocr_processor.extract_invoice_fields(ocr_result)
                    
                    result = {
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'ocr_text': ocr_result.text[:500] + "..." if len(ocr_result.text) > 500 else ocr_result.text,
                        'confidence': ocr_result.confidence,
                        'processing_time': ocr_result.processing_time,
                        'engine': ocr_result.engine,
                        'invoice_number': invoice_fields.invoice_number,
                        'issue_date': invoice_fields.issue_date,
                        'total_net': invoice_fields.total_net,
                        'currency': invoice_fields.currency,
                        'seller_name': invoice_fields.seller_name,
                        'error': ocr_result.error
                    }
                    
                    results.append(result)
                    
                    if args.verbose:
                        self.logger.info(f"  Confidence: {ocr_result.confidence:.2f}")
                        self.logger.info(f"  Processing time: {ocr_result.processing_time:.2f}s")
                        if invoice_fields.invoice_number:
                            self.logger.info(f"  Invoice number: {invoice_fields.invoice_number}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    results.append({
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'error': str(e)
                    })
            
            # Save results
            if results:
                import json
                import pandas as pd
                
                # Save as JSON
                json_path = args.output_dir / "ocr_sample_results.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
                
                # Save as CSV
                csv_path = args.output_dir / "ocr_sample_results.csv"
                df = pd.DataFrame(results)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                self.logger.info(f"Results saved to {json_path} and {csv_path}")
                
                # Print summary
                successful = len([r for r in results if 'error' not in r or not r['error']])
                avg_confidence = sum(r.get('confidence', 0) for r in results if 'confidence' in r) / len(results)
                
                self.logger.info(f"OCR sampling completed: {successful}/{len(results)} files processed successfully")
                self.logger.info(f"Average confidence: {avg_confidence:.2f}")
            else:
                self.logger.warning("No files were processed")
            
            self.logger.info("OCR sampling completed successfully")
            return ExitCode.SUCCESS.value
        
        except Exception as e:
            self.logger.error(f"OCR sampling failed: {e}")
            return ExitCode.PROCESSING_ERROR.value


def main():
    """Main entry point for OCR sample CLI."""
    cli = OCRSampleCLI()
    cli.main()


if __name__ == "__main__":
    main()
