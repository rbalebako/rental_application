# rental_application

A Python script that reads applicant attributes from a CSV file and fills them into a
fillable PDF rental application form.  An optional AI-powered cover letter introduction
is generated via a locally running [Ollama](https://ollama.com) instance.

## Requirements

- Python 3.10+
- [pypdf](https://pypdf.readthedocs.io/) – PDF reading and form-filling
- [reportlab](https://www.reportlab.com/) – template creation helper
- [ollama](https://github.com/ollama/ollama-python) – local Ollama AI client (optional)
- A locally running [Ollama](https://ollama.com) instance with a pulled model (e.g. `llama3`)

```bash
pip install -r requirements.txt
```

## Files

| File | Description |
|------|-------------|
| `fill_rental_pdf.py` | Main script – reads CSV and fills a PDF template |
| `create_sample_template.py` | Helper – creates a sample fillable PDF template |
| `sample_applicants.csv` | Example CSV with three Swiss rental applicants |
| `requirements.txt` | Python dependencies |

## Quick start

### 1 – Create a fillable PDF template

```bash
python create_sample_template.py rental_application_template.pdf
```

You can also supply your own fillable PDF.  The script maps the CSV columns below
to PDF AcroForm field names (see `CSV_TO_PDF_FIELD_MAP` in `fill_rental_pdf.py`).

### 2 – Prepare your CSV

The CSV must have a header row.  Supported columns:

| CSV column | PDF field | Example |
|------------|-----------|---------|
| `last_name` | `lastName` | Müller |
| `first_name` | `firstName` | Hans |
| `date_of_birth` | `dateOfBirth` | 01.01.1985 |
| `nationality` | `nationality` | Swiss |
| `marital_status` | `maritalStatus` | Single |
| `current_address` | `currentAddress` | Bahnhofstrasse 1 |
| `zip_code` | `zipCode` | 8001 |
| `city` | `city` | Zürich |
| `phone` | `phone` | +41 79 123 45 67 |
| `email` | `email` | hans@example.com |
| `employer` | `employer` | ABC AG |
| `occupation` | `occupation` | Software Engineer |
| `annual_income` | `annualIncome` | 95000 |
| `num_persons` | `numPersons` | 1 |
| `has_pets` | `hasPets` | No |
| `move_in_date` | `moveInDate` | 01.05.2025 |
| `num_cars` | `numCars` | 1 |

See `sample_applicants.csv` for a ready-to-use example.

### 3 – Fill the PDFs

```bash
# Fill PDFs with AI cover letter (requires Ollama running locally)
python fill_rental_pdf.py sample_applicants.csv rental_application_template.pdf

# Specify a custom output directory
python fill_rental_pdf.py sample_applicants.csv template.pdf --output-dir filled/

# Skip AI generation
python fill_rental_pdf.py sample_applicants.csv template.pdf --no-ai

# Use a different Ollama model
python fill_rental_pdf.py sample_applicants.csv template.pdf --ai-model llama3.2
```

One PDF per CSV row is written to the output directory (default: `output/`).

## AI integration (Ollama)

When Ollama is running locally (`ollama serve`) and a model has been pulled
(`ollama pull llama3`), the script sends the applicant's key details to the
model and writes the resulting 2–3 sentence professional introduction into the
`aiSummary` field of the PDF.

Pass `--no-ai` to skip this step entirely.
