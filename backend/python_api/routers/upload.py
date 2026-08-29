import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from services.storage_service import upload_file


router = APIRouter(
    prefix="/api",
    tags=["Upload"]
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}


# ---------------------------------------------------------
# UPLOAD ENDPOINT
# ---------------------------------------------------------

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # 1. CHECK FILE
    # -----------------------------------------------------

    if not file:

        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )


    # -----------------------------------------------------
    # 2. CHECK CONTENT TYPE
    # -----------------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed formats: JPG, PNG, WEBP and PDF."
            )
        )


    # -----------------------------------------------------
    # 3. READ FILE
    # -----------------------------------------------------

    try:

        file_bytes = await file.read()

    except Exception as error:

        logger.exception(
            "Unable to read uploaded file: %s",
            error
        )

        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded file."
        )


    # -----------------------------------------------------
    # 4. CHECK FILE SIZE
    # -----------------------------------------------------

    file_size = len(file_bytes)

    if file_size == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )


    if file_size > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "File is too large. "
                "Maximum allowed size is 10 MB."
            )
        )


    # -----------------------------------------------------
    # 5. UPLOAD TO STORAGE
    # -----------------------------------------------------

    try:

        storage_result = upload_file(
            file_bytes=file_bytes,
            original_filename=file.filename,
            content_type=file.content_type,
        )

    except RuntimeError as error:

        logger.exception(
            "Storage error: %s",
            error
        )

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:

        logger.exception(
            "Unexpected upload error: %s",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="File upload failed."
        )


    # -----------------------------------------------------
    # 6. STANDARD RESPONSE
    # -----------------------------------------------------

    return {
        "success": True,
        "message": "File uploaded successfully.",

        "filename": file.filename,

        "content_type": file.content_type,

        "size": file_size,

        "storage": storage_result["storage"],

        "storage_key": storage_result["key"],

        "stored_filename": storage_result["filename"],

        "file_url": storage_result["url"],
    }