import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ocr_services import (
    extract_text_from_document
)


router = APIRouter(
    prefix="/api",
    tags=["OCR"]
)


logger = logging.getLogger(__name__)


@router.post("/ocr")
async def perform_ocr(
    document: UploadFile = File(...)
):

    try:

        if not document.filename:
            raise HTTPException(
                status_code=400,
                detail="Document is required."
            )

        result = await extract_text_from_document(
            document
        )

        return {
            "success": True,
            "message": "OCR completed successfully",
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:

        logger.exception(
            "OCR processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail="OCR processing failed."
        )