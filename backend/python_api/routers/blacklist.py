from fastapi import APIRouter

from schemas.common import BlacklistRequest


router = APIRouter(prefix="/api", tags=["Blacklist"])


@router.get("/blacklist")
async def get_blacklist():
    return {
        "success": True,
        "message": "Blacklist retrieved successfully",
        "data": [],
    }


@router.post("/blacklist")
async def add_blacklist(data: BlacklistRequest):
    return {
        "success": True,
        "message": "Blacklist entry added",
        "data": {
            "document_number": data.document_number,
            "reason": data.reason,
        },
    }


@router.delete("/blacklist/{document_number}")
async def remove_blacklist(document_number: str):
    return {
        "success": True,
        "message": "Blacklist entry removed",
        "data": {
            "document_number": document_number,
        },
    }
