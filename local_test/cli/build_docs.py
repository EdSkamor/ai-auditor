"""
Documentation Build CLI for AI Auditor system.
Builds Sphinx documentation with coverage checks.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.base import BaseCLI, ExitCode, CLIError
from core.exceptions import FileProcessingError


class BuildDocsCLI(BaseCLI):
    """CLI for documentation building."""
    
    def __init__(self):
        super().__init__(
            name="build-docs",
            description="Build Sphinx documentation with coverage and quality checks"
        )
        self._setup_docs_args()
    
    def _setup_docs_args(self) -> None:
        """Setup documentation-specific arguments."""
        # Build options
        self.parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean build directory before building"
        )
        self.parser.add_argument(
            "--html",
            action="store_true",
            help="Build HTML documentation"
        )
        self.parser.add_argument(
            "--pdf",
            action="store_true",
            help="Build PDF documentation"
        )
        self.parser.add_argument(
            "--latex",
            action="store_true",
            help="Build LaTeX documentation"
        )
        self.parser.add_argument(
            "--all",
            action="store_true",
            help="Build all documentation formats"
        )
        
        # Quality checks
        self.parser.add_argument(
            "--check-docstrings",
            action="store_true",
            help="Check docstring coverage"
        )
        self.parser.add_argument(
            "--check-links",
            action="store_true",
            help="Check for broken links"
        )
        self.parser.add_argument(
            "--check-spelling",
            action="store_true",
            help="Check spelling in documentation"
        )
        
        # Output options
        self.parser.add_argument(
            "--build-dir",
            type=Path,
            default=Path("docs/_build"),
            help="Build directory (default: docs/_build)"
        )
        self.parser.add_argument(
            "--source-dir",
            type=Path,
            default=Path("docs"),
            help="Source directory (default: docs)"
        )
        self.parser.add_argument(
            "--warn-as-error",
            action="store_true",
            help="Treat warnings as errors"
        )
        
        # Advanced options
        self.parser.add_argument(
            "--parallel",
            type=int,
            default=1,
            help="Number of parallel jobs (default: 1)"
        )
        self.parser.add_argument(
            "--nitpicky",
            action="store_true",
            help="Run in nitpicky mode (more strict)"
        )
    
    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate documentation-specific arguments."""
        if not args.source_dir.exists():
            raise CLIError(f"Source directory not found: {args.source_dir}", ExitCode.FILE_NOT_FOUND)
        
        if not (args.html or args.pdf or args.latex or args.all):
            raise CLIError("At least one build format must be specified", ExitCode.INVALID_ARGS)
        
        if args.parallel <= 0:
            raise CLIError("Parallel jobs must be positive", ExitCode.INVALID_ARGS)
    
    def _check_sphinx_installed(self) -> bool:
        """Check if Sphinx is installed."""
        try:
            subprocess.run([sys.executable, "-m", "sphinx", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_sphinx_command(self, args: argparse.Namespace, command: List[str]) -> int:
        """Run a Sphinx command."""
        try:
            cmd = [sys.executable, "-m", "sphinx"] + command
            
            if args.verbose:
                self.logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, cwd=args.source_dir)
            return result.returncode
            
        except Exception as e:
            self.logger.error(f"Failed to run Sphinx command: {e}")
            return ExitCode.PROCESSING_ERROR.value
    
    def _run_impl(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Run documentation building logic."""
        try:
            # Check if Sphinx is installed
            if not self._check_sphinx_installed():
                raise CLIError("Sphinx is not installed. Install with: pip install sphinx", ExitCode.PROCESSING_ERROR)
            
            self.logger.info("Starting documentation build")
            
            if args.dry_run:
                self.logger.info("DRY RUN: Would build documentation")
                return ExitCode.SUCCESS.value
            
            # Clean build directory if requested
            if args.clean and args.build_dir.exists():
                self.logger.info(f"Cleaning build directory: {args.build_dir}")
                import shutil
                shutil.rmtree(args.build_dir)
            
            # Build documentation
            exit_code = ExitCode.SUCCESS.value
            
            if args.html or args.all:
                self.logger.info("Building HTML documentation")
                cmd = ["-b", "html", ".", str(args.build_dir / "html")]
                if args.warn_as_error:
                    cmd.append("-W")
                if args.nitpicky:
                    cmd.append("-n")
                if args.parallel > 1:
                    cmd.extend(["-j", str(args.parallel)])
                
                result = self._run_sphinx_command(args, cmd)
                if result != 0:
                    exit_code = ExitCode.PROCESSING_ERROR.value
            
            if args.pdf or args.all:
                self.logger.info("Building PDF documentation")
                cmd = ["-b", "latex", ".", str(args.build_dir / "latex")]
                if args.warn_as_error:
                    cmd.append("-W")
                if args.nitpicky:
                    cmd.append("-n")
                
                result = self._run_sphinx_command(args, cmd)
                if result != 0:
                    exit_code = ExitCode.PROCESSING_ERROR.value
                else:
                    # Build PDF from LaTeX
                    latex_dir = args.build_dir / "latex"
                    if latex_dir.exists():
                        self.logger.info("Building PDF from LaTeX")
                        try:
                            subprocess.run(["make", "all-pdf"], cwd=latex_dir, check=True)
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"Failed to build PDF: {e}")
                            exit_code = ExitCode.PROCESSING_ERROR.value
            
            if args.latex or args.all:
                self.logger.info("Building LaTeX documentation")
                cmd = ["-b", "latex", ".", str(args.build_dir / "latex")]
                if args.warn_as_error:
                    cmd.append("-W")
                if args.nitpicky:
                    cmd.append("-n")
                
                result = self._run_sphinx_command(args, cmd)
                if result != 0:
                    exit_code = ExitCode.PROCESSING_ERROR.value
            
            # Run quality checks
            if args.check_docstrings:
                self.logger.info("Checking docstring coverage")
                # TODO: Implement docstring coverage check
            
            if args.check_links:
                self.logger.info("Checking for broken links")
                # TODO: Implement link checking
            
            if args.check_spelling:
                self.logger.info("Checking spelling")
                # TODO: Implement spelling check
            
            if exit_code == ExitCode.SUCCESS.value:
                self.logger.info("Documentation build completed successfully")
            else:
                self.logger.error("Documentation build completed with errors")
            
            return exit_code
        
        except Exception as e:
            self.logger.error(f"Documentation build failed: {e}")
            return ExitCode.PROCESSING_ERROR.value


def main():
    """Main entry point for documentation build CLI."""
    cli = BuildDocsCLI()
    cli.main()


if __name__ == "__main__":
    main()
