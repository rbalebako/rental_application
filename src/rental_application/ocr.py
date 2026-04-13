"""OCR utilities for extracting text from scanned PDFs and images."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import easyocr


class OCRExtractor:
    """Extract text and field information from scanned documents using OCR."""

    def __init__(self, language: str = "de"):
        """Initialize OCR extractor.

        Args:
            language: Language code (de, en, fr, etc.)
        """
        self.language = language
        self.reader: Optional[easyocr.Reader] = None

    def _get_reader(self) -> easyocr.Reader:
        """Get or create EasyOCR reader (lazy loading).

        Returns:
            EasyOCR Reader instance
        """
        if self.reader is None:
            self.reader = easyocr.Reader([self.language], gpu=False)
        return self.reader

    def extract_text_from_image(self, image_path: str | Path) -> str:
        """Extract all text from an image.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        reader = self._get_reader()
        results = reader.readtext(str(image_path))

        # Combine all text results
        text_lines = [line[1] for line in results]
        return "\n".join(text_lines)

    def extract_text_from_pdf(self, pdf_path: str | Path) -> str:
        """Extract text from PDF pages using OCR (convert to images first).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text from all pages
        """
        import pdf2image

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Convert PDF pages to images
        try:
            images = pdf2image.convert_from_path(str(pdf_path))
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF to images: {e}")

        # Extract text from each page
        all_text = []
        for page_num, image in enumerate(images, 1):
            try:
                text = self.extract_text_from_image_object(image)
                all_text.append(f"--- Page {page_num} ---\n{text}")
            except Exception as e:
                print(f"Warning: Failed to OCR page {page_num}: {e}")
                all_text.append(f"--- Page {page_num} (failed) ---")

        return "\n".join(all_text)

    def extract_text_from_image_object(self, image) -> str:
        """Extract text from a PIL Image object.

        Args:
            image: PIL Image object

        Returns:
            Extracted text
        """
        import io
        import tempfile

        # Save image to temporary file and process
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            return self.extract_text_from_image(tmp.name)

    def extract_fields_from_text(self, text: str) -> Dict[str, str]:
        """Parse extracted text to identify form fields.

        Looks for patterns like "Field Name: value" or "Field Name" on one line
        and value on the next.

        Args:
            text: Extracted text from OCR

        Returns:
            Dictionary mapping field names to values
        """
        fields = {}
        lines = text.strip().split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Look for "Field: value" pattern
            if ":" in line:
                parts = line.split(":", 1)
                field_name = parts[0].strip()
                field_value = parts[1].strip() if len(parts) > 1 else ""

                # Filter out page markers and short labels
                if len(field_name) > 2 and not field_name.startswith("---"):
                    fields[field_name] = field_value

            # Look for checkbox/filled patterns
            elif line.lower() in ["☑", "✓", "x", "x", "[x]"]:
                # Previous line might be the field name
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    if prev_line and len(prev_line) > 2:
                        fields[prev_line] = "checked"

        return fields
