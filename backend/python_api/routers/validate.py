import logging

from fastapi import APIRouter, HTTPException

from utils.response_formatter import (
    success_response,
    error_response,
)


router = APIRouter(
    prefix="/api/validate",
    tags=["Validation"],
)

logger = logging.getLogger(__name__)


@router.post("")
async def validate_document(
    data: dict,
):
    """
    Document validation API.

    Person 4:
        API/interface

    Person 5:
        Actual validation/business logic
    """

    logger.info(
        "Document validation request started"
    )

    try:

        # -----------------------------------------
        # PERSON 5 INTEGRATION POINT
        # -----------------------------------------

        #
        # Later replace this section with
        # Person 5's validation service.
        #

        from services.validation_services import (
            validate_passport
        )

        # Convert incoming dictionary into
        # an object compatible with the
        # existing validation function.

        ocr_data = type(
            "OCRData",
            (),
            {
                "passport_number": data.get(
                    "passport_number",
                    ""
                ),

                "name": data.get(
                    "name",
                    ""
                ),

                "nationality": data.get(
                    "nationality",
                    ""
                ),

                "date_of_birth": data.get(
                    "date_of_birth",
                    ""
                ),

                "date_of_expiry": data.get(
                    "date_of_expiry",
                    ""
                ),

                "gender": data.get(
                    "gender",
                    ""
                ),
            },
        )()

        result = validate_passport(
            ocr_data
        )

        # -----------------------------------------
        # TASK 7 — RESPONSE FORMATTING
        # -----------------------------------------

        return success_response(
            message="Document validation completed",
            data=result,
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Document validation failed"
        )

        return error_response(
            message="Document validation failed",
            code="VALIDATION_FAILED",
            status_code=500,
        )