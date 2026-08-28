import cv2
import json
import sys
import os

def detect_and_highlight_tampering(image_path):
    tamper_score = 0
    flags = []
    
    if not os.path.exists(image_path):
        return {"tamperScore": 0, "isTampered": False, "flags": ["FILE_NOT_FOUND"], "highlightedImagePath": None}

    # Load image in grayscale for processing and color for drawing highlights
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_color = cv2.imread(image_path)

    if img_gray is None:
        return {"tamperScore": 0, "isTampered": False, "flags": ["INVALID_IMAGE_FILE"], "highlightedImagePath": None}

    # 1. Edge Discontinuity (Photo cut/paste detection)
    edges = cv2.Canny(img_gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    suspicious_box_found = False
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter for sharp box-like cuts typical of photo replacement
        if w > 50 and h > 50 and (w * h) > 2500:
            cv2.rectangle(img_color, (x, y), (x + w, y + h), (0, 0, 255), 3) # Draw Red Box
            cv2.putText(img_color, "SUSPICIOUS EDGE CUT", (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            suspicious_box_found = True

    if suspicious_box_found:
        tamper_score += 40
        flags.append("HIGH_EDGE_DISCONTINUITY_POSSIBLE_PHOTO_CUT")

    # 2. Text Erase / Blur Detection
    laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
    if laplacian_var < 50.0:
        tamper_score += 30
        flags.append("BLURRY_TEXT_OR_UNNATURAL_SMOOTHING")
        # Overlay warning banner across top
        cv2.putText(img_color, "WARNING: UNNATURAL SMOOTHING/BLUR DETECTED", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Save output highlighted image
    output_path = image_path.replace(".jpg", "_highlighted.jpg").replace(".png", "_highlighted.png")
    cv2.imwrite(output_path, img_color)

    return {
        "tamperScore": tamper_score,
        "isTampered": tamper_score >= 30,
        "flags": flags,
        "highlightedImagePath": output_path if tamper_score >= 30 else None
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    result = detect_and_highlight_tampering(sys.argv[1])
    print(json.dumps(result))