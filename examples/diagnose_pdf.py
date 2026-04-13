#!/usr/bin/env python3
"""Diagnose PDF form fields."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rental_application import PDFExtractor


def diagnose_pdf(pdf_path):
    """Analyze a PDF for form fields."""
    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return

    print(f"Analyzing: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print()

    try:
        extractor = PDFExtractor(pdf_path)

        # Get metadata
        metadata = extractor.get_metadata()
        print("📋 PDF Metadata:")
        print(f"  Pages: {metadata['num_pages']}")
        print(f"  Title: {metadata['title']}")
        print(f"  Creator: {metadata['creator']}")
        print()

        # Get form fields
        fields = extractor.extract_form_fields()
        print(f"📝 Form Fields: {len(fields)}")

        if len(fields) == 0:
            print("  ⚠️  NO FORM FIELDS FOUND!")
            print("  This PDF is not a fillable form.")
            print("  Options:")
            print("    1. Use a different PDF that IS a fillable form")
            print("    2. Convert your PDF to a fillable form (using Adobe Acrobat or online tools)")
            print("    3. If it's a scanned document, use OCR (not yet implemented)")
            return

        print("  Form fields found:")
        for name, value in list(fields.items())[:10]:
            value_str = str(value)[:40]
            print(f"    - {name}: '{value_str}'")

        if len(fields) > 10:
            print(f"    ... and {len(fields) - 10} more")

        # Get text
        text = extractor.extract_text()
        print()
        print(f"📄 Text in PDF: {len(text)} characters")
        print(f"  First 200 chars: {text[:200]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 diagnose.py <pdf_path>")
        print("Example: python3 diagnose.py filled_out.pdf")
        sys.exit(1)

    diagnose_pdf(sys.argv[1])
