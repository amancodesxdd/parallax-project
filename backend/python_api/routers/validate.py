import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from services.validation_services import validate_passport_fields

logger = logging.getLogger(__name__)
router = APIRouter()


class ValidationRequest(BaseModel):
    fields: dict


@router.post("/check")
async def validate_fields(payload: ValidationRequest):
    """Executes structural validation rules against extracted JSON metadata."""
    try:
        results = validate_passport_fields(payload.fields)
        return {
            "success": True,
            "message": "Field validation rules executed",
            "data": results
        }
    except Exception as exc:
        logger.exception("Validation router error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "VALIDATION_FAILED", "message": str(exc)}
        )