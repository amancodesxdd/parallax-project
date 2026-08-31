"""
Unified forensic pipeline for the Node gateway.

Single subprocess invocation returning OCR fields, AI-generation detection,
tampering detection, and (optional) face matching as one JSON payload.

Usage:
    python forensics_pipeline.py --document <image_path> [--selfie <image_path>]
"""

import argparse
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
MODEL_PATH = os.path.join(BASE_DIR, "python_api", "models", "face_detection_yunet_2023mar.onnx")

PASSPORT_RE = re.compile(r"[A-Z]{2}[0-9]{7}")
DATE_RE = re.compile(r"\b\d{2}[/\.-]\d{2}[/\.-]\d{4}\b")


def load_env():
    """Load backend/.env so TESSERACT_CMD etc. resolve regardless of cwd."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH, override=False)
    except ImportError:
        pass


def parse_passport_text(raw_text):
    """Extracts structured passport fields from raw OCR text via regex."""
    fields = {}
    m = PASSPORT_RE.search(raw_text)
    if m:
        fields["DocumentNumber"] = {"value": m.group(0)}
    dates = DATE_RE.findall(raw_text)
    if len(dates) >= 1:
        fields["DateOfBirth"] = {"value": dates[0]}
    if len(dates) >= 2:
        fields["DateOfExpiration"] = {"value": dates[1]}
    if "IND" in raw_text or "INDIA" in raw_text:
        fields["CountryRegion"] = {"value": "IND"}
    return fields


def run_ocr(image_path):
    """Tesseract OCR with graceful fallback when tesseract/pytesseract is unavailable."""
    try:
        import cv2
        import numpy as np
        import pytesseract

        cmd = os.environ.get("TESSERACT_CMD")
        if cmd and os.path.exists(cmd):
            pytesseract.pytesseract.tesseract_cmd = cmd

        img = cv2.imread(image_path)
        if img is None:
            return {"ok": False, "raw_text": "", "fields": {}, "error": "IMAGE_DECODE_FAILED"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        raw_text = pytesseract.image_to_string(processed)

        return {
            "ok": True,
            "raw_text": raw_text.strip(),
            "fields": parse_passport_text(raw_text),
        }
    except Exception as exc:
        return {"ok": False, "raw_text": "", "fields": {}, "error": str(exc)}


def run_ai_detection(image_path):
    """FFT spectral + texture regularity analysis for AI-generated imagery."""
    try:
        import cv2
        import numpy as np

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return {"aiScore": 0, "isAiGenerated": False, "flags": ["IMAGE_READ_ERROR"]}

        ai_score = 0
        flags = []

        f = np.fft.fft2(image)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)

        h, w = image.shape
        center_h, center_w = h // 2, w // 2
        radius = min(h, w) // 8

        y, x = np.ogrid[:h, :w]
        mask = (x - center_w) ** 2 + (y - center_h) ** 2 > radius ** 2
        high_freq_power = np.mean(magnitude_spectrum[mask])

        if high_freq_power > 165 or high_freq_power < 70:
            ai_score += 45
            flags.append("SYNTHETIC_FREQUENCY_SPECTRUM_ANOMALY")

        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        if laplacian_var < 30.0:
            ai_score += 35
            flags.append("UNNATURAL_SMOOTHNESS_NO_SENSOR_NOISE")

        return {
            "aiScore": ai_score,
            "isAiGenerated": ai_score >= 40,
            "flags": flags,
        }
    except Exception as exc:
        return {"aiScore": 0, "isAiGenerated": False, "flags": [f"AI_DETECTOR_ERROR: {str(exc)}"]}


def run_tamper_detection(image_path):
    """Edge-discontinuity + blur/smoothing analysis for tampered documents."""
    try:
        import cv2

        if not os.path.exists(image_path):
            return {"tamperScore": 0, "isTampered": False, "flags": ["FILE_NOT_FOUND"]}

        img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img_gray is None:
            return {"tamperScore": 0, "isTampered": False, "flags": ["INVALID_IMAGE_FILE"]}

        tamper_score = 0
        flags = []

        edges = cv2.Canny(img_gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 50 and h > 50 and (w * h) > 2500:
                tamper_score += 40
                flags.append("HIGH_EDGE_DISCONTINUITY_POSSIBLE_PHOTO_CUT")
                break

        laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
        if laplacian_var < 50.0:
            tamper_score += 30
            flags.append("BLURRY_TEXT_OR_UNNATURAL_SMOOTHING")

        return {
            "tamperScore": tamper_score,
            "isTampered": tamper_score >= 30,
            "flags": flags,
        }
    except Exception as exc:
        return {"tamperScore": 0, "isTampered": False, "flags": [f"TAMPER_DETECTOR_ERROR: {str(exc)}"]}


def run_face_match(doc_path, selfie_path):
    """YuNet DNN face detection + multi-channel histogram comparison."""
    if not selfie_path:
        return {
            "face_score": 100.0,
            "matched": True,
            "skipped": True,
            "details": "Selfie omitted from validation request",
        }
    try:
        import cv2
        import numpy as np

        if not os.path.exists(MODEL_PATH):
            return {"face_score": 50.0, "matched": False, "skipped": False, "error": "FACE_MODEL_MISSING"}

        doc_img = cv2.imread(doc_path)
        selfie_img = cv2.imread(selfie_path)
        if doc_img is None or selfie_img is None:
            return {"face_score": 40.0, "matched": False, "skipped": False, "details": "Could not decode one or both images"}

        detector = cv2.FaceDetectorYN.create(
            MODEL_PATH, "", (0, 0),
            score_threshold=0.7, nms_threshold=0.3, top_k=5000,
        )

        def detect_boxes(img):
            h, w = img.shape[:2]
            detector.setInputSize((w, h))
            _, faces = detector.detect(img)
            if faces is None or len(faces) == 0:
                return []
            ordered = sorted(faces, key=lambda f: float(f[14]), reverse=True)
            return [(int(b[0]), int(b[1]), int(b[2]), int(b[3])) for b in ordered]

        doc_faces = detect_boxes(doc_img)
        selfie_faces = detect_boxes(selfie_img)

        if len(doc_faces) == 0 or len(selfie_faces) == 0:
            return {"face_score": 40.0, "matched": False, "skipped": False, "details": "Could not detect clear face region in one or both images"}

        (x1, y1, w1, h1) = doc_faces[0]
        (x2, y2, w2, h2) = selfie_faces[0]

        crop1 = cv2.resize(doc_img[y1:y1 + h1, x1:x1 + w1], (100, 100))
        crop2 = cv2.resize(selfie_img[y2:y2 + h2, x2:x2 + w2], (100, 100))

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
        return {"face_score": 50.0, "matched": False, "skipped": False, "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Passport forensic pipeline")
    parser.add_argument("--document", required=True, help="Path to document image")
    parser.add_argument("--selfie", default=None, help="Optional path to selfie image")
    args = parser.parse_args()

    load_env()

    result = {
        "document": args.document,
        "ocr": run_ocr(args.document),
        "ai": run_ai_detection(args.document),
        "tamper": run_tamper_detection(args.document),
        "face": run_face_match(args.document, args.selfie),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)