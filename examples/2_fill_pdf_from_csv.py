#!/usr/bin/env python3
"""Step 2: Fill PDF with values from CSV.

This script:
1. Reads the CSV file created by script 1
2. Fills the PDF with the values from the "New Value" column
3. Saves the filled PDF
"""

import sys
from pathlib import Path
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rental_application import PDFExtractor, PDFFiller
from rental_application.config import config


def fill_pdf_from_csv(pdf_path, csv_path, output_path):
    """Fill PDF with values from CSV.

    Args:
        pdf_path: Path to template PDF
        csv_path: Path to CSV with values
        output_path: Path to save filled PDF

    Returns:
        True if successful
    """
    pdf_path = Path(pdf_path).resolve()
    csv_path = Path(csv_path).resolve()
    output_path = Path(output_path).resolve()

    # Enable verbose output
    config.verbose = True

    # Check files exist
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found!")
        print(f"   Expected: {pdf_path}")
        return False

    if not csv_path.exists():
        print(f"❌ ERROR: CSV not found!")
        print(f"   Expected: {csv_path}")
        return False

    print(f"📋 Opening PDF: {pdf_path.name}")
    print(f"📄 Reading CSV: {csv_path.name}")
    print()

    try:
        # Read CSV
        print("📖 Reading CSV values...")
        values_to_fill = {}
        rows_read = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_name = row.get('Field Name', '').strip()
                new_value = row.get('New Value', '').strip()

                # Only include fields with values
                if field_name and new_value:
                    values_to_fill[field_name] = new_value
                    rows_read += 1

        print(f"✓ Read {rows_read} rows from CSV")
        print(f"✓ Will fill {len(values_to_fill)} fields with values")

        if len(values_to_fill) == 0:
            print("⚠️  No values found in CSV 'New Value' column")
            print("   Make sure you filled in the CSV file")
            return False

        print()

        # Extract fields from PDF to verify field names
        print("🔍 Validating PDF fields...")
        extractor = PDFExtractor(pdf_path)
        existing_fields = extractor.extract_form_fields()
        available_field_names = set(existing_fields.keys())

        print(f"✓ PDF has {len(available_field_names)} fields")
        print()

        # Check for matches
        matched = 0
        unmatched = []

        for field_name in values_to_fill.keys():
            if field_name in available_field_names:
                matched += 1
            else:
                unmatched.append(field_name)

        print(f"✓ Matched {matched} fields")
        if unmatched:
            print(f"⚠️  {len(unmatched)} fields not found in PDF:")
            for fname in unmatched[:5]:
                print(f"   - {fname}")
            if len(unmatched) > 5:
                print(f"   ... and {len(unmatched) - 5} more")

        # Fill PDF
        print()
        print("✏️  Filling PDF...")
        filler = PDFFiller(pdf_path)
        filler.fill_form(values_to_fill, output_path)

        print(f"✓ PDF filled!")
        print(f"📄 Output: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    # Default paths
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "../Oerlikon.pdf"  # Template PDF
    csv_path = script_dir / "../fields.csv"  # CSV with values
    output_path = script_dir / "../filled_application.pdf"  # Output

    # Allow command-line arguments
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        csv_path = Path(sys.argv[2])
    if len(sys.argv) > 3:
        output_path = Path(sys.argv[3])

    print("=" * 60)
    print("Step 2: Fill PDF from CSV")
    print("=" * 60)
    print()

    success = fill_pdf_from_csv(pdf_path, csv_path, output_path)

    if success:
        print("\n✓ Step 2 complete!")
        print(f"Your filled PDF is ready: {output_path.name}")
    else:
        print("\n❌ Step 2 failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
