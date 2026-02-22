import cv2
import easyocr
import numpy as np
import os

# Initialize the EasyOCR Reader
# This will download the CRAFT detection model on first run (~100MB)
# We include 'ja' and 'en' to help the model recognize both scripts
reader = easyocr.Reader(['ja', 'en'], gpu=False, model_storage_directory='models', download_enabled=True)  # Set gpu=True if you have a compatible GPU and want faster processing

def get_text_bboxes(image_path):
    """
    Uses CRAFT (via EasyOCR) to find text regions.
    Returns boxes as [x_min, y_min, width, height]
    """
    # detect() returns: (horizontal_boxes, free_form_boxes)
    # We focus on horizontal_boxes for most standard text
    img = cv2.imread(image_path)
    result = reader.detect(img)
    
    horizontal_boxes = result[0][0] # List of [x_min, x_max, y_min, y_max]
    
    refined_boxes = []
    for box in horizontal_boxes:
        x_min, x_max, y_min, y_max = box
        # Convert to standard [x, y, w, h] format
        refined_boxes.append([x_min, y_min, x_max - x_min, y_max - y_min])
            
    return refined_boxes

if __name__ == "__main__":
    print("--- CRAFT Vision Engine Test ---")
    input_img = "debug_output/japanese_text.png"
    
    if not os.path.exists(input_img):
        print(f"Error: Run Step 4/5 capture first.")
    else:
        # 1. Run CRAFT Detection
        boxes = get_text_bboxes(input_img)
        print(f"CRAFT detected {len(boxes)} logical text regions.")
        
        # 2. Visualize
        img = cv2.imread(input_img)
        for (x, y, w, h) in boxes:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2) # Blue boxes for CRAFT
        
        # 3. VERIFIABLE OUTPUT
        output_path = "debug_output/craft_detection_test.png"
        cv2.imwrite(output_path, img)
        
        print(f"Sample BBox [X, Y, W, H]: {boxes[0] if boxes else 'None'}")
        print(f"Verification image saved to: {output_path}")
    print("--- Test Finished ---")