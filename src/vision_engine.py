import cv2
import numpy as np
import os

def detect_text_regions(image_path):
    """
    Uses Image Processing to locate 'islands' of text.
    Acts as our YOLO-like localization engine.
    """
    # 1. Load image and convert to grayscale
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Binary Thresholding (makes text black and background white)
    # This helps in isolating the characters
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 8)

    # 3. Dilate the text to join nearby parts of a single character
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    # 4. Find Contours (the 'boxes' around pixel islands)
    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bboxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter out tiny noise (dots/specs) and huge boxes (the whole screen)
        if w > 5 and h > 5:
            bboxes.append([x, y, x + w, y + h])
            
    return bboxes

if __name__ == "__main__":
    print("--- Vision Engine (V2) Test ---")
    input_img = "debug_output/capture_test.png"
    
    if not os.path.exists(input_img):
        print(f"Error: {input_img} not found.")
    else:
        boxes = detect_text_regions(input_img)
        print(f"Detected {len(boxes)} potential text regions.")
        
        img = cv2.imread(input_img)
        for box in boxes:
            x1, y1, x2, y2 = box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        output_path = "debug_output/detection_test.png"
        cv2.imwrite(output_path, img)
        print(f"Verification image saved to: {output_path}")
    print("--- Test Finished ---")