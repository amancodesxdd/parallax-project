import os
import logging

from dotenv import load_dotenv
from fastapi import UploadFile

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient


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

    This function belongs to Person 4's
    OCR integration layer.

    Person 5 can consume the returned data
    for validation/database/risk processing.
    """

    if not file:
        raise ValueError("Document file is required.")

    if not file.filename:
        raise ValueError("Document filename is missing.")

    # Read uploaded file
    file_bytes = await file.read()

    if not file_bytes:
        raise ValueError("Uploaded document is empty.")

    logger.info(
        "Sending document to Azure OCR: %s",
        file.filename
    )

    # Send document to Azure Document Intelligence
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

    # ------------------------------------------------
    # Extract structured fields
    # ------------------------------------------------

    extracted_fields = {}

    if result.documents:

        document = result.documents[0]

        extracted_fields["document_type"] = (
            document.doc_type
        )

        fields = document.fields or {}

        for field_name, field in fields.items():

            value = getattr(field, "value", None)

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

    # ------------------------------------------------
    # Raw OCR text
    # ------------------------------------------------

    raw_text = result.content or ""

    # ------------------------------------------------
    # Return standardized response
    # ------------------------------------------------

    return {
        "provider": "azure-document-intelligence",
        "model": MODEL_ID,
        "filename": file.filename,
        "raw_text": raw_text,
        "fields": extracted_fields
    }