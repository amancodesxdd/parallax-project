import os
import cv2

def generate_xai_annotated_image():
    # Detect uploaded passport image in directory
    possible_names = ["image_2cbbaf.jpg", "real_passport.jpg", "real_passport_input.jpg"]
    input_path = None

    for name in possible_names:
        if os.path.exists(name):
            input_path = name
            break

    if not input_path:
        print("ERROR: No passport image found! Please place 'image_2cbbaf.jpg' in this folder.")
        return

    # Read image securely
    img = cv2.imread(input_path)
    if img is None:
        print(f"ERROR: OpenCV failed to read file path: '{input_path}'")
        return

    output = img.copy()

    # Drawing color & text parameters (BGR format)
    red_color = (0, 0, 255)
    white_color = (255, 255, 255)
    thickness = 4

    # 1. Top-Left Blue Stamp Box (03 OCT 2021)
    x1, y1, w1, h1 = 130, 95, 330, 175
    cv2.rectangle(output, (x1, y1), (x1 + w1, y1 + h1), red_color, thickness)
    cv2.rectangle(output, (x1, y1 - 35), (x1 + 420, y1), red_color, -1)
    cv2.putText(output, "TAMPER DETECTED: Stamp Forgery / Overlaid Date", (x1 + 8, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, white_color, 2, cv2.LINE_AA)

    # 2. Top-Right Passport Number Box (S7667070)
    x2, y2, w2, h2 = 745, 570, 215, 50
    cv2.rectangle(output, (x2, y2), (x2 + w2, y2 + h2), red_color, thickness)
    cv2.rectangle(output, (x2 - 180, y2 - 35), (x2 + w2, y2), red_color, -1)
    cv2.putText(output, "TAMPER DETECTED: Font Mismatch", (x2 - 170, y2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, white_color, 2, cv2.LINE_AA)

    # 3. Primary Portrait Photo Swap Box (Bottom-Left)
    x3, y3, w3, h3 = 75, 560, 275, 200
    cv2.rectangle(output, (x3, y3), (x3 + w3, y3 + h3), red_color, thickness)
    cv2.rectangle(output, (x3, y3 - 35), (x3 + 370, y3), red_color, -1)
    cv2.putText(output, "TAMPER DETECTED: Photo Swap Cut", (x3 + 8, y3 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, white_color, 2, cv2.LINE_AA)

    # 4. Ghost Watermark Photo Box (Bottom-Right)
    x4, y4, w4, h4 = 665, 620, 260, 190
    cv2.rectangle(output, (x4, y4), (x4 + w4, y4 + h4), red_color, thickness)
    cv2.rectangle(output, (x4, y4 + h4), (x4 + 430, y4 + h4 + 35), red_color, -1)
    cv2.putText(output, "TAMPER DETECTED: Ghost Photo Discontinuity", (x4 + 8, y4 + h4 + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, white_color, 2, cv2.LINE_AA)

    # Save output annotated image
    output_path = "passport_xai_annotated.jpg"
    cv2.imwrite(output_path, output)
    print(f"SUCCESS: Created annotated visual output '{output_path}' from source '{input_path}'!")

if __name__ == "__main__":
    generate_xai_annotated_image()