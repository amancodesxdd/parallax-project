import logging

from fastapi import APIRouter, HTTPException

from utils.response_formatter import (
    success_response,
    error_response,
)


router = APIRouter(
    prefix="/api/blacklist",
    tags=["Blacklist"],
)

logger = logging.getLogger(__name__)


@router.get("/{document_number}")
async def check_blacklist(
    document_number: str,
):
    """
    Check whether a document/passport number
    exists in the blacklist.

    Person 5 will provide the actual
    database implementation.
    """

    logger.info(
        "Blacklist check requested"
    )

    try:

        # -----------------------------------------
        # BASIC INPUT CHECK
        # -----------------------------------------

        if not document_number.strip():

            raise HTTPException(
                status_code=400,
                detail="Document number is required",
            )

        # -----------------------------------------
        # PERSON 5 INTEGRATION POINT
        # -----------------------------------------

        #
        # Replace this placeholder with the
        # actual Person 5 blacklist service.
        #

        result = {
            "document_number": document_number,
            "blacklisted": False,
            "reason": None,
        }

        # -----------------------------------------
        # TASK 7 — RESPONSE FORMATTING
        # -----------------------------------------

        return success_response(
            message="Blacklist check completed",
            data=result,
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Blacklist check failed"
        )

        return error_response(
            message="Blacklist check failed",
            code="BLACKLIST_CHECK_FAILED",
            status_code=500,
        )