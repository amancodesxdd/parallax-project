import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from utils.response_formatter import (
    success_response,
    error_response,
)


router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)

logger = logging.getLogger(__name__)


@router.get("")
async def get_history(
    date: Optional[str] = Query(
        default=None
    ),
    status: Optional[str] = Query(
        default=None
    ),
    risk: Optional[float] = Query(
        default=None
    ),
):
    """
    Retrieve scan history.

    Filters:
        date
        status
        risk

    Database implementation will be
    connected by Person 5.
    """

    logger.info(
        "History request received"
    )

    try:

        # -----------------------------------------
        # PERSON 5 INTEGRATION POINT
        # -----------------------------------------

        #
        # Replace this placeholder with the
        # actual database service from Person 5.
        #

        result = {
            "items": [],
            "filters": {
                "date": date,
                "status": status,
                "risk": risk,
            },
        }

        # -----------------------------------------
        # TASK 7 — RESPONSE FORMATTING
        # -----------------------------------------

        return success_response(
            message="Scan history retrieved successfully",
            data=result,
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "History request failed"
        )

        return error_response(
            message="Unable to retrieve scan history",
            code="HISTORY_FETCH_FAILED",
            status_code=500,
        )