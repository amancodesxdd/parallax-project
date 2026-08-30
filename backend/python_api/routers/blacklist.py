import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# In-Memory Blacklist Fallback for testing/offline mode
MOCK_BLACKLIST = {"J1234567", "A9876543", "Z1111111"}


class BlacklistCheckRequest(BaseModel):
    document_number: str


@router.post("/check")
async def check_blacklist(payload: BlacklistCheckRequest):
    """Checks if a passport number exists in the watch/blacklist database."""
    doc_num = payload.document_number.strip().upper()
    is_blacklisted = doc_num in MOCK_BLACKLIST

    return {
        "success": True,
        "document_number": doc_num,
        "is_blacklisted": is_blacklisted,
        "reason": "Flagged on Interpol/SSB Watchlist" if is_blacklisted else None
    }