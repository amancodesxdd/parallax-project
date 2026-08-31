import logging
import os
import re

import cv2
import numpy as np
import pytesseract
from dotenv import load_dotenv
from fastapi import UploadFile

from utils.fallback_handler import get_ocr_fallback

logger = logging.getLogger(__name__)

# Load backend/.env (parent of parent of this file) so TESSERACT_CMD resolves
# regardless of the process working directory.
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_BACKEND_ROOT, ".env"))

_tesseract_cmd = os.environ.get("TESSERACT_CMD")
if _tesseract_cmd and os.path.exists(_tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd
else:
    logger.warning("TESSERACT_CMD not set or not found; relying on system PATH.")


def parse_passport_text(raw_text: str) -> dict:
    """Extracts structured passport fields from raw OCR text using regex patterns."""
    extracted_fields = {}

    # Indian Passport Format: 2 letters + 7 digits
    passport_match = re.search(r"[A-Z]{2}[0-9]{7}", raw_text)
    if passport_match:
        extracted_fields["DocumentNumber"] = {
            "value": passport_match.group(0),
            "confidence": 0.85,
        }

    # Extract dates (DD/MM/YYYY or DD-MM-YYYY)
    dates = re.findall(r"\b\d{2}[/\.-]\d{2}[/\.-]\d{4}\b", raw_text)
    if len(dates) >= 1:
        extracted_fields["DateOfBirth"] = {"value": dates[0], "confidence": 0.80}
    if len(dates) >= 2:
        extracted_fields["DateOfExpiration"] = {"value": dates[1], "confidence": 0.80}

    # Country / Nationality detection
    if "IND" in raw_text or "INDIA" in raw_text:
        extracted_fields["CountryRegion"] = {"value": "IND", "confidence": 0.90}

    return extracted_fields


async def extract_text_from_document(file: UploadFile) -> dict:
    """Runs local Tesseract OCR on an uploaded document file with fallback handling."""
    if not file or not file.filename:
        raise ValueError("Document file is required.")

    file_bytes = await file.read()
    if not file_bytes:
        raise ValueError("Uploaded document is empty.")

    logger.info("Executing Tesseract OCR for file: %s", file.filename)

    try:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image format.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        raw_text = pytesseract.image_to_string(processed_img)
        extracted_fields = parse_passport_text(raw_text)

        return {
            "provider": "tesseract-ocr-local",
            "model": "tesseract-v5",
            "filename": file.filename,
            "raw_text": raw_text.strip(),
            "fields": extracted_fields,
            "fallback": False,
        }

    except Exception as exc:
        logger.exception("Tesseract OCR execution failed for %s", file.filename)
        fallback_result = get_ocr_fallback(reason=str(exc))
        fallback_result["filename"] = file.filename
        return fallback_result