#!/usr/bin/env python3
"""
Promethium Documentation Generation Script

This script generates API documentation from the codebase and
updates the docs/ directory with the latest information.

Usage:
    python scripts/generate_docs.py [--output-dir docs/]

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def generate_api_docs(output_dir: Path) -> None:
    """Generate API documentation using pdoc."""
    print(f"Generating API documentation to {output_dir}...")
    
    api_docs_dir = output_dir / "api"
    api_docs_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run([
        sys.executable, "-m", "pdoc",
        "--output-dir", str(api_docs_dir),
        "--html",
        "promethium"
    ], check=True)
    
    print("API documentation generated successfully")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Promethium documentation"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs"),
        help="Output directory for generated documentation"
    )
    
    args = parser.parse_args()
    
    generate_api_docs(args.output_dir)
    print("Documentation generation completed")


if __name__ == "__main__":
    main()
