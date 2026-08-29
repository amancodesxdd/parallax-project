import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.storage_service import save_uploaded_file


router = APIRouter(prefix="/api", tags=["Upload"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info("Upload request received: %s", file.filename)

    try:
        result = await save_uploaded_file(file)

        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        logger.exception("File upload failed")
        raise HTTPException(
            status_code=500,
            detail="File upload failed",
        )
