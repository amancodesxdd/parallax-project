import os
from typing import Optional

from fastapi import HTTPException, UploadFile


# =========================================================
# CONFIGURATION
# =========================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


ALLOWED_DOCUMENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}


# =========================================================
# BASIC FILE VALIDATION
# =========================================================

async def validate_file(
    file: Optional[UploadFile],
    allowed_types: set[str] | None = None,
    max_size: int = MAX_FILE_SIZE,
) -> None:
    """
    Validate an uploaded file.

    Checks:
        1. File exists
        2. Filename exists
        3. Content type is allowed
        4. File is not empty
        5. File size is within the limit

    Raises:
        HTTPException if validation fails.
    """

    # -----------------------------------------------------
    # 1. CHECK FILE EXISTS
    # -----------------------------------------------------

    if file is None:
        raise HTTPException(
            status_code=400,
            detail="File is required."
        )

    # -----------------------------------------------------
    # 2. CHECK FILENAME
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    # -----------------------------------------------------
    # 3. CHECK CONTENT TYPE
    # -----------------------------------------------------

    if allowed_types is None:
        allowed_types = ALLOWED_DOCUMENT_TYPES

    if file.content_type not in allowed_types:

        allowed_formats = ", ".join(
            sorted(allowed_types)
        )

        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file format. "
                f"Allowed formats: {allowed_formats}"
            )
        )

    # -----------------------------------------------------
    # 4. READ FILE
    # -----------------------------------------------------

    try:

        file_bytes = await file.read()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded file."
        ) from exc

    # -----------------------------------------------------
    # 5. CHECK EMPTY FILE
    # -----------------------------------------------------

    file_size = len(file_bytes)

    if file_size == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # -----------------------------------------------------
    # 6. CHECK FILE SIZE
    # -----------------------------------------------------

    if file_size > max_size:

        max_size_mb = max_size / (
            1024 * 1024
        )

        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large. "
                f"Maximum allowed size is "
                f"{max_size_mb:.0f} MB."
            )
        )

    # -----------------------------------------------------
    # 7. RESET FILE POINTER
    # -----------------------------------------------------

    await file.seek(0)


# =========================================================
# DOCUMENT VALIDATION
# =========================================================

async def validate_document(
    document: Optional[UploadFile],
) -> None:
    """
    Validate a document before OCR or scanning.

    Supported:
        JPG
        PNG
        WEBP
        PDF
    """

    await validate_file(
        file=document,
        allowed_types=ALLOWED_DOCUMENT_TYPES,
    )


# =========================================================
# IMAGE VALIDATION
# =========================================================

async def validate_image(
    image: Optional[UploadFile],
) -> None:
    """
    Validate an image file.

    Used for:
        - selfie
        - face verification
        - image-based document processing
    """

    await validate_file(
        file=image,
        allowed_types=ALLOWED_IMAGE_TYPES,
    )


# =========================================================
# MULTIPLE FILE VALIDATION
# =========================================================

async def validate_scan_request(
    document: Optional[UploadFile],
    selfie: Optional[UploadFile] = None,
) -> None:
    """
    Validate the complete /api/scan request.

    Document:
        Required

    Selfie:
        Optional

    Document:
        JPG / PNG / WEBP / PDF

    Selfie:
        JPG / PNG / WEBP
    """

    # -----------------------------------------------------
    # Validate document
    # -----------------------------------------------------

    await validate_document(document)

    # -----------------------------------------------------
    # Validate selfie if supplied
    # -----------------------------------------------------

    if selfie is not None:

        await validate_image(selfie)