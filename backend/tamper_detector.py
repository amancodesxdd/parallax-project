import sys
import json
import cv2
import numpy as np

def analyze_document(image_path):
    flags = []
    tamper_score = 0
    
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {
            "tamperScore": 100, 
            "isTampered": True, 
            "flags": ["INVALID_OR_MISSING_IMAGE_FILE"]
        }

    # 1. Edge Discontinuity Check (Detects photo replacement or copy-paste borders)
    edges = cv2.Canny(img, 100, 200)
    edge_density = np.sum(edges > 0) / float(img.size)
    
    if edge_density > 0.15:
        tamper_score += 40
        flags.append("HIGH_EDGE_DISCONTINUITY_POSSIBLE_PHOTO_CUT")

    # 2. Text Smoothing/Blur Check (Detects Photoshop erase/smoothing tools)
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 50:
        tamper_score += 30
        flags.append("BLURRY_TEXT_OR_UNNATURAL_SMOOTHING")

    final_score = min(tamper_score, 100)
    return {
        "tamperScore": final_score,
        "isTampered": final_score > 30,
        "flags": flags
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        result = analyze_document(image_path)
        print(json.dumps(result))
    else:
        print(json.dumps({"tamperScore": 0, "isTampered": False, "flags": ["NO_IMAGE_PROVIDED"]}))