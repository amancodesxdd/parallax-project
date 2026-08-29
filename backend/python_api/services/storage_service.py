import os
import uuid
import logging
from io import BytesIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# AWS CONFIGURATION
# ---------------------------------------------------------

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

# Used to switch between S3 and local/demo storage.
STORAGE_MODE = os.getenv("STORAGE_MODE", "s3").lower()


# ---------------------------------------------------------
# S3 CLIENT
# ---------------------------------------------------------

s3_client = None

if (
    AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY
    and AWS_S3_BUCKET
):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


# ---------------------------------------------------------
# UPLOAD TO S3
# ---------------------------------------------------------

def upload_to_s3(
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
) -> dict:

    if s3_client is None:
        raise RuntimeError(
            "AWS S3 is not configured. "
            "Check AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY "
            "and AWS_S3_BUCKET in .env"
        )

    # Generate a unique filename so two users
    # cannot accidentally overwrite each other's files.
    extension = os.path.splitext(original_filename)[1].lower()

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    s3_key = f"uploads/{unique_filename}"

    try:

        s3_client.upload_fileobj(
            BytesIO(file_bytes),
            AWS_S3_BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": content_type
            },
        )

        # S3 object URL
        file_url = (
            f"https://{AWS_S3_BUCKET}.s3."
            f"{AWS_REGION}.amazonaws.com/{s3_key}"
        )

        logger.info(
            "File uploaded successfully: %s",
            s3_key
        )

        return {
            "storage": "s3",
            "key": s3_key,
            "filename": unique_filename,
            "url": file_url,
        }

    except (BotoCoreError, ClientError) as error:

        logger.exception(
            "S3 upload failed: %s",
            error
        )

        raise RuntimeError(
            "Cloud storage upload failed."
        )


# ---------------------------------------------------------
# LOCAL FALLBACK
# ---------------------------------------------------------

def save_locally(
    file_bytes: bytes,
    original_filename: str,
) -> dict:

    upload_directory = "uploads"

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        upload_directory,
        unique_filename
    )

    with open(file_path, "wb") as file:

        file.write(file_bytes)

    logger.info(
        "File saved locally: %s",
        file_path
    )

    return {
        "storage": "local",
        "key": file_path,
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}",
    }


# ---------------------------------------------------------
# MAIN STORAGE FUNCTION
# ---------------------------------------------------------

def upload_file(
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
) -> dict:

    if STORAGE_MODE == "local":

        return save_locally(
            file_bytes,
            original_filename
        )

    return upload_to_s3(
        file_bytes,
        original_filename,
        content_type
    )