import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from services.face_service import verify_face_match

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify")
async def match_faces(
    document: UploadFile = File(...),
    selfie: UploadFile = File(...)
):
    """Compares the face region of the passport against an uploaded selfie image."""
    try:
        result = await verify_face_match(document_file=document, selfie_file=selfie)
        return {
            "success": True,
            "message": "Face match verification executed",
            "data": result
        }
    except Exception as exc:
        logger.exception("Face verification router error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "FACE_VERIFICATION_FAILED", "message": str(exc)}
        )