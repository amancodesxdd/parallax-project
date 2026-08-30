import logging
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
@router.get("/")
async def get_scan_history(limit: int = Query(10, ge=1, le=100)):
    """Fetches recent passport screening logs for the dashboard history table."""
    # Placeholder return structured to match your frontend schema
    return {
        "success": True,
        "count": 0,
        "data": []
    }