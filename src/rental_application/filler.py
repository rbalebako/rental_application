"""Main orchestrator for filling rental application PDFs."""

from pathlib import Path
from typing import Dict, List, Optional

from rental_application.config import config
from rental_application.field_mapper import FieldMatcher, FieldValueTransformer
from rental_application.llm_client import LLMClient, LocalLLMClient
from rental_application.models import FormFillingResult
from rental_application.pdf_handler import PDFExtractor, PDFFiller


class RentalApplicationFiller:
    """Main orchestrator for filling out rental application PDFs."""

    def __init__(
        self,
        source_pdf: str | Path,
        target_pdf: str | Path,
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize the filler.

        Args:
            source_pdf: Path to source PDF (already filled)
            target_pdf: Path to template PDF (to be filled)
            llm_client: LLM client (defaults to LocalLLMClient with Ollama)
        """
        self.source_pdf = Path(source_pdf)
        self.target_pdf = Path(target_pdf)
        self.llm_client = llm_client or LocalLLMClient()

        # Validate PDFs exist
        if not self.source_pdf.exists():
            raise FileNotFoundError(f"Source PDF not found: {source_pdf}")
        if not self.target_pdf.exists():
            raise FileNotFoundError(f"Target PDF not found: {target_pdf}")

        # Initialize components
        self.source_extractor = PDFExtractor(self.source_pdf)
        self.target_filler = PDFFiller(self.target_pdf)
        self.field_matcher = FieldMatcher(self.llm_client)

        # State
        self._source_fields: Optional[Dict[str, str]] = None
        self._target_fields: Optional[List[str]] = None
        self._field_mapping: Optional[Dict[str, str]] = None

    def get_source_fields(self) -> Dict[str, str]:
        """Extract and cache source form fields.

        Returns:
            Dictionary mapping field names to values
        """
        if self._source_fields is None:
            self._source_fields = self.source_extractor.extract_form_fields()
        return self._source_fields

    def get_target_fields(self) -> List[str]:
        """Get and cache target form fields.

        Returns:
            List of target field names
        """
        if self._target_fields is None:
            self._target_fields = self.target_filler.validate_fields()
        return self._target_fields

    def get_mapping(self) -> Dict[str, str]:
        """Get the current field mapping (compute if needed).

        Returns:
            Dictionary mapping target fields to source fields
        """
        if self._field_mapping is None:
            source_fields = list(self.get_source_fields().keys())
            target_fields = self.get_target_fields()

            self._field_mapping = self.field_matcher.match_fields(
                source_fields,
                target_fields,
                source_schema_name=self.source_pdf.stem,
                target_schema_name=self.target_pdf.stem,
            )
        return self._field_mapping

    def auto_fill(
        self,
        output_path: str | Path,
        skip_unmapped: bool = True,
    ) -> FormFillingResult:
        """Automatically fill the target PDF with source data.

        Args:
            output_path: Path where filled PDF should be saved
            skip_unmapped: Skip fields without mappings

        Returns:
            FormFillingResult with status and details
        """
        result = FormFillingResult(success=False, filled_fields=0, skipped_fields=0)

        try:
            # Get data
            source_fields = self.get_source_fields()
            mapping = self.get_mapping()

            # Build field values for target PDF
            fill_data: Dict[str, str] = {}
            unmapped_targets = []

            for target_field in self.get_target_fields():
                if target_field in mapping:
                    source_field = mapping[target_field]
                    if source_field in source_fields:
                        source_value = source_fields[source_field]
                        # Apply transformations
                        fill_value = FieldValueTransformer.transform_value(
                            source_value,
                            target_field,
                        )
                        fill_data[target_field] = fill_value
                        result.filled_fields += 1
                    else:
                        result.warnings.append(
                            f"Mapped source field '{source_field}' not found for target '{target_field}'"
                        )
                        result.skipped_fields += 1
                else:
                    if not skip_unmapped:
                        unmapped_targets.append(target_field)
                    result.skipped_fields += 1

            # Fill the PDF
            output_file = Path(output_path)
            self.target_filler.fill_form(fill_data, output_file)

            result.success = True
            result.output_path = str(output_file)

            if config.verbose:
                print(f"✓ Filled {result.filled_fields} fields, skipped {result.skipped_fields}")
                if unmapped_targets:
                    print(f"  Unmapped fields: {unmapped_targets[:5]}")

            return result

        except Exception as e:
            result.errors.append(str(e))
            if config.verbose:
                print(f"✗ Error: {e}")
            return result

    def validate(self) -> List[str]:
        """Validate the configuration and PDFs.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check LLM availability
        if not self.llm_client.is_available():
            errors.append("LLM client not available")

        # Check source PDF has fields
        source_fields = self.get_source_fields()
        if not source_fields:
            errors.append("Source PDF has no form fields")

        # Check target PDF has fields
        target_fields = self.get_target_fields()
        if not target_fields:
            errors.append("Target PDF has no form fields")

        return errors

    def save_mapping_for_reuse(self, schema_name: str) -> None:
        """Save the current mapping for future reuse.

        Args:
            schema_name: Identifier for this form schema pair
        """
        mapping = self.get_mapping()
        cache = self.field_matcher.cache
        if cache:
            cache.save_mapping(
                f"{schema_name}_source",
                f"{schema_name}_target",
                mapping,
            )

    def load_mapping_from_cache(
        self,
        schema_name: str,
    ) -> bool:
        """Load a previously saved mapping from cache.

        Args:
            schema_name: Identifier for this form schema pair

        Returns:
            True if mapping was loaded, False otherwise
        """
        cache = self.field_matcher.cache
        if not cache:
            return False

        mapping = cache.load_mapping(
            f"{schema_name}_source",
            f"{schema_name}_target",
        )
        if mapping:
            self._field_mapping = mapping
            return True
        return False
