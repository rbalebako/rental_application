"""LLM prompt templates for field matching and extraction."""

from typing import Dict, List


def field_matching_prompt(
    source_fields: List[str], target_fields: List[str]
) -> str:
    """Generate prompt for matching source fields to target fields.

    Args:
        source_fields: List of source form field names
        target_fields: List of target form field names

    Returns:
        Formatted prompt string
    """
    return f"""You are an expert in matching form fields between different PDF forms, including forms in German and other languages.

Given a source form and a target form, map each target field to the most appropriate source field.

SOURCE FORM FIELDS:
{chr(10).join(f"- {f}" for f in source_fields)}

TARGET FORM FIELDS:
{chr(10).join(f"- {f}" for f in target_fields)}

For each target field, provide:
1. The matching source field (or "NONE" if no match exists)
2. A confidence score (0.0 to 1.0)
3. Brief explanation of the match

Format your response as JSON:
{{
  "mappings": [
    {{
      "target_field": "field_name",
      "source_field": "matching_field",
      "confidence": 0.95,
      "reason": "Both fields capture..."
    }}
  ]
}}

Be precise and only match fields when you're confident they represent the same information."""


def field_extraction_prompt(
    source_value: str, target_field_name: str, context: str = ""
) -> str:
    """Generate prompt for extracting/transforming field values.

    Args:
        source_value: The value from the source field
        target_field_name: Name of the target field
        context: Additional context about the transformation

    Returns:
        Formatted prompt string
    """
    return f"""You are helping fill out a rental application form.

SOURCE VALUE: {source_value}
TARGET FIELD: {target_field_name}
{f"CONTEXT: {context}" if context else ""}

Based on the source value and target field name, provide the appropriate value to fill in the target field.

Consider:
- Format conversions (e.g., dates, phone numbers)
- Field-specific requirements
- Data cleaning and normalization

Respond with just the value to fill in, no explanation needed.
If the value cannot be meaningfully transformed or doesn't apply, respond with "N/A"."""


def form_field_extraction_prompt(
    form_text: str, num_expected_fields: int = 10
) -> str:
    """Generate prompt for extracting form field information from PDF text.

    Args:
        form_text: Extracted text from the PDF
        num_expected_fields: Expected number of fields to find

    Returns:
        Formatted prompt string
    """
    return f"""Analyze the following rental application form text and identify all form fields.

FORM TEXT:
{form_text[:2000]}  # Limit to first 2000 chars

For each field, identify:
1. Field name/label
2. Field type (text, checkbox, date, etc.)
3. Current value (if filled)
4. Whether it appears required

Expected approximately {num_expected_fields} fields.

Respond in JSON format:
{{
  "fields": [
    {{
      "name": "field_name",
      "type": "text",
      "value": "current_value",
      "required": true
    }}
  ]
}}"""
