"""Data models for rental application PDF processing."""

from enum import Enum
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field


class FieldType(str, Enum):
    """Supported PDF form field types."""

    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    DATE = "date"
    SIGNATURE = "signature"
    UNKNOWN = "unknown"


class FormField(BaseModel):
    """Represents a single form field."""

    name: str
    type: FieldType = FieldType.UNKNOWN
    value: Optional[str] = None
    required: bool = False
    options: Optional[List[str]] = None  # For dropdown/radio fields


class FormSchema(BaseModel):
    """Represents a complete form schema."""

    name: str = Field(..., description="Form identifier (e.g., 'SwissRentalApp2024')")
    fields: Dict[str, FormField] = Field(default_factory=dict)


class FieldMapping(BaseModel):
    """Represents a mapping between source and target field."""

    source_field: str
    target_field: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    value_transform: Optional[Callable] = None
    notes: Optional[str] = None


class FormFillingResult(BaseModel):
    """Result of a form filling operation."""

    success: bool
    filled_fields: int
    skipped_fields: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    output_path: Optional[str] = None
