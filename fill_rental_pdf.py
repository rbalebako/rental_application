"""
fill_rental_pdf.py – Fill Swiss rental application PDFs from a CSV file.

Reads applicant data from a CSV, optionally generates an AI-powered cover letter
introduction via a locally running Ollama instance, and writes one filled PDF per
applicant row to the output directory.

Usage:
    python fill_rental_pdf.py sample_applicants.csv rental_application_template.pdf
    python fill_rental_pdf.py sample_applicants.csv template.pdf --output-dir filled/
    python fill_rental_pdf.py sample_applicants.csv template.pdf --no-ai
    python fill_rental_pdf.py sample_applicants.csv template.pdf --ai-model llama3.2
"""

import argparse
import csv
import logging
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

try:
    import ollama as _ollama

    _OLLAMA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OLLAMA_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping: CSV column name → PDF AcroForm field name
# Extend this dict when your PDF template uses different field names.
# ---------------------------------------------------------------------------
CSV_TO_PDF_FIELD_MAP: dict[str, str] = {
    "last_name": "lastName",
    "first_name": "firstName",
    "date_of_birth": "dateOfBirth",
    "nationality": "nationality",
    "marital_status": "maritalStatus",
    "current_address": "currentAddress",
    "zip_code": "zipCode",
    "city": "city",
    "phone": "phone",
    "email": "email",
    "employer": "employer",
    "occupation": "occupation",
    "annual_income": "annualIncome",
    "num_persons": "numPersons",
    "has_pets": "hasPets",
    "move_in_date": "moveInDate",
    "num_cars": "numCars",
}


# ---------------------------------------------------------------------------
# CSV reading
# ---------------------------------------------------------------------------

def read_csv(csv_path: str) -> list[dict[str, str]]:
    """Read all rows from a CSV file and return them as a list of dicts."""
    path = Path(csv_path)
    if not path.is_file():
        logger.error("CSV file not found: %s", csv_path)
        sys.exit(1)

    applicants: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            applicants.append(dict(row))

    logger.info("Read %d applicant(s) from %s", len(applicants), csv_path)
    return applicants


# ---------------------------------------------------------------------------
# AI summary via local Ollama
# ---------------------------------------------------------------------------

def generate_ai_summary(applicant: dict[str, str], model: str = "llama3") -> str:
    """
    Use a locally running Ollama instance to produce a short, professional
    cover letter introduction for the applicant.

    Returns an empty string when Ollama is unavailable or returns an error.
    """
    if not _OLLAMA_AVAILABLE:
        logger.warning("ollama package is not installed – skipping AI summary.")
        return ""

    first = applicant.get("first_name", "")
    last = applicant.get("last_name", "")
    occupation = applicant.get("occupation", "")
    employer = applicant.get("employer", "")
    income = applicant.get("annual_income", "")
    persons = applicant.get("num_persons", "1")
    move_in = applicant.get("move_in_date", "")

    prompt = (
        "You are assisting with a Swiss rental application.\n"
        "Write a brief, professional cover letter introduction of 2–3 sentences "
        "for the following applicant. Use a formal, friendly tone suitable for a "
        "Swiss landlord. Reply with the introduction text only, no headings.\n\n"
        f"Name: {first} {last}\n"
        f"Occupation: {occupation}\n"
        f"Employer: {employer}\n"
        f"Annual income: {income} CHF\n"
        f"Number of persons moving in: {persons}\n"
        f"Desired move-in date: {move_in}\n"
    )

    try:
        response = _ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as exc:
        logger.warning("Ollama request failed (%s) – skipping AI summary.", exc)
        return ""


# ---------------------------------------------------------------------------
# PDF filling
# ---------------------------------------------------------------------------

def fill_pdf(
    template_path: str,
    output_path: str,
    field_values: dict[str, str],
) -> None:
    """
    Open *template_path*, fill all AcroForm fields present in *field_values*,
    and write the result to *output_path*.
    """
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    with open(output_path, "wb") as fh:
        writer.write(fh)

    logger.info("Filled PDF written to %s", output_path)


def _safe_filename(value: str) -> str:
    """Strip characters that are unsafe in file names."""
    return re.sub(r'[^\w-]', '_', value)


# ---------------------------------------------------------------------------
# Per-applicant processing
# ---------------------------------------------------------------------------

def process_applicant(
    applicant: dict[str, str],
    template_path: str,
    output_dir: str,
    use_ai: bool = True,
    ai_model: str = "llama3",
) -> None:
    """Generate (optionally) an AI summary and fill the PDF for one applicant."""
    first = _safe_filename(applicant.get("first_name", "unknown"))
    last = _safe_filename(applicant.get("last_name", "unknown"))
    output_path = os.path.join(output_dir, f"rental_application_{first}_{last}.pdf")

    # Build the dict of PDF field name → value from the CSV row
    field_values: dict[str, str] = {}
    for csv_col, pdf_field in CSV_TO_PDF_FIELD_MAP.items():
        value = applicant.get(csv_col, "")
        if value:
            field_values[pdf_field] = value

    # AI-generated cover letter introduction
    if use_ai:
        logger.info("Generating AI summary for %s %s …", first, last)
        summary = generate_ai_summary(applicant, model=ai_model)
        if summary:
            field_values["aiSummary"] = summary
            logger.info("AI summary added for %s %s.", first, last)

    fill_pdf(template_path, output_path, field_values)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fill Swiss rental application PDFs from a CSV file, "
            "with optional AI cover letter generation via local Ollama."
        )
    )
    parser.add_argument("csv_file", help="Path to the CSV file with applicant data")
    parser.add_argument("template_pdf", help="Path to the fillable PDF template")
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Directory for filled PDFs (default: output/)",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI cover letter generation",
    )
    parser.add_argument(
        "--ai-model",
        default="llama3",
        help="Ollama model name to use for AI generation (default: llama3)",
    )

    args = parser.parse_args()

    if not Path(args.template_pdf).is_file():
        logger.error("Template PDF not found: %s", args.template_pdf)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    applicants = read_csv(args.csv_file)
    for applicant in applicants:
        process_applicant(
            applicant,
            args.template_pdf,
            args.output_dir,
            use_ai=not args.no_ai,
            ai_model=args.ai_model,
        )

    logger.info("Done. %d application(s) written to '%s/'.", len(applicants), args.output_dir)


if __name__ == "__main__":
    main()
