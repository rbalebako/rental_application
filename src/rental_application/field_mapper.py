"""Field matching engine for mapping source to target form fields."""

import re
from typing import Dict, List, Optional

from rental_application.config import config
from rental_application.llm_client import LLMClient
from rental_application.utils.cache import FieldMappingCache
from rental_application.utils.prompts import field_matching_prompt


class FieldMatcher:
    """Intelligently matches source fields to target fields using LLM."""

    def __init__(
        self,
        llm_client: LLMClient,
        use_cache: bool = True,
    ):
        """Initialize field matcher.

        Args:
            llm_client: LLM client for semantic matching
            use_cache: Whether to use cached mappings
        """
        self.llm_client = llm_client
        self.use_cache = use_cache
        self.cache = FieldMappingCache() if use_cache else None

    def match_fields(
        self,
        source_fields: List[str],
        target_fields: List[str],
        source_schema_name: str = "source",
        target_schema_name: str = "target",
    ) -> Dict[str, str]:
        """Match target fields to source fields using LLM.

        Args:
            source_fields: List of available source field names
            target_fields: List of target fields to match
            source_schema_name: Identifier for source form schema
            target_schema_name: Identifier for target form schema

        Returns:
            Dictionary mapping target field names to source field names
        """
        # Check cache
        if self.use_cache and self.cache:
            cached = self.cache.load_mapping(source_schema_name, target_schema_name)
            if cached:
                return cached

        # Get matches from LLM
        mapping = self._match_fields_with_llm(source_fields, target_fields)

        # Apply confidence filtering
        filtered = {
            target: source
            for target, source in mapping.items()
            if source != "NONE"
        }

        # Cache result
        if self.use_cache and self.cache:
            self.cache.save_mapping(source_schema_name, target_schema_name, filtered)

        return filtered

    def _match_fields_with_llm(
        self,
        source_fields: List[str],
        target_fields: List[str],
    ) -> Dict[str, str]:
        """Use LLM to match fields.

        Args:
            source_fields: List of source field names
            target_fields: List of target field names

        Returns:
            Dictionary mapping target fields to source fields
        """
        prompt = field_matching_prompt(source_fields, target_fields)

        try:
            response_text = self.llm_client.generate_json(prompt, temperature=0.1)
        except Exception:
            # Fallback to simple string matching
            return self._match_fields_fallback(source_fields, target_fields)

        mapping = {}
        if isinstance(response_text, dict) and "mappings" in response_text:
            for entry in response_text["mappings"]:
                target = entry.get("target_field")
                source = entry.get("source_field", "NONE")
                if target:
                    mapping[target] = source

        return mapping

    def _match_fields_fallback(
        self,
        source_fields: List[str],
        target_fields: List[str],
    ) -> Dict[str, str]:
        """Fallback field matching using simple heuristics.

        Args:
            source_fields: List of source field names
            target_fields: List of target field names

        Returns:
            Dictionary mapping target fields to source fields
        """
        mapping = {}
        for target in target_fields:
            best_match = None
            best_score = 0.0

            for source in source_fields:
                score = self._similarity_score(target, source)
                if score > best_score:
                    best_score = score
                    best_match = source

            # Only map if similarity is above threshold
            if best_score >= config.confidence_threshold:
                mapping[target] = best_match
            else:
                mapping[target] = "NONE"

        return mapping

    @staticmethod
    def _similarity_score(field1: str, field2: str) -> float:
        """Calculate similarity score between two field names.

        Args:
            field1: First field name
            field2: Second field name

        Returns:
            Similarity score from 0.0 to 1.0
        """
        # Normalize field names
        f1 = field1.lower().replace("_", " ").replace("[", "").replace("]", "")
        f2 = field2.lower().replace("_", " ").replace("[", "").replace("]", "")

        # Extract words
        words1 = set(f1.split())
        words2 = set(f2.split())

        # Jaccard similarity
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0


class FieldValueTransformer:
    """Transform values from source to target field formats."""

    @staticmethod
    def transform_value(
        source_value: str,
        target_field_name: str,
        target_field_type: Optional[str] = None,
    ) -> str:
        """Transform a value to match target field requirements.

        Args:
            source_value: Value from source field
            target_field_name: Name of target field
            target_field_type: Type of target field (text, date, checkbox, etc.)

        Returns:
            Transformed value
        """
        if not source_value:
            return ""

        # Common transformations
        if target_field_type == "checkbox":
            return "On" if source_value.lower() in ["yes", "true", "1", "x"] else ""

        elif target_field_type == "date":
            return FieldValueTransformer._normalize_date(source_value)

        elif target_field_type == "phone":
            return FieldValueTransformer._normalize_phone(source_value)

        return source_value

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Normalize date formats.

        Args:
            date_str: Input date string

        Returns:
            Normalized date (YYYY-MM-DD format)
        """
        # Try common date formats
        patterns = [
            (r"(\d{4})-(\d{2})-(\d{2})", r"\1-\2-\3"),  # Already normalized
            (r"(\d{2})/(\d{2})/(\d{4})", r"\3-\1-\2"),  # MM/DD/YYYY
            (r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1"),  # DD.MM.YYYY
        ]

        for pattern, replacement in patterns:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)

        return date_str

    @staticmethod
    def _normalize_phone(phone_str: str) -> str:
        """Normalize phone number format.

        Args:
            phone_str: Input phone string

        Returns:
            Normalized phone number
        """
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone_str)
        return digits
