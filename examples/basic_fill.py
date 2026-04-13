"""Example: Basic rental application PDF filling."""

from pathlib import Path

# Add the src directory to path for development
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rental_application import RentalApplicationFiller, LocalLLMClient


def main():
    """Fill a rental application PDF."""

    # Paths to PDFs
    source_pdf = "../filled_out.pdf"  # Already filled
    target_pdf = "../Oerlikon.pdf"  # Template to fill
    output_pdf = "../filled_application.pdf"

    # Resolve to absolute paths for better error messages
    from pathlib import Path
    script_dir = Path(__file__).parent
    source_pdf_abs = (script_dir / source_pdf).resolve()
    target_pdf_abs = (script_dir / target_pdf).resolve()

    # Create LLM client (connect to Ollama)
    # Make sure Ollama is running: ollama serve
    llm = LocalLLMClient(model="mistral")

    # Check if PDFs exist before creating filler
    if not source_pdf_abs.exists():
        print(f"❌ ERROR: Source PDF not found!")
        print(f"   Expected file: {source_pdf_abs}")
        print(f"   Looking in directory: {source_pdf_abs.parent}")
        print(f"   Files in that directory:")
        try:
            for f in source_pdf_abs.parent.glob("*.pdf"):
                print(f"     - {f.name}")
        except Exception:
            print("     (directory not accessible)")
        return

    if not target_pdf_abs.exists():
        print(f"❌ ERROR: Target PDF not found!")
        print(f"   Expected file: {target_pdf_abs}")
        print(f"   Looking in directory: {target_pdf_abs.parent}")
        print(f"   Files in that directory:")
        try:
            for f in target_pdf_abs.parent.glob("*.pdf"):
                print(f"     - {f.name}")
        except Exception:
            print("     (directory not accessible)")
        return

    # Create filler instance
    try:
        filler = RentalApplicationFiller(
            source_pdf=str(source_pdf_abs),
            target_pdf=str(target_pdf_abs),
            llm_client=llm,
        )
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return
    except Exception as e:
        print(f"❌ ERROR creating filler: {e}")
        return

    # Validate setup
    errors = filler.validate()
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return

    print("✓ Configuration valid")

    # Inspect source fields
    source_fields = filler.get_source_fields()
    print(f"Source fields: {len(source_fields)}")
    for name, value in list(source_fields.items())[:3]:
        print(f"  - {name}: {value[:30]}")

    # Inspect target fields
    target_fields = filler.get_target_fields()
    print(f"Target fields: {len(target_fields)}")
    print(f"  - First 3: {target_fields[:3]}")

    # Get field mappings (uses LLM)
    print("\nGenerating field mappings...")
    mapping = filler.get_mapping()
    print(f"Mapped {len(mapping)} fields")
    for target, source in list(mapping.items())[:3]:
        print(f"  {target} <- {source}")

    # Auto-fill the PDF
    print(f"\nFilling PDF...")
    result = filler.auto_fill(output_path=output_pdf)

    # Print results
    print("\nResults:")
    print(f"  Success: {result.success}")
    print(f"  Filled fields: {result.filled_fields}")
    print(f"  Skipped fields: {result.skipped_fields}")
    if result.errors:
        print(f"  Errors: {result.errors}")
    if result.warnings:
        print(f"  Warnings: {result.warnings[:3]}")

    if result.success:
        print(f"\n✓ Filled PDF saved to: {result.output_path}")

        # Save mapping for future use
        filler.save_mapping_for_reuse("swiss_rental_2024")
        print("✓ Mapping cached for future use")


if __name__ == "__main__":
    main()
