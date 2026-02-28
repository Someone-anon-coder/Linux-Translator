import sys
import signal
from PyQt6.QtWidgets import QApplication
from viewport import ViewportWindow
from capture import CaptureThread
from ocr import OCRProcessor

def handle_final_data(data_list):
    """Temporary function to verify data reaches the main thread."""
    if data_list:
        print(f"[SYSTEM SUCCESS] Received {len(data_list)} text blocks ready for rendering.")

def main():
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    window = ViewportWindow()
    window.show()
    
    capture_thread = CaptureThread(window)
    ocr_processor = OCRProcessor()
    
    # Connect signals
    capture_thread.frame_processed.connect(ocr_processor.process_frame)
    # NEW: Connect the final packaged data to our print function
    ocr_processor.data_processed.connect(handle_final_data)
    
    capture_thread.start()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    exit_code = app.exec()
    
    capture_thread.stop()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()