import logging
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.face_service import verify_face
from services.ocr_services import extract_text_from_document
from services.validation_services import validate_passport


router = APIRouter(prefix="/api", tags=["Scan"])
logger = logging.getLogger(__name__)


@router.post("/scan")
async def scan_document(
    document: UploadFile = File(...),
    selfie: UploadFile | None = File(None),
):
    scan_id = str(uuid4())

    logger.info("Scan started: %s", scan_id)

    try:
        if not document.filename:
            raise HTTPException(
                status_code=400,
                detail="Document is required",
            )

        # 1. OCR
        ocr_result = await extract_text_from_document(document)

        # 2. Face verification, if selfie is supplied
        face_result = None
        if selfie is not None:
            face_result = await verify_face(document, selfie)

        # 3. Validation interface for Person 5
        validation_result = validate_passport(
            type(
                "OCRData",
                (),
                {
                    "passport_number": ocr_result.get("passport_number", ""),
                    "name": ocr_result.get("name", ""),
                    "nationality": ocr_result.get("nationality", ""),
                    "date_of_birth": ocr_result.get("date_of_birth", ""),
                    "date_of_expiry": ocr_result.get("date_of_expiry", ""),
                },
            )()
        )

        # 4. Compile response
        result = {
            "scan_id": scan_id,
            "ocr": ocr_result,
            "face": face_result,
            "validation": validation_result,
        }

        logger.info("Scan completed: %s", scan_id)

        return {
            "success": True,
            "message": "Document scan completed",
            "data": result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Scan failed: %s", scan_id)
        raise HTTPException(
            status_code=500,
            detail="Document scanning failed",
        )
