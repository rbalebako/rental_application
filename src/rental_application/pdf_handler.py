"""PDF extraction and filling utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Any

import pdfplumber
from pypdf import PdfReader, PdfWriter

from rental_application.config import config


class PDFExtractor:
    """Extract data from PDF forms."""

    def __init__(self, pdf_path: str | Path):
        """Initialize extractor with a PDF file.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        self._ocr_mode = False
        self._ocr_text = ""

    def extract_form_fields(self) -> Dict[str, str]:
        """Extract all form field names and values from the PDF.

        Falls back to OCR if no form fields are found.

        Returns:
            Dictionary mapping field names to their values
        """
        # Try standard form field extraction first
        try:
            reader = PdfReader(self.pdf_path)
            fields = reader.get_fields()

            if fields:
                result = {}
                for field_name, field_data in fields.items():
                    value = field_data.get("/V", "")
                    # Handle different value types
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="ignore")
                    result[field_name] = str(value) if value else ""

                if config.verbose:
                    print(f"✓ Extracted {len(result)} form fields from fillable PDF")

                return result
        except Exception as e:
            if config.verbose:
                print(f"Warning: Failed to extract form fields: {e}")

        # Fallback to OCR if no form fields found
        if config.verbose:
            print("No form fields found. Attempting OCR extraction...")

        try:
            from rental_application.ocr import OCRExtractor

            ocr = OCRExtractor(language=config.language)
            text = ocr.extract_text_from_pdf(self.pdf_path)
            fields = ocr.extract_fields_from_text(text)

            if fields:
                if config.verbose:
                    print(f"✓ Extracted {len(fields)} fields using OCR")
                self._ocr_mode = True
                self._ocr_text = text
                return fields

            # If OCR didn't find fields, return raw text as a single field
            if text:
                if config.verbose:
                    print("Warning: No structured fields found via OCR, using raw text")
                return {"_document_text": text}

        except ImportError:
            if config.verbose:
                print(
                    "Warning: OCR not available. Install with: "
                    "pip install easyocr pdf2image"
                )
        except Exception as e:
            if config.verbose:
                print(f"Warning: OCR extraction failed: {e}")

        return {}

    def extract_text(self) -> str:
        """Extract all text from the PDF.

        Returns:
            Concatenated text from all pages
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
                return "\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}") from e

    def get_metadata(self) -> Dict[str, Any]:
        """Get PDF metadata.

        Returns:
            Dictionary with PDF metadata
        """
        try:
            reader = PdfReader(self.pdf_path)
            metadata = reader.metadata or {}
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "num_pages": len(reader.pages),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get PDF metadata: {e}") from e

    def list_form_fields(self) -> List[str]:
        """List all available form field names.

        Returns:
            List of field names
        """
        reader = PdfReader(self.pdf_path)
        fields = reader.get_fields()
        return list(fields.keys()) if fields else []


class PDFFiller:
    """Fill PDF form fields."""

    def __init__(self, pdf_path: str | Path):
        """Initialize filler with a PDF template.

        Args:
            pdf_path: Path to the PDF template file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def fill_form(
        self,
        field_mapping: Dict[str, str],
        output_path: str | Path,
    ) -> None:
        """Fill form fields with provided values.

        Args:
            field_mapping: Dictionary mapping field names to values
            output_path: Path where filled PDF should be saved
        """
        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()

            # Copy all pages to writer
            for page in reader.pages:
                writer.add_page(page)

            # Update form fields
            writer.update_page_form_field_values(writer.pages[0], field_mapping)

            # Write output
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "wb") as f:
                writer.write(f)

        except Exception as e:
            raise RuntimeError(f"Failed to fill PDF form: {e}") from e

    def validate_fields(self) -> List[str]:
        """Validate and list available form fields in the template.

        Returns:
            List of available field names
        """
        reader = PdfReader(self.pdf_path)
        fields = reader.get_fields()
        return list(fields.keys()) if fields else []
