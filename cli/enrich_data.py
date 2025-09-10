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

            # Import KRS integration
            from core.krs_integration import (
                KRSIntegration,
                search_company_by_name,
                search_company_by_nip,
                search_company_by_regon,
            )

            # Initialize KRS integration
            krs = KRSIntegration(
                api_key=args.api_key,
                cache_dir=args.cache_dir,
                cache_ttl_hours=args.cache_ttl_hours,
                rate_limit_delay=args.rate_limit_delay,
            )

            # Process input data
            if args.input_file and args.input_file.exists():
                self.logger.info(f"Processing input file: {args.input_file}")

                # Load input data
                import pandas as pd

                if args.input_file.suffix.lower() == ".csv":
                    df = pd.read_csv(args.input_file, encoding="utf-8")
                elif args.input_file.suffix.lower() in [".xlsx", ".xls"]:
                    df = pd.read_excel(args.input_file)
                else:
                    raise ValueError(
                        f"Unsupported file format: {args.input_file.suffix}"
                    )

                self.logger.info(f"Loaded {len(df)} records from {args.input_file}")

                # Convert to list of dictionaries
                companies = df.to_dict("records")

                # Enrich data
                self.logger.info("Starting data enrichment...")
                enriched_companies = krs.batch_enrich(companies)

                # Save enriched data
                enriched_df = pd.DataFrame(enriched_companies)

                if args.output_format == "csv":
                    output_path = (
                        args.output_dir
                        / f"enriched_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    )
                    enriched_df.to_csv(output_path, index=False, encoding="utf-8")
                else:
                    output_path = (
                        args.output_dir
                        / f"enriched_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    enriched_df.to_excel(output_path, index=False)

                self.logger.info(f"Enriched data saved to: {output_path}")

                # Print summary
                enriched_count = sum(
                    1 for c in enriched_companies if c.get("krs_enriched", False)
                )
                self.logger.info("Enrichment summary:")
                self.logger.info(f"  Total companies: {len(enriched_companies)}")
                self.logger.info(f"  Successfully enriched: {enriched_count}")
                self.logger.info(
                    f"  Failed: {len(enriched_companies) - enriched_count}"
                )

            else:
                # Single company search
                if args.nip:
                    self.logger.info(f"Searching company by NIP: {args.nip}")
                    result = search_company_by_nip(args.nip, args.include_inactive)
                elif args.regon:
                    self.logger.info(f"Searching company by REGON: {args.regon}")
                    result = search_company_by_regon(args.regon, args.include_inactive)
                elif args.company_name:
                    self.logger.info(f"Searching company by name: {args.company_name}")
                    result = search_company_by_name(
                        args.company_name, args.exact_match, args.include_inactive
                    )
                else:
                    raise ValueError(
                        "No search criteria provided (NIP, REGON, or company name)"
                    )

                if result.error:
                    self.logger.error(f"Search failed: {result.error}")
                    return ExitCode.PROCESSING_ERROR.value

                if not result.companies:
                    self.logger.warning("No companies found")
                    return ExitCode.SUCCESS.value

                # Print results
                self.logger.info(
                    f"Found {result.total_found} companies (query time: {result.query_time:.2f}s)"
                )

                for i, company in enumerate(result.companies, 1):
                    self.logger.info(f"Company {i}:")
                    self.logger.info(f"  NIP: {company.nip}")
                    self.logger.info(f"  REGON: {company.regon}")
                    self.logger.info(f"  Name: {company.name}")
                    self.logger.info(f"  Legal form: {company.legal_form}")
                    self.logger.info(f"  Address: {company.address}")
                    self.logger.info(f"  City: {company.city}")
                    self.logger.info(f"  Status: {company.status}")
                    self.logger.info(f"  Main activity: {company.main_activity}")
                    if company.registration_date:
                        self.logger.info(
                            f"  Registration date: {company.registration_date.strftime('%Y-%m-%d')}"
                        )

                # Save results
                if args.save_results:
                    import json

                    output_path = (
                        args.output_dir
                        / f"krs_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )

                    results_data = {
                        "query": {
                            "nip": result.query.nip,
                            "regon": result.query.regon,
                            "name": result.query.name,
                            "exact_match": result.query.exact_match,
                            "include_inactive": result.query.include_inactive,
                        },
                        "results": [
                            {
                                "nip": c.nip,
                                "regon": c.regon,
                                "name": c.name,
                                "legal_form": c.legal_form,
                                "address": c.address,
                                "city": c.city,
                                "postal_code": c.postal_code,
                                "voivodeship": c.voivodeship,
                                "status": c.status,
                                "main_activity": c.main_activity,
                                "registration_date": (
                                    c.registration_date.isoformat()
                                    if c.registration_date
                                    else None
                                ),
                                "last_updated": (
                                    c.last_updated.isoformat()
                                    if c.last_updated
                                    else None
                                ),
                            }
                            for c in result.companies
                        ],
                        "total_found": result.total_found,
                        "query_time": result.query_time,
                        "cached": result.cached,
                    }

                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(results_data, f, ensure_ascii=False, indent=2)

                    self.logger.info(f"Results saved to: {output_path}")

            # Cache statistics
            if args.show_cache_stats:
                cache_stats = krs.get_cache_stats()
                self.logger.info("Cache statistics:")
                self.logger.info(f"  Cache directory: {cache_stats['cache_dir']}")
                self.logger.info(f"  Total files: {cache_stats['total_files']}")
                self.logger.info(f"  Total size: {cache_stats['total_size_mb']:.2f} MB")
                self.logger.info(f"  TTL: {cache_stats['ttl_hours']} hours")

            # Clear cache if requested
            if args.clear_cache:
                krs.clear_cache()
                self.logger.info("Cache cleared")

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
