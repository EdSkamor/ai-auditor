"""
Main CLI entry point for AI Auditor system.
Provides unified command-line interface for all operations.
"""

import sys
import argparse
from pathlib import Path

from .validate import ValidateCLI
from .ocr_sample import OCRSampleCLI
from .enrich_data import EnrichDataCLI
from .generate_risk_table import GenerateRiskTableCLI
from .build_docs import BuildDocsCLI


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ai-auditor",
        description="AI Auditor - Production system for invoice validation and audit support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  validate          Validate PDF invoices against POP data
  ocr-sample        Sample OCR data from PDF files
  enrich-data       Enrich company data with KRS/Whitelist
  generate-risk-table  Generate Excel risk tables
  build-docs        Build Sphinx documentation

Use 'ai-auditor <command> --help' for command-specific help.
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add subcommands
    ValidateCLI().parser.prog = "ai-auditor validate"
    subparsers.add_parser("validate", parents=[ValidateCLI().parser], add_help=False)
    
    OCRSampleCLI().parser.prog = "ai-auditor ocr-sample"
    subparsers.add_parser("ocr-sample", parents=[OCRSampleCLI().parser], add_help=False)
    
    EnrichDataCLI().parser.prog = "ai-auditor enrich-data"
    subparsers.add_parser("enrich-data", parents=[EnrichDataCLI().parser], add_help=False)
    
    GenerateRiskTableCLI().parser.prog = "ai-auditor generate-risk-table"
    subparsers.add_parser("generate-risk-table", parents=[GenerateRiskTableCLI().parser], add_help=False)
    
    BuildDocsCLI().parser.prog = "ai-auditor build-docs"
    subparsers.add_parser("build-docs", parents=[BuildDocsCLI().parser], add_help=False)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate CLI
    try:
        if args.command == "validate":
            cli = ValidateCLI()
            return cli.run(sys.argv[2:])
        elif args.command == "ocr-sample":
            cli = OCRSampleCLI()
            return cli.run(sys.argv[2:])
        elif args.command == "enrich-data":
            cli = EnrichDataCLI()
            return cli.run(sys.argv[2:])
        elif args.command == "generate-risk-table":
            cli = GenerateRiskTableCLI()
            return cli.run(sys.argv[2:])
        elif args.command == "build-docs":
            cli = BuildDocsCLI()
            return cli.run(sys.argv[2:])
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

