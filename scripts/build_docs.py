#!/usr/bin/env python3
"""
Build Sphinx documentation for AI Auditor.
"""

import sys
import subprocess
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.base import BaseCLI, ExitCode


class BuildDocsCLI(BaseCLI):
    """CLI for building Sphinx documentation."""
    
    def __init__(self):
        super().__init__()
        self.parser.description = "Build Sphinx documentation for AI Auditor"
        
        # Add specific arguments
        self.parser.add_argument(
            "--format",
            choices=["html", "pdf", "latex", "epub"],
            default="html",
            help="Output format (default: html)"
        )
        
        self.parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean build directory before building"
        )
        
        self.parser.add_argument(
            "--serve",
            action="store_true",
            help="Serve documentation after building (HTML only)"
        )
        
        self.parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch for changes and rebuild automatically"
        )
        
        self.parser.add_argument(
            "--install-deps",
            action="store_true",
            help="Install Sphinx dependencies"
        )
    
    def _run_impl(self, args):
        """Build documentation."""
        try:
            docs_dir = Path(__file__).parent.parent / "docs"
            
            if not docs_dir.exists():
                self.logger.error("Documentation directory not found")
                return ExitCode.PROCESSING_ERROR.value
            
            # Install dependencies if requested
            if args.install_deps:
                self.logger.info("Installing Sphinx dependencies...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "sphinx", "sphinx-rtd-theme", "sphinx-autodoc-typehints"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.error(f"Failed to install dependencies: {result.stderr}")
                    return ExitCode.PROCESSING_ERROR.value
                
                self.logger.info("Dependencies installed successfully")
            
            # Clean build directory if requested
            if args.clean:
                build_dir = docs_dir / "build"
                if build_dir.exists():
                    self.logger.info("Cleaning build directory...")
                    shutil.rmtree(build_dir)
            
            # Build documentation
            self.logger.info(f"Building documentation in {args.format} format...")
            
            if args.watch:
                # Watch mode
                self.logger.info("Starting watch mode...")
                result = subprocess.run([
                    "make", "-C", str(docs_dir), "watch"
                ])
            else:
                # Single build
                result = subprocess.run([
                    "make", "-C", str(docs_dir), args.format
                ])
            
            if result.returncode != 0:
                self.logger.error("Documentation build failed")
                return ExitCode.PROCESSING_ERROR.value
            
            self.logger.info("Documentation built successfully")
            
            # Serve if requested
            if args.serve and args.format == "html":
                self.logger.info("Starting documentation server...")
                self.logger.info("Documentation available at: http://localhost:8000")
                subprocess.run([
                    "make", "-C", str(docs_dir), "serve"
                ])
            
            return ExitCode.SUCCESS.value
            
        except Exception as e:
            self.logger.error(f"Documentation build failed: {e}")
            return ExitCode.PROCESSING_ERROR.value


def main():
    """Main entry point."""
    cli = BuildDocsCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())

