from pydantic import BaseModel


class FaceVerificationResult(BaseModel):

    provider: str

    matched: bool

    face_score: float

    confidence: float

    message: str

    unmatched_faces: int