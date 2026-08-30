import logging
from fastapi import UploadFile

from services.request_validation import validate_document_input
from services.storage_service import save_file_locally
from services.ocr_services import extract_text_from_document
from services.validation_services import validate_passport_fields
from services.face_service import verify_face_match

logger = logging.getLogger(__name__)


async def run_full_pipeline(document_file: UploadFile, selfie_file: UploadFile = None) -> dict:
    """
    Executes core 4-module pipeline:
    Input Validation -> Storage -> Tesseract OCR -> Rules Engine -> Face Verification -> Risk Scoring.
    """
    logger.info("Executing screening pipeline for: %s", document_file.filename)

    # Module 0: Input Validation & Persistence
    await validate_document_input(document_file)
    saved_path = await save_file_locally(document_file)

    # Module 1: OCR Extraction
    ocr_result = await extract_text_from_document(document_file)

    # Module 2: Rule Validation
    val_result = validate_passport_fields(ocr_result.get("fields", {}))

    # Module 3 & 4: Face Verification & Composite Risk Scoring
    face_result = await verify_face_match(document_file, selfie_file)

    val_score = val_result["validation_score"]
    face_score = face_result["face_score"]
    tamper_score = 100  # Default clean baseline score

    # Risk Formula = 100 - (Val 40% + Tamper 40% + Face 20%)
    composite_risk = round(100 - (val_score * 0.40 + tamper_score * 0.40 + face_score * 0.20), 2)

    # Tri-Tier Verdict Logic
    if composite_risk <= 30:
        verdict = "APPROVE"
    elif composite_risk <= 60:
        verdict = "REVIEW"
    else:
        verdict = "REJECT"

    return {
        "verdict": verdict,
        "risk_score": composite_risk,
        "file_path": saved_path,
        "ocr_data": ocr_result,
        "validation_results": val_result,
        "face_match_results": face_result,
    }