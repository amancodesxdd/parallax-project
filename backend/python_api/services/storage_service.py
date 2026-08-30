import logging
import os
import uuid
from fastapi import UploadFile

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_file_locally(file: UploadFile) -> str:
    """Saves incoming upload file stream to local disk storage."""
    try:
        ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        filename = f"{uuid.uuid4().hex}.{ext}"
        target_path = os.path.join(UPLOAD_DIR, filename)

        file_bytes = await file.read()
        await file.seek(0)

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        logger.info("Saved local document to: %s", target_path)
        return target_path

    except Exception as exc:
        logger.error("Failed writing document to storage: %s", str(exc))
        raise RuntimeError(f"Storage service failure: {str(exc)}")