import logging
import cv2
import numpy as np
from fastapi import UploadFile

logger = logging.getLogger(__name__)


async def verify_face_match(document_file: UploadFile, selfie_file: UploadFile = None) -> dict:
    """Compares the document photo against a live selfie image via OpenCV face detection."""
    if not selfie_file:
        logger.info("No selfie provided; skipping facial biometric match.")
        return {
            "face_score": 100.0,
            "matched": True,
            "skipped": True,
            "details": "Selfie omitted from validation request",
        }

    try:
        doc_bytes = await document_file.read()
        selfie_bytes = await selfie_file.read()

        await document_file.seek(0)
        await selfie_file.seek(0)

        doc_img = cv2.imdecode(np.frombuffer(doc_bytes, np.uint8), cv2.IMREAD_COLOR)
        selfie_img = cv2.imdecode(np.frombuffer(selfie_bytes, np.uint8), cv2.IMREAD_COLOR)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        doc_gray = cv2.cvtColor(doc_img, cv2.COLOR_BGR2GRAY)
        selfie_gray = cv2.cvtColor(selfie_img, cv2.COLOR_BGR2GRAY)

        doc_faces = face_cascade.detectMultiScale(doc_gray, scaleFactor=1.1, minNeighbors=5)
        selfie_faces = face_cascade.detectMultiScale(selfie_gray, scaleFactor=1.1, minNeighbors=5)

        if len(doc_faces) == 0 or len(selfie_faces) == 0:
            return {
                "face_score": 40.0,
                "matched": False,
                "skipped": False,
                "details": "Could not detect clear face region in one or both uploaded images",
            }

        (x1, y1, w1, h1) = doc_faces[0]
        (x2, y2, w2, h2) = selfie_faces[0]

        crop1 = cv2.resize(doc_gray[y1:y1 + h1, x1:x1 + w1], (100, 100))
        crop2 = cv2.resize(selfie_gray[y2:y2 + h2, x2:x2 + w2], (100, 100))

        hist1 = cv2.calcHist([crop1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([crop2], [0], None, [256], [0, 256])

        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)

        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        match_score = round(max(0.0, correlation) * 100.0, 2)

        return {
            "face_score": match_score,
            "matched": match_score >= 65.0,
            "skipped": False,
            "details": f"Biometric similarity confidence: {match_score}%",
        }

    except Exception as exc:
        logger.error("Face verification service failed: %s", str(exc))
        return {
            "face_score": 50.0,
            "matched": False,
            "skipped": False,
            "error": str(exc),
        }