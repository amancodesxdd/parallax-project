import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.face_service import verify_face
from services.request_validation import validate_image

from utils.response_formatter import (
    success_response,
    error_response,
)


router = APIRouter(
    prefix="/api/face",
    tags=["Face"],
)

logger = logging.getLogger(__name__)


@router.post("")
async def verify_document_face(
    document: UploadFile = File(...),
    selfie: UploadFile = File(...),
):
    """
    Face verification API.

    Flow:

    Document + Selfie
          ↓
    Request Validation
          ↓
    Face Verification Service
          ↓
    Standard Response
    """

    logger.info(
        "Face verification request started"
    )

    try:

        # -----------------------------------------
        # TASK 6 — REQUEST VALIDATION
        # -----------------------------------------

        await validate_image(document)
        await validate_image(selfie)

        # -----------------------------------------
        # TASK 3 — FACE VERIFICATION
        # -----------------------------------------

        result = await verify_face(
            document,
            selfie,
        )

        # -----------------------------------------
        # TASK 7 — RESPONSE FORMATTING
        # -----------------------------------------

        return success_response(
            message="Face verification completed",
            data=result,
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Face verification failed"
        )

        return error_response(
            message="Face verification failed",
            code="FACE_VERIFICATION_FAILED",
            status_code=500,
        )