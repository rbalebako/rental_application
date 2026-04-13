"""Rental application PDF filler library."""

from .config import Config, config
from .field_mapper import FieldMatcher, FieldValueTransformer
from .filler import RentalApplicationFiller
from .llm_client import LocalLLMClient, LLMClient
from .models import FieldMapping, FieldType, FormField, FormFillingResult, FormSchema
from .pdf_handler import PDFExtractor, PDFFiller

# Import OCR optionally (may not be available)
try:
    from .ocr import OCRExtractor
except ImportError:
    OCRExtractor = None

__version__ = "0.1.0"

__all__ = [
    "Config",
    "config",
    "FieldMapping",
    "FieldMatcher",
    "FieldType",
    "FieldValueTransformer",
    "FormField",
    "FormFillingResult",
    "FormSchema",
    "LocalLLMClient",
    "LLMClient",
    "OCRExtractor",
    "PDFExtractor",
    "PDFFiller",
    "RentalApplicationFiller",
]
