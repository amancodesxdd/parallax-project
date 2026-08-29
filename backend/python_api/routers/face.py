import logging

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile
)

from services.face_service import (
    verify_face
)


router = APIRouter(
    prefix="/api",
    tags=["Face Verification"]
)

logger = logging.getLogger(__name__)


@router.post("/face")
async def face_verification(
    document: UploadFile = File(...),
    selfie: UploadFile = File(...)
):

    try:

        if not document.filename:
            raise HTTPException(
                status_code=400,
                detail="Document image is required."
            )

        if not selfie.filename:
            raise HTTPException(
                status_code=400,
                detail="Selfie image is required."
            )

        result = await verify_face(
            document,
            selfie
        )

        return {
            "success": True,
            "message": (
                "Face verification completed"
            ),
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        logger.exception(
            "Face verification failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Face verification failed."
        ) from exc