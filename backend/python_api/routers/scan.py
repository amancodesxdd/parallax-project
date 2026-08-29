import logging
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.orchestration_service import run_scan_pipeline


router = APIRouter(
    prefix="/api/scan",
    tags=["Scan"]
)

logger = logging.getLogger(__name__)


@router.post("")
async def scan_document(
    document: UploadFile = File(...),
    selfie: UploadFile | None = File(None),
):
    """
    Main document scanning endpoint.

    The actual processing is handled by
    orchestration_service.py.

    Pipeline:

    Document
       ↓
    OCR
       ↓
    Person 5 processing
       ↓
    Face verification
       ↓
    Combined response
    """

    scan_id = str(uuid4())

    logger.info("Scan started: %s", scan_id)

    try:

        # -----------------------------------------
        # Basic document validation
        # -----------------------------------------

        if not document.filename:
            raise HTTPException(
                status_code=400,
                detail="Document is required"
            )

        # -----------------------------------------
        # Run complete orchestration pipeline
        # -----------------------------------------

        result = await run_scan_pipeline(
            document=document,
            selfie=selfie
        )

        # Add scan ID to the final response

        result["scan_id"] = scan_id

        logger.info(
            "Scan completed successfully: %s",
            scan_id
        )

        return result

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Scan failed: %s",
            scan_id
        )

        raise HTTPException(
            status_code=500,
            detail="Document scanning failed"
        )