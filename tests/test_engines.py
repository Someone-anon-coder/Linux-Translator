import cv2
import numpy as np
import pytesseract
import requests
import sys
import time

def create_test_image():
    print("[DEBUG] Generating a dummy image with text...")
    # Create a white background image
    img = np.ones((200, 500, 3), dtype=np.uint8) * 255
    # Add some English text to it
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Hello world, this is a local test."
    cv2.putText(img, text, (20, 100), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Save temporarily to disk for verification
    cv2.imwrite("images/dummy_test_image.png", img)
    print("[DEBUG] Dummy image saved at images/dummy_test_image.png")
    return img

def test_tesseract(image):
    print("[DEBUG] Running Tesseract OCR on the image...")
    try:
        # Run OCR
        extracted_text = pytesseract.image_to_string(image).strip()
        print(f"[DEBUG] Tesseract extracted: '{extracted_text}'")
        return extracted_text
    except Exception as e:
        print(f"[ERROR] Tesseract failed: {e}")
        sys.exit(1)

def test_libretranslate(text, source='en', target='es'):
    print(f"[DEBUG] Sending text to local LibreTranslate (http://127.0.0.1:5000)...")
    try:
        url = "http://127.0.0.1:5000/translate"
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }
        headers = { "Content-Type": "application/json" }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        translated_text = response.json().get("translatedText")
        print(f"[DEBUG] LibreTranslate returned: '{translated_text}'")
        return translated_text
    except requests.exceptions.ConnectionError:
        print("[ERROR] LibreTranslate connection failed. Is it running on port 5000?")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] LibreTranslate request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== STARTING ENGINE VERIFICATION ===")
    
    # 1. Image Creation
    img = create_test_image()
    
    # 2. OCR Test
    tesseract_output = test_tesseract(img)
    
    if not tesseract_output:
        print("[SYSTEM CHECK] FAILED: Tesseract returned empty text.")
        sys.exit(1)
        
    # 3. Translation Test
    translation_output = test_libretranslate(tesseract_output, source='en', target='es')
    
    # 4. Final Output
    print("\n[SYSTEM CHECK] Tesseract Output: '{}' | LibreTranslate Output: '{}' | Status: SUCCESS".format(
        tesseract_output, translation_output
    ))
    print("=== VERIFICATION COMPLETE ===")