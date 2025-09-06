"""
Base CLI framework for AI Auditor system.
Provides consistent error handling, logging, and argument parsing.
"""

import sys
import argparse
import logging
import traceback
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.exceptions import AuditorException


class ExitCode(Enum):
    """Standard exit codes for CLI applications."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGS = 2
    FILE_NOT_FOUND = 3
    PERMISSION_DENIED = 4
    NETWORK_ERROR = 5
    PROCESSING_ERROR = 6
    VALIDATION_ERROR = 7


class CLIError(AuditorException):
    """CLI-specific exception."""
    
    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR):
        super().__init__(message, "CLI_ERROR")
        self.exit_code = exit_code


class BaseCLI:
    """Base class for all CLI applications."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parser = argparse.ArgumentParser(
            prog=name,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self._setup_common_args()
        self._setup_logging()
    
    def _setup_common_args(self) -> None:
        """Setup common arguments for all CLIs."""
        self.parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose logging"
        )
        self.parser.add_argument(
            "--quiet", "-q",
            action="store_true", 
            help="Enable quiet mode (minimal output)"
        )
        self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with full traces"
        )
        self.parser.add_argument(
            "--config",
            type=Path,
            help="Configuration file path"
        )
        self.parser.add_argument(
            "--output-dir", "-o",
            type=Path,
            default=Path.cwd(),
            help="Output directory (default: current directory)"
        )
        self.parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Set logging level"
        )
        self.parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview mode without actual processing"
        )
        self.parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing files"
        )
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _configure_logging(self, args: argparse.Namespace) -> None:
        """Configure logging based on arguments."""
        # Set log level
        if args.debug:
            level = logging.DEBUG
        elif args.verbose:
            level = logging.INFO
        elif args.quiet:
            level = logging.WARNING
        else:
            level = getattr(logging, args.log_level.upper())
        
        # Update handler level
        for handler in self.logger.handlers:
            handler.setLevel(level)
        
        self.logger.setLevel(level)
    
    def _handle_exception(self, e: Exception, args: argparse.Namespace) -> int:
        """Handle exceptions with appropriate exit codes."""
        if isinstance(e, CLIError):
            if not args.quiet:
                self.logger.error(str(e))
            return e.exit_code.value
        
        elif isinstance(e, AuditorException):
            if not args.quiet:
                self.logger.error(str(e))
            
            # Map exception types to exit codes
            if isinstance(e, AuditorException):
                if "file" in e.message.lower() or "not found" in e.message.lower():
                    return ExitCode.FILE_NOT_FOUND.value
                elif "permission" in e.message.lower():
                    return ExitCode.PERMISSION_DENIED.value
                elif "network" in e.message.lower() or "api" in e.message.lower():
                    return ExitCode.NETWORK_ERROR.value
                elif "validation" in e.message.lower():
                    return ExitCode.VALIDATION_ERROR.value
                else:
                    return ExitCode.PROCESSING_ERROR.value
            
            return ExitCode.GENERAL_ERROR.value
        
        else:
            # Unexpected exception
            if args.debug:
                self.logger.exception("Unexpected error occurred")
            else:
                self.logger.error(f"Unexpected error: {str(e)}")
                if not args.quiet:
                    self.logger.info("Use --debug for full traceback")
            
            return ExitCode.GENERAL_ERROR.value
    
    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate arguments (override in subclasses)."""
        pass
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration file (override in subclasses)."""
        return {}
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application."""
        try:
            # Parse arguments
            parsed_args = self.parser.parse_args(args)
            
            # Configure logging
            self._configure_logging(parsed_args)
            
            # Validate arguments
            self._validate_args(parsed_args)
            
            # Load configuration
            config = self._load_config(parsed_args.config)
            
            # Run the main logic
            return self._run_impl(parsed_args, config)
            
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return ExitCode.GENERAL_ERROR.value
        
        except Exception as e:
            return self._handle_exception(e, getattr(self, '_current_args', argparse.Namespace()))
    
    def _run_impl(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Implementation of the main logic (override in subclasses)."""
        raise NotImplementedError("Subclasses must implement _run_impl")
    
    def main(self) -> None:
        """Main entry point."""
        exit_code = self.run()
        sys.exit(exit_code)
