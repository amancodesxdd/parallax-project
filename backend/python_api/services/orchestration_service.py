import logging
from typing import Any, Dict, Optional

from services.ocr_services import extract_text_from_document


logger = logging.getLogger(__name__)


async def run_scan_pipeline(
    document,
    selfie=None,
    document_type: Optional[str] = None
) -> Dict[str, Any]:

    logger.info("Starting scan pipeline")

    try:

        # ==========================================
        # STEP 1 — OCR
        # ==========================================

        logger.info("Running OCR")

        ocr_result = await extract_text_from_document(
            document
        )

        logger.info("OCR completed")

        # ==========================================
        # STEP 2 — Person 5 processing
        # ==========================================

        person5_result = await process_with_person5(
            ocr_result=ocr_result,
            document_type=document_type
        )

        # ==========================================
        # STEP 3 — Face verification
        # ==========================================

        face_result = None

        if selfie is not None:

            try:

                # Import here to avoid unnecessary
                # circular imports

                from services.face_service import verify_face

                # Reset files before using them again

                await document.seek(0)
                await selfie.seek(0)

                logger.info(
                    "Running face verification"
                )

                face_result = await verify_face(
                    document,
                    selfie
                )

            except Exception as exc:

                logger.warning(
                    "Face verification failed: %s",
                    exc
                )

                face_result = {
                    "success": False,
                    "matched": False,
                    "face_score": 0.0,
                    "confidence": 0.0,
                    "message": "Face verification unavailable"
                }

        # ==========================================
        # STEP 4 — Compile everything
        # ==========================================

        final_result = compile_scan_result(
            ocr_result=ocr_result,
            person5_result=person5_result,
            face_result=face_result
        )

        logger.info(
            "Scan pipeline completed"
        )

        return {
            "success": True,
            "message": "Document scan completed",
            "data": final_result
        }

    except Exception as exc:

        logger.exception(
            "Scan pipeline failed"
        )

        return {
            "success": False,
            "message": "Scan pipeline failed",
            "error": str(exc)
        }


async def process_with_person5(
    ocr_result: Dict[str, Any],
    document_type: Optional[str] = None
) -> Dict[str, Any]:

    """
    Integration point for Person 5.

    Person 5 can later connect:

    - validation
    - database
    - blacklist
    - tampering detection
    - risk scoring
    - verdict
    - history
    """

    logger.info(
        "Sending OCR result to Person 5"
    )

    return {
        "success": True,

        "document_type": document_type,

        "extracted_data": ocr_result,

        "validation_results": {},

        "tampering_flags": [],

        "risk_score": None,

        "verdict": None,

        "processed_by": "person5-placeholder"
    }


def compile_scan_result(
    ocr_result: Dict[str, Any],
    person5_result: Dict[str, Any],
    face_result: Optional[Dict[str, Any]]
) -> Dict[str, Any]:

    return {

        "ocr": ocr_result,

        "validation": person5_result.get(
            "validation_results",
            {}
        ),

        "tampering": person5_result.get(
            "tampering_flags",
            []
        ),

        "face": face_result,

        "risk": {
            "score": person5_result.get(
                "risk_score"
            ),

            "verdict": person5_result.get(
                "verdict"
            )
        }
    }