import logging

from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["History"])
logger = logging.getLogger(__name__)


@router.get("/history")
async def get_history():
    logger.info("History requested")

    # Temporary response.
    # Person 5 can replace this with PostgreSQL/SQLAlchemy queries.

    return {
        "success": True,
        "message": "History retrieved successfully",
        "data": [],
    }
