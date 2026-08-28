import sys
import json
import cv2
import numpy as np

def detect_ai_generated(image_path):
    flags = []
    ai_score = 0

    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return {"aiScore": 0, "isAiGenerated": False, "flags": ["IMAGE_READ_ERROR"]}

        # 1. Spectral Analysis via FFT (Fast Fourier Transform)
        f = np.fft.fft2(image)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)

        h, w = image.shape
        center_h, center_w = h // 2, w // 2
        radius = min(h, w) // 8
        
        y, x = np.ogrid[:h, :w]
        mask = (x - center_w)**2 + (y - center_h)**2 > radius**2
        high_freq_power = np.mean(magnitude_spectrum[mask])

        # Flag spectral anomalies characteristic of AI generation
        if high_freq_power > 165 or high_freq_power < 70:
            ai_score += 45
            flags.append("SYNTHETIC_FREQUENCY_SPECTRUM_ANOMALY")

        # 2. Laplacian Variance / Texture Regularity Check
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        if laplacian_var < 30.0:
            ai_score += 35
            flags.append("UNNATURAL_SMOOTHNESS_NO_SENSOR_NOISE")

        is_ai = ai_score >= 40

        return {
            "aiScore": ai_score,
            "isAiGenerated": is_ai,
            "flags": flags
        }

    except Exception as e:
        return {"aiScore": 0, "isAiGenerated": False, "flags": [f"AI_DETECTOR_ERROR: {str(e)}"]}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"aiScore": 0, "isAiGenerated": False, "flags": ["NO_IMAGE_PROVIDED"]}))
        sys.exit(1)

    img_path = sys.argv[1]
    result = detect_ai_generated(img_path)
    print(json.dumps(result))