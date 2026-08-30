import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from services.orchestration_service import run_full_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
@router.post("/")
async def scan_document(
    document: UploadFile = File(...),
    selfie: UploadFile = File(None),
):
    """
    Main Screening Endpoint: Orchestrates OCR, database validation, 
    forensics checks, face matching, and risk scoring.
    """
    try:
        result = await run_full_pipeline(document_file=document, selfie_file=selfie)
        return {
            "success": True,
            "message": "Document screening completed successfully",
            "data": result
        }
    except ValueError as val_err:
        logger.warning(f"Validation error during scan: {str(val_err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_INPUT", "message": str(val_err)}
        )
    except Exception as exc:
        logger.exception("Error executing full document scan pipeline")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "SCAN_FAILED", "message": str(exc)}
        )