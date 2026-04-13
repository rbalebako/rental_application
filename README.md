# Rental Application PDF Filler

Automate filling out Swiss rental application PDFs using intelligent field matching and local LLMs.

## Overview

This library automatically fills out rental application PDFs by:

1. **Extracting data** from an already-filled source PDF
2. **Matching fields** intelligently using a local LLM (Ollama)
3. **Filling** the target PDF with mapped and transformed values

Perfect for reusing information across multiple rental applications without manual data re-entry.

## Features

- ✅ **Fillable PDF forms** - Extracts and fills PDF form fields
- ✅ **Scanned PDFs/Images** - Automatic OCR fallback for scanned documents
- ✅ **Intelligent field matching** - Uses local LLMs to semantically match form fields
- ✅ **Smart value transformation** - Handles different date/phone/checkbox formats
- ✅ **Mapping cache** - Reuse mappings for similar form types
- ✅ **Type-safe** - Built with Pydantic for robust data validation
- ✅ **Provider agnostic** - Simple LLM client for local models (Ollama) or custom implementations
- ✅ **Modular design** - Use individual components independently

## Quick Start

### Prerequisites

- Python 3.10+
- Ollama running locally (or compatible LLM service)

### Installation

```bash
# Clone and install
git clone https://github.com/yourusername/rental_application.git
cd rental_application
poetry install

# Or with pip
pip install -r requirements.txt
```

### Setup Ollama

```bash
# Install Ollama (https://ollama.ai)
ollama serve

# In another terminal, pull a model
ollama pull mistral  # or neural-chat, llama2, etc.
```

### Basic Usage

```python
from rental_application import RentalApplicationFiller, LocalLLMClient

# Create LLM client
llm = LocalLLMClient(model="mistral")

# Initialize filler
filler = RentalApplicationFiller(
    source_pdf="old_application.pdf",
    target_pdf="new_application.pdf",
    llm_client=llm
)

# Validate setup
errors = filler.validate()
if errors:
    print("Errors:", errors)
    exit(1)

# Fill the PDF
result = filler.auto_fill(output_path="filled_application.pdf")

if result.success:
    print(f"✓ Filled {result.filled_fields} fields")
    print(f"Output: {result.output_path}")
```

## Architecture

### Core Components

```
rental_application/
├── models.py           # Pydantic data models
├── config.py           # Configuration management
├── pdf_handler.py      # PDF extraction & filling
├── llm_client.py       # LLM abstraction (Ollama, etc.)
├── field_mapper.py     # Field matching & transformation
├── filler.py           # Main orchestrator
└── utils/
    ├── prompts.py      # LLM prompt templates
    └── cache.py        # Mapping cache utilities
```

### Data Flow

```
Source PDF → PDFExtractor → Form Fields
                                ↓
          PDFExtractor ← ← ← FieldMatcher (uses LLM)
                                ↓
          PDFFiller ← ← ← Field Mapping
                                ↓
Target PDF ← PDFFiller ← Value Transformation
                                ↓
Output PDF (Filled)
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `models.py` | Type definitions for forms, fields, mappings |
| `config.py` | Settings (LLM host, thresholds, paths) |
| `pdf_handler.py` | Read/write PDFs, extract form fields |
| `llm_client.py` | LLM abstraction for Ollama/local models |
| `field_mapper.py` | Match fields semantically, transform values |
| `filler.py` | Orchestrate the entire process |
| `prompts.py` | LLM prompts for field matching |
| `cache.py` | Save/load mappings for reuse |

## Usage Examples

### Complete Example with Caching

```python
from rental_application import RentalApplicationFiller, LocalLLMClient

# Use custom Ollama host
llm = LocalLLMClient(host="192.168.1.100:11434", model="neural-chat")

filler = RentalApplicationFiller(
    source_pdf="2024_application.pdf",
    target_pdf="2025_application.pdf",
    llm_client=llm
)

# Fill and cache mapping
result = filler.auto_fill("filled_2025.pdf")

# Save mapping for reuse
filler.save_mapping_for_reuse("swiss_rental_2024_to_2025")

# Later, for similar forms:
filler2 = RentalApplicationFiller(
    source_pdf="2024_application.pdf",
    target_pdf="another_2025_form.pdf",
    llm_client=llm
)
filler2.load_mapping_from_cache("swiss_rental_2024_to_2025")
result2 = filler2.auto_fill("filled_another_2025.pdf")
```

### Using Components Independently

```python
from rental_application import PDFExtractor, PDFFiller

# Just extract fields
extractor = PDFExtractor("form.pdf")
fields = extractor.extract_form_fields()
text = extractor.extract_text()

# Just fill a form
filler = PDFFiller("template.pdf")
filler.fill_form(
    {"field1": "value1", "field2": "value2"},
    output_path="filled.pdf"
)

# Get field mapping recommendations
from rental_application import FieldMatcher, LocalLLMClient
matcher = FieldMatcher(LocalLLMClient())
mapping = matcher.match_fields(source_fields, target_fields)
```

## Configuration

Set via environment variables or `.env` file:

```bash
# LLM settings
RENTAL_APP_OLLAMA_HOST=localhost:11434
RENTAL_APP_OLLAMA_MODEL=mistral
RENTAL_APP_TIMEOUT_SECONDS=30

# Thresholds
RENTAL_APP_CONFIDENCE_THRESHOLD=0.7

# Features
RENTAL_APP_VERBOSE=true
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=rental_application

# Run specific test
poetry run pytest tests/test_field_mapper.py::test_similarity_score
```

## Troubleshooting

### "Ollama not available at localhost:11434"

- Ensure Ollama is running: `ollama serve`
- Check custom host if needed: `LocalLLMClient(host="your-host:port")`

### LLM responses not in expected format

- Switch to different model: `LocalLLMClient(model="neural-chat")`
- Lower temperature for more deterministic output
- Check LLM context length isn't exceeded

### Fields not mapping

- Check confidence threshold: `config.confidence_threshold = 0.5`
- Review LLM prompt templates in `utils/prompts.py`
- Use fallback heuristic matching (happens automatically)

## Performance Notes

- **First run**: ~30-60s (LLM generates mappings)
- **Cached mappings**: <1s (loads from cache)
- **Memory**: ~200-500MB with LLM running
- **PDF size**: Supports PDFs up to 100MB

## Supported PDF Form Types

- Text fields ✅
- Checkboxes ✅
- Radio buttons ✅
- Dropdown/Select ✅
- Date fields ✅
- Signature fields (extracted as text) ✅
- **Scanned PDFs/Images (OCR)** ✅ NEW!

## OCR Support (Scanned Documents)

If your PDF is a scanned image or doesn't have fillable form fields, the system automatically falls back to **OCR extraction**:

1. Converts PDF pages to images
2. Extracts text using EasyOCR (supports 80+ languages including German)
3. Identifies field names and values from extracted text
4. Continues with normal field matching and filling

**No configuration needed** - OCR is automatic if fillable fields aren't found.

### OCR Performance

- **First run:** ~30-60s (downloads language model on first use)
- **Subsequent runs:** ~10-30s per page
- **Accuracy:** ~90-95% for printed forms, varies for handwritten text

### OCR Configuration

OCR language defaults to German (`de`). Customize via environment variable:

```bash
RENTAL_APP_LANGUAGE=en  # English
RENTAL_APP_LANGUAGE=fr  # French
RENTAL_APP_LANGUAGE=de  # German (default)
```

## Limitations

- Handwritten form entries may have lower OCR accuracy
- Very small or blurry text in scanned PDFs may not extract clearly
- Complex form layouts may need manual field adjustment
- Swiss-specific form knowledge improvements welcome
- Complex conditional fields not yet supported

## Contributing

Contributions welcome! Areas for improvement:

- Better Swiss rental form recognition
- OCR support for scanned forms
- More LLM provider integrations
- Performance optimizations
- Test coverage expansion

## License

Apache License 2.0 - See LICENSE file
