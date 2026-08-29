from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_uploaded_file(file: UploadFile) -> dict:
    if not file.filename:
        raise ValueError("Filename is missing")

    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(
            "Unsupported file type. Allowed: JPG, PNG, PDF"
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 10 MB limit")

    extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return {
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "path": str(file_path),
        "content_type": file.content_type,
        "size": len(content),
    }
