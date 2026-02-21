import cv2
from ultralytics import YOLO
import os

# Initialize the model (YOLOv8 Nano is used here as a base)
# In a production environment, you would use a model fine-tuned for text
model = YOLO('yolov8n.pt') 

def detect_text_regions(image_path):
    """
    Analyzes an image and returns a list of bounding boxes where text/objects are found.
    """
    results = model(image_path, conf=0.25, verbose=False) # 25% confidence threshold
    
    bboxes = []
    # Extract coordinates from results
    for result in results:
        for box in result.boxes:
            # Get coordinates: x1, y1, x2, y2
            coords = box.xyxy[0].tolist()
            bboxes.append([int(c) for c in coords])
            
    return bboxes

if __name__ == "__main__":
    print("--- Vision Engine Test ---")
    input_img = "debug_output/capture_test.png"
    
    if not os.path.exists(input_img):
        print(f"Error: {input_img} not found. Run Step 4 first.")
    else:
        # 1. Detect boxes
        boxes = detect_text_regions(input_img)
        print(f"Detected {len(boxes)} potential text regions.")
        
        # 2. Visualize for verification
        img = cv2.imread(input_img)
        for box in boxes:
            x1, y1, x2, y2 = box
            # Draw a bright green rectangle around detected regions
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 3. VERIFIABLE OUTPUT: Save the visual proof
        output_path = "debug_output/detection_test.png"
        cv2.imwrite(output_path, img)
        
        print(f"BBox Coordinates: {boxes}")
        print(f"Verification image saved to: {output_path}")
    print("--- Test Finished ---")