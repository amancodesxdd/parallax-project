import logging
import pytesseract
import cv2
import numpy as np
import re
from fastapi import UploadFile

from utils.fallback_handler import get_ocr_fallback

logger = logging.getLogger(__name__)

# OPTIONAL (Windows): If Tesseract binary is not in your system PATH, set it explicitly:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def parse_passport_text(raw_text: str) -> dict:
    """
    Parses key passport fields (Document Number, DOB, Expiry, Nationality) 
    from raw Tesseract OCR text using regular expressions.
    """
    extracted_fields = {}

    # 1. Indian Passport Regex (2 uppercase letters + 7 digits)
    passport_match = re.search(r'[A-Z]{2}[0-9]{7}', raw_text)
    if passport_match:
        extracted_fields["DocumentNumber"] = {
            "value": passport_match.group(0),
            "confidence": 0.85
        }

    # 2. Date of Birth & Expiry Date patterns (DD/MM/YYYY or DD-MM-YYYY)
    dates = re.findall(r'\b\d{2}[/\.-]\d{2}[/\.-]\d{4}\b', raw_text)
    if len(dates) >= 1:
        extracted_fields["DateOfBirth"] = {"value": dates[0], "confidence": 0.80}
    if len(dates) >= 2:
        extracted_fields["DateOfExpiration"] = {"value": dates[1], "confidence": 0.80}

    # 3. Country / Nationality Check
    if "IND" in raw_text or "INDIA" in raw_text:
        extracted_fields["CountryRegion"] = {"value": "IND", "confidence": 0.90}

    return extracted_fields


async def extract_text_from_document(file: UploadFile) -> dict:
    """
    Processes an uploaded identity document using local Tesseract OCR.
    
    If local processing fails, fallback mock data is returned via get_ocr_fallback() 
    so downstream pipeline modules continue without crashing.
    """

    # =================================================
    # 1. BASIC INPUT VALIDATION
    # =================================================
    if not file:
        raise ValueError("Document file is required.")

    if not file.filename:
        raise ValueError("Document filename is missing.")

    # =================================================
    # 2. READ UPLOADED FILE BYTES
    # =================================================
    file_bytes = await file.read()

    if not file_bytes:
        raise ValueError("Uploaded document is empty.")

    logger.info("Sending document to Local Tesseract OCR: %s", file.filename)

    # =================================================
    # 3. TESSERACT OCR EXECUTION
    # =================================================
    try:
        # Decode image bytes into an OpenCV array
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image file format.")

        # Image Pre-processing for improved OCR accuracy
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Extract raw text
        raw_text = pytesseract.image_to_string(processed_img)

        # Parse fields into structured dictionary matching downstream schema
        extracted_fields = parse_passport_text(raw_text)

        logger.info("Local Tesseract OCR completed: %s", file.filename)

        return {
            "provider": "tesseract-ocr-local",
            "model": "tesseract-v5",
            "filename": file.filename,
            "raw_text": raw_text.strip(),
            "fields": extracted_fields,
            "fallback": False
        }

    except Exception as exc:
        # =================================================
        # 4. FALLBACK HANDLER ON FAILURE
        # =================================================
        logger.exception("Local Tesseract OCR failed for %s", file.filename)

        fallback_result = get_ocr_fallback(reason=str(exc))
        fallback_result["filename"] = file.filename

        return fallback_result