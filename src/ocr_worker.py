import cv2
import pytesseract
import os

def preprocess_for_ocr(img_bin):
    """
    Cleans the image to make it easier for Tesseract to read.
    """
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(img_bin, cv2.COLOR_BGR2GRAY)
    
    # 2. Rescale (Zoom in) if the text is too small (Tesseract likes >30px height)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 3. Thresholding (Turns image into pure Black and White)
    # Using Otsu's Binarization to automatically find the best threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def extract_text_from_boxes(image_path, bboxes, lang='jpn+eng'):
    """
    Crops the image based on bboxes and runs Tesseract OCR.
    """
    original_img = cv2.imread(image_path)
    results = []

    for i, (x, y, w, h) in enumerate(bboxes):
        # Prevent cropping outside image boundaries
        x, y, w, h = max(0, x), max(0, y), max(1, w), max(1, h)
        
        # 1. Crop the text region
        crop = original_img[y:y+h, x:x+w]
        
        # 2. Preprocess the crop
        cleaned_crop = preprocess_for_ocr(crop)
        
        # 3. Save a sample of the cleaned crop for verification
        if i < 5: # Only save the first 5 to avoid clutter
            cv2.imwrite(f"debug_output/cleaned_crop_{i}.png", cleaned_crop)

        # 4. Run Tesseract (psm 6: Assume a single uniform block of text)
        text = pytesseract.image_to_string(cleaned_crop, lang=lang, config='--psm 6')
        clean_text = text.strip()
        
        if clean_text:
            results.append({
                "box": [x, y, w, h],
                "text": clean_text
            })
            
    return results

if __name__ == "__main__":
    print("--- OCR Pipeline Test ---")
    input_img = "debug_output/japanese_text.png"
    
    # For testing, we simulate the BBoxes from Step 6
    # (In the final app, these come dynamically from the vision_engine)
    from vision_engine import get_text_bboxes
    
    if not os.path.exists(input_img):
        print("Error: Capture an image first.")
    else:
        print("Locating text regions...")
        boxes = get_text_bboxes(input_img)
        
        print(f"Extracting text from {len(boxes)} regions...")
        ocr_results = extract_text_from_boxes(input_img, boxes)
        
        # VERIFIABLE OUTPUT: Print what the computer 'read'
        for res in ocr_results:
            print(f"Pos {res['box']} -> OCR Output: {res['text']}")
            
    print("--- Test Finished ---")