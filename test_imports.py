#!/usr/bin/env python3
"""Quick test to verify imports and basic functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")
try:
    from rental_application.models import FieldType, FormField, FormSchema
    print("✓ models imported")

    from rental_application.config import config
    print("✓ config imported")

    from rental_application.pdf_handler import PDFExtractor, PDFFiller
    print("✓ pdf_handler imported")

    from rental_application.llm_client import LocalLLMClient
    print("✓ llm_client imported")

    from rental_application.field_mapper import FieldMatcher, FieldValueTransformer
    print("✓ field_mapper imported")

    from rental_application.filler import RentalApplicationFiller
    print("✓ filler imported")

    print("\n✓ All imports successful!")

    # Test basic functionality
    print("\nTesting basic functionality...")
    field = FormField(name="test", type=FieldType.TEXT, value="hello")
    print(f"✓ Created FormField: {field.name} = {field.value}")

    schema = FormSchema(name="test_schema", fields={"test": field})
    print(f"✓ Created FormSchema: {schema.name}")

    print("\n✓ All basic tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
