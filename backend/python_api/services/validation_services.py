import logging
import re

logger = logging.getLogger(__name__)


def validate_passport_fields(extracted_fields: dict) -> dict:
    """Applies country-specific regex format rules to extracted passport metadata."""
    errors = []
    warnings = []

    doc_num = extracted_fields.get("DocumentNumber", {}).get("value")
    nationality = extracted_fields.get("CountryRegion", {}).get("value")

    if doc_num:
        if not re.match(r"^[A-Z]{2}[0-9]{7}$", str(doc_num)):
            errors.append(f"Format Violation: Document '{doc_num}' fails Indian regex (2 Letters + 7 Digits).")
    else:
        errors.append("Passport Document Number is missing or unreadable.")

    if not nationality:
        warnings.append("Country/Nationality metadata missing from document.")

    val_score = max(0, 100 - (len(errors) * 40 + len(warnings) * 10))

    return {
        "is_valid": len(errors) == 0,
        "validation_score": val_score,
        "errors": errors,
        "warnings": warnings,
    }