import sys
import cv2
import pytesseract
from PyQt6.QtWidgets import QApplication

def check_system():
    print("--- System Verification ---")
    
    # Check Python Version
    print(f"Python Version: {sys.version}")
    
    # Check OpenCV
    print(f"OpenCV Version: {cv2.__version__}")
    
    # Check Tesseract Path and Visibility
    # This verifies if the 'apt' package is reachable
    try:
        tess_version = pytesseract.get_tesseract_version()
        print(f"Tesseract OCR: Found (Version {tess_version})")
    except Exception as e:
        print(f"Tesseract OCR: NOT FOUND. Error: {e}")

    # Check UI Capabilities
    if QApplication(sys.argv):
        print("PyQt6: Initialized successfully")
    
    print("--- Verification Finished ---")

if __name__ == "__main__":
    check_system()