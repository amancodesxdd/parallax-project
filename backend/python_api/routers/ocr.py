import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ocr_services import extract_text_from_document
from services.request_validation import validate_document

from utils.response_formatter import (
    success_response,
    error_response,
)


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"],
)

logger = logging.getLogger(__name__)


@router.post("")
async def perform_ocr(
    document: UploadFile = File(...),
):
    """
    OCR API endpoint.

    Flow:

    Document
       ↓
    Request Validation
       ↓
    OCR Service
       ↓
    Standard Response
    """

    logger.info(
        "OCR request started: %s",
        document.filename,
    )

    try:

        # -----------------------------------------
        # TASK 6 — REQUEST VALIDATION
        # -----------------------------------------

        await validate_document(document)

        # -----------------------------------------
        # TASK 2 — OCR INTEGRATION
        # -----------------------------------------

        result = await extract_text_from_document(
            document
        )

        # -----------------------------------------
        # TASK 7 — RESPONSE FORMATTING
        # -----------------------------------------

        return success_response(
            message="OCR completed successfully",
            data=result,
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "OCR request failed"
        )

        return error_response(
            message="OCR processing failed",
            code="OCR_FAILED",
            status_code=500,
        )