import logging
import os
import threading

import cv2
import numpy as np
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# ONNX model for the YuNet DNN face detector (bundled in python_api/models/).
# Note: this build of opencv 5.x does not expose the legacy
# cv2.CascadeClassifier binding, so we use cv2.FaceDetectorYN instead.
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "face_detection_yunet_2023mar.onnx",
)

_detector = None
_detector_lock = threading.Lock()
_DETECTOR_MIN_SCORE = 0.7


def _get_detector():
    """Lazily instantiate a shared YuNet face detector (thread-safe)."""
    global _detector
    if _detector is not None:
        return _detector

    with _detector_lock:
        if _detector is None:
            if not os.path.exists(_MODEL_PATH):
                raise RuntimeError(
                    f"Face detection model not found at {_MODEL_PATH}. "
                    "Re-download face_detection_yunet_2023mar.onnx into python_api/models/"
                )
            _detector = cv2.FaceDetectorYN.create(
                _MODEL_PATH,
                "",
                (0, 0),
                score_threshold=_DETECTOR_MIN_SCORE,
                nms_threshold=0.3,
                top_k=5000,
            )
    return _detector


def _detect_faces(img_bgr):
    """Returns a list of (x, y, w, h) bounding boxes for the top-scoring faces."""
    detector = _get_detector()

    h, w = img_bgr.shape[:2]
    detector.setInputSize((w, h))

    _, faces = detector.detect(img_bgr)
    if faces is None or len(faces) == 0:
        return []

    # Sort by detection score (last column) descending
    ordered = sorted(faces, key=lambda f: float(f[14]), reverse=True)
    return [(int(box[0]), int(box[1]), int(box[2]), int(box[3])) for box in ordered]


async def verify_face_match(document_file: UploadFile, selfie_file: UploadFile = None) -> dict:
    """Compares the document photo against a live selfie image via YuNet face detection."""
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

        if doc_img is None or selfie_img is None:
            return {
                "face_score": 40.0,
                "matched": False,
                "skipped": False,
                "details": "Could not decode one or both uploaded images",
            }

        doc_faces = _detect_faces(doc_img)
        selfie_faces = _detect_faces(selfie_img)

        if len(doc_faces) == 0 or len(selfie_faces) == 0:
            return {
                "face_score": 40.0,
                "matched": False,
                "skipped": False,
                "details": "Could not detect clear face region in one or both uploaded images",
            }

        (x1, y1, w1, h1) = doc_faces[0]
        (x2, y2, w2, h2) = selfie_faces[0]

        crop1 = cv2.resize(doc_img[y1:y1 + h1, x1:x1 + w1], (100, 100))
        crop2 = cv2.resize(selfie_img[y2:y2 + h2, x2:x2 + w2], (100, 100))

        # Multi-channel histogram correlation (BGR) for a more robust match than grayscale alone.
        correlations = []
        for channel in range(3):
            hist1 = cv2.calcHist([crop1], [channel], None, [256], [0, 256])
            hist2 = cv2.calcHist([crop2], [channel], None, [256], [0, 256])

            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)

            correlations.append(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))

        match_score = round(max(0.0, sum(correlations) / len(correlations)) * 100.0, 2)

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