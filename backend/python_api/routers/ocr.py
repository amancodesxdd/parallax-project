import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from services.ocr_services import extract_text_from_document

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/extract")
async def extract_ocr(file: UploadFile = File(...)):
    """Runs local Tesseract OCR on a document image and returns extracted fields."""
    try:
        ocr_result = await extract_text_from_document(file)
        return {
            "success": True,
            "message": "OCR text extraction completed",
            "data": ocr_result
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_REQUEST", "message": str(val_err)}
        )
    except Exception as exc:
        logger.exception("OCR router extraction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "OCR_FAILED", "message": str(exc)}
        )