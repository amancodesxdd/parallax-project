import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from services.request_validation import validate_document_input
from services.storage_service import save_file_locally

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/file")
async def upload_document(file: UploadFile = File(...)):
    """Validates and stores an uploaded file into local storage."""
    try:
        await validate_document_input(file)
        saved_path = await save_file_locally(file)

        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "filename": file.filename,
                "saved_path": saved_path
            }
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_UPLOAD", "message": str(val_err)}
        )
    except Exception as exc:
        logger.exception("Upload router error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "UPLOAD_FAILED", "message": str(exc)}
        )