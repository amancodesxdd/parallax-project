from fastapi import APIRouter, HTTPException

from schemas.common import ValidateRequest
from services.validation_services import validate_passport


router = APIRouter(prefix="/api", tags=["Validation"])


@router.post("/validate")
async def validate_document(data: ValidateRequest):
    try:
        result = validate_passport(data)

        return {
            "success": True,
            "message": "Document validation completed",
            "data": result,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document validation failed",
        )
