"""Tests for models."""

from rental_application.models import FieldType, FormField, FormSchema


def test_form_field_creation():
    """Test FormField creation."""
    field = FormField(
        name="full_name",
        type=FieldType.TEXT,
        value="John Doe",
        required=True,
    )
    assert field.name == "full_name"
    assert field.type == FieldType.TEXT
    assert field.value == "John Doe"
    assert field.required is True


def test_form_schema_creation():
    """Test FormSchema creation."""
    field1 = FormField(name="name", type=FieldType.TEXT)
    field2 = FormField(name="accept", type=FieldType.CHECKBOX)

    schema = FormSchema(
        name="test_form",
        fields={
            "name": field1,
            "accept": field2,
        },
    )
    assert schema.name == "test_form"
    assert len(schema.fields) == 2
    assert "name" in schema.fields


def test_field_type_enum():
    """Test FieldType enum."""
    assert FieldType.TEXT.value == "text"
    assert FieldType.CHECKBOX.value == "checkbox"
    assert FieldType.DATE.value == "date"
