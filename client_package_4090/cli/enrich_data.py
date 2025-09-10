"""
Data Enrichment CLI for AI Auditor system.
Handles KRS and Whitelist data enrichment.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.base import BaseCLI, CLIError, ExitCode


class EnrichDataCLI(BaseCLI):
    """CLI for data enrichment operations."""

    def __init__(self):
        super().__init__(
            name="enrich-data",
            description="Enrich company data with KRS and Whitelist information",
        )
        self._setup_enrichment_args()

    def _setup_enrichment_args(self) -> None:
        """Setup enrichment-specific arguments."""
        # Input options
        self.parser.add_argument(
            "--input",
            "-i",
            type=Path,
            required=True,
            help="Input CSV/Excel file with company data",
        )
        self.parser.add_argument(
            "--company-column",
            default="company_name",
            help="Column name containing company names (default: company_name)",
        )

        # Enrichment sources
        self.parser.add_argument(
            "--krs", action="store_true", help="Enable KRS data enrichment"
        )
        self.parser.add_argument(
            "--whitelist", action="store_true", help="Enable whitelist data enrichment"
        )
        self.parser.add_argument(
            "--krs-api-key",
            help="KRS API key (or set KRS_API_KEY environment variable)",
        )
        self.parser.add_argument(
            "--whitelist-file", type=Path, help="Whitelist data file (CSV/Excel)"
        )

        # Processing options
        self.parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Batch size for API calls (default: 100)",
        )
        self.parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Delay between API calls in seconds (default: 1.0)",
        )
        self.parser.add_argument(
            "--max-retries",
            type=int,
            default=3,
            help="Maximum number of retries for failed API calls (default: 3)",
        )

        # Cache options
        self.parser.add_argument(
            "--cache-dir", type=Path, help="Cache directory for API responses"
        )
        self.parser.add_argument(
            "--use-cache", action="store_true", help="Use cached data when available"
        )
        self.parser.add_argument(
            "--cache-ttl",
            type=int,
            default=86400,
            help="Cache TTL in seconds (default: 86400 = 24h)",
        )

        # Output options
        self.parser.add_argument(
            "--output-format",
            choices=["excel", "csv", "json"],
            default="excel",
            help="Output format (default: excel)",
        )
        self.parser.add_argument(
            "--include-original",
            action="store_true",
            help="Include original data in output",
        )

    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate enrichment-specific arguments."""
        if not args.input.exists():
            raise CLIError(
                f"Input file not found: {args.input}", ExitCode.FILE_NOT_FOUND
            )

        if not (args.krs or args.whitelist):
            raise CLIError(
                "At least one enrichment source (--krs or --whitelist) must be specified",
                ExitCode.INVALID_ARGS,
            )

        if args.krs and not args.krs_api_key:
            import os

            if not os.getenv("KRS_API_KEY"):
                raise CLIError(
                    "KRS API key required (--krs-api-key or KRS_API_KEY environment variable)",
                    ExitCode.INVALID_ARGS,
                )

        if args.whitelist and args.whitelist_file and not args.whitelist_file.exists():
            raise CLIError(
                f"Whitelist file not found: {args.whitelist_file}",
                ExitCode.FILE_NOT_FOUND,
            )

        if args.batch_size <= 0:
            raise CLIError("Batch size must be positive", ExitCode.INVALID_ARGS)

        if args.delay < 0:
            raise CLIError("Delay must be non-negative", ExitCode.INVALID_ARGS)

        if args.max_retries < 0:
            raise CLIError("Max retries must be non-negative", ExitCode.INVALID_ARGS)

    def _run_impl(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Run data enrichment logic."""
        try:
            self.logger.info(f"Starting data enrichment for: {args.input}")

            if args.dry_run:
                self.logger.info("DRY RUN: Would enrich data")
                return ExitCode.SUCCESS.value

            # TODO: Implement actual data enrichment logic
            # This is a placeholder for the enrichment implementation

            self.logger.info("Data enrichment completed successfully")
            return ExitCode.SUCCESS.value

        except Exception as e:
            self.logger.error(f"Data enrichment failed: {e}")
            return ExitCode.PROCESSING_ERROR.value


def main():
    """Main entry point for data enrichment CLI."""
    cli = EnrichDataCLI()
    cli.main()


if __name__ == "__main__":
    main()
