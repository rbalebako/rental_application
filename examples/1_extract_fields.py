#!/usr/bin/env python3
"""Step 1: Extract all fields from a PDF and save to CSV for review/editing.

This script:
1. Opens a PDF (fillable form or scanned image)
2. Extracts all field names
3. Saves them to a CSV file for user to fill in values
"""

import sys
from pathlib import Path
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rental_application import PDFExtractor
from rental_application.config import config


def extract_and_save_to_csv(pdf_path, csv_path):
    """Extract fields from PDF and save to CSV.

    Args:
        pdf_path: Path to PDF file
        csv_path: Path to output CSV file
    """
    pdf_path = Path(pdf_path).resolve()
    csv_path = Path(csv_path).resolve()

    # Enable verbose output
    config.verbose = True

    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found!")
        print(f"   Expected: {pdf_path}")
        return False

    print(f"📋 Opening PDF: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print()

    try:
        extractor = PDFExtractor(pdf_path)

        # Get metadata
        metadata = extractor.get_metadata()
        print(f"📄 PDF Info:")
        print(f"   Pages: {metadata['num_pages']}")
        print(f"   Title: {metadata['title']}")
        print()

        # Extract fields
        print("🔍 Extracting fields...")
        fields = extractor.extract_form_fields()

        if not fields:
            print("⚠️  No fields found in PDF")
            return False

        print(f"✓ Found {len(fields)} fields")
        print()

        # Check if OCR was used
        if extractor._ocr_mode:
            print("📸 Used OCR (scanned document)")
        else:
            print("✓ Used fillable form mode")

        # Save to CSV
        print(f"\n💾 Saving to CSV: {csv_path.name}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Field Name', 'Current Value', 'New Value'])

            for field_name, value in sorted(fields.items()):
                # Current value in first PDF, leave "New Value" column empty for user
                writer.writerow([field_name, value, ''])

        print(f"✓ Saved to: {csv_path}")
        print(f"\n📝 Instructions:")
        print(f"   1. Open {csv_path.name} in Excel or text editor")
        print(f"   2. Fill in the 'New Value' column with the values you want")
        print(f"   3. Save the CSV")
        print(f"   4. Run: python3 2_fill_pdf_from_csv.py")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    # Default paths (relative to script location)
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "../Oerlikon.pdf"  # Template PDF to extract fields from
    csv_path = script_dir / "../fields.csv"  # Output CSV

    # Allow command-line arguments
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        csv_path = Path(sys.argv[2])

    print("=" * 60)
    print("Step 1: Extract PDF Fields to CSV")
    print("=" * 60)
    print()

    success = extract_and_save_to_csv(pdf_path, csv_path)

    if success:
        print("\n✓ Step 1 complete!")
        print("Next: Edit the CSV file and run script 2 to fill the PDF")
    else:
        print("\n❌ Step 1 failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
