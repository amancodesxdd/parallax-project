import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def validate_document_input(file: UploadFile) -> dict:
    """Validates uploaded document file extension, non-empty payload, and size limit."""
    if not file or not file.filename:
        raise ValueError("Missing file parameter in upload request.")

    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    file_bytes = await file.read()
    await file.seek(0)

    if len(file_bytes) == 0:
        raise ValueError("Uploaded file is empty (0 bytes).")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds 10MB limit ({len(file_bytes) / (1024 * 1024):.2f}MB).")

    return {
        "valid": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(file_bytes),
    }