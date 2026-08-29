import os
import logging

from dotenv import load_dotenv
from fastapi import UploadFile

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

from utils.fallback_handler import get_ocr_fallback


load_dotenv()

logger = logging.getLogger(__name__)


AZURE_ENDPOINT = os.getenv(
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
)

AZURE_KEY = os.getenv(
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"
)


if not AZURE_ENDPOINT or not AZURE_KEY:
    raise RuntimeError(
        "Azure Document Intelligence credentials are not configured."
    )


client = DocumentIntelligenceClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)


MODEL_ID = "prebuilt-idDocument"


async def extract_text_from_document(
    file: UploadFile
):
    """
    Send an uploaded identity document to
    Azure Document Intelligence and return
    structured OCR information.

    If Azure OCR fails, fallback mock data
    is returned so that the rest of the
    pipeline can continue during development
    and integration testing.
    """

    # =================================================
    # BASIC INPUT VALIDATION
    # =================================================

    if not file:
        raise ValueError(
            "Document file is required."
        )

    if not file.filename:
        raise ValueError(
            "Document filename is missing."
        )

    # =================================================
    # READ UPLOADED FILE
    # =================================================

    file_bytes = await file.read()

    if not file_bytes:
        raise ValueError(
            "Uploaded document is empty."
        )

    logger.info(
        "Sending document to Azure OCR: %s",
        file.filename
    )

    # =================================================
    # AZURE OCR
    # =================================================

    try:

        poller = client.begin_analyze_document(
            MODEL_ID,
            analyze_request=file_bytes,
            content_type=file.content_type
        )

        # Wait for Azure processing to finish

        result = poller.result()

        logger.info(
            "Azure OCR completed: %s",
            file.filename
        )

    except Exception as exc:

        # ---------------------------------------------
        # AZURE FAILED
        # ---------------------------------------------

        logger.exception(
            "Azure OCR failed for %s",
            file.filename
        )

        fallback_result = get_ocr_fallback(
            reason=str(exc)
        )

        # Preserve original filename

        fallback_result["filename"] = (
            file.filename
        )

        return fallback_result

    # =================================================
    # EXTRACT STRUCTURED FIELDS
    # =================================================

    extracted_fields = {}

    if result.documents:

        document = result.documents[0]

        extracted_fields["document_type"] = {
            "value": document.doc_type,
            "confidence": 1.0
        }

        fields = document.fields or {}

        for field_name, field in fields.items():

            value = getattr(
                field,
                "value",
                None
            )

            if value is None:

                value = getattr(
                    field,
                    "content",
                    None
                )

            extracted_fields[field_name] = {
                "value": value,
                "confidence": field.confidence
            }

    # =================================================
    # RAW OCR TEXT
    # =================================================

    raw_text = result.content or ""

    # =================================================
    # RETURN AZURE RESULT
    # =================================================

    return {
        "provider": "azure-document-intelligence",
        "model": MODEL_ID,
        "filename": file.filename,
        "raw_text": raw_text,
        "fields": extracted_fields,
        "fallback": False
    }