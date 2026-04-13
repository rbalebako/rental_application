"""Tests for field matcher."""

from rental_application.field_mapper import FieldMatcher, FieldValueTransformer
from unittest.mock import Mock


def test_similarity_score():
    """Test field name similarity scoring."""
    # Exact match
    assert FieldMatcher._similarity_score("first_name", "first_name") == 1.0

    # Partial match (both contain 'name')
    score = FieldMatcher._similarity_score("first_name", "full_name")
    assert score > 0.5  # Both have 'name' in common

    # Different fields
    score = FieldMatcher._similarity_score("first_name", "email_address")
    assert score < 0.5  # No common words


def test_normalize_date():
    """Test date normalization."""
    # YYYY-MM-DD (already normalized)
    assert FieldValueTransformer._normalize_date("2024-01-15") == "2024-01-15"

    # MM/DD/YYYY format
    assert FieldValueTransformer._normalize_date("01/15/2024") == "2024-01-15"

    # DD.MM.YYYY format
    assert FieldValueTransformer._normalize_date("15.01.2024") == "2024-01-15"


def test_normalize_phone():
    """Test phone number normalization."""
    # Remove non-digits
    assert FieldValueTransformer._normalize_phone("+41 79 123 45 67") == "41791234567"
    assert FieldValueTransformer._normalize_phone("(079) 123-45-67") == "0791234567"


def test_transform_checkbox():
    """Test checkbox value transformation."""
    assert FieldValueTransformer.transform_value("yes", "field", "checkbox") == "On"
    assert FieldValueTransformer.transform_value("true", "field", "checkbox") == "On"
    assert FieldValueTransformer.transform_value("no", "field", "checkbox") == ""
    assert FieldValueTransformer.transform_value("false", "field", "checkbox") == ""


def test_field_matcher_initialization():
    """Test FieldMatcher initialization."""
    mock_llm = Mock()
    matcher = FieldMatcher(llm_client=mock_llm, use_cache=False)

    assert matcher.llm_client == mock_llm
    assert matcher.use_cache is False
