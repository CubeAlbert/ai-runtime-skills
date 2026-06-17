#!/usr/bin/env python3
"""Merge two PDF files into one, Chinese first then English.

Usage:
    python merge_pdfs.py CV_CHN.pdf CV_EN.pdf --output merged.pdf
    python merge_pdfs.py --help

Requires: PyPDF2 (pip install PyPDF2)
"""

import argparse
import sys
from pathlib import Path


def merge_pdfs(first: Path, second: Path, output: Path) -> None:
    """Merge two PDF files into one. Appends second after first."""
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        print("Error: PyPDF2 is not installed.", file=sys.stderr)
        print("Install it with: pip install PyPDF2", file=sys.stderr)
        sys.exit(1)

    if not first.exists():
        print(f"Error: file not found: {first}", file=sys.stderr)
        sys.exit(1)
    if not second.exists():
        print(f"Error: file not found: {second}", file=sys.stderr)
        sys.exit(1)

    merger = PdfMerger()
    try:
        merger.append(str(first))
        merger.append(str(second))
        merger.write(str(output))
        merger.close()
    except Exception as e:
        print(f"Error: failed to merge PDFs: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Merged: {output} ({first.name} + {second.name})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge two PDF files into one (Chinese CV first, then English)."
    )
    parser.add_argument(
        "first",
        type=Path,
        help="First PDF file (typically the Chinese version)",
    )
    parser.add_argument(
        "second",
        type=Path,
        help="Second PDF file (typically the English version)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output path for the merged PDF",
    )
    args = parser.parse_args()

    merge_pdfs(args.first, args.second, args.output)


if __name__ == "__main__":
    main()
