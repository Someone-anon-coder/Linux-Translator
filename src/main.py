import sys
import signal
from PyQt6.QtWidgets import QApplication
from viewport import ViewportWindow
from capture import CaptureThread
from ocr import OCRProcessor

def main():
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    # 1. Initialize Viewport
    window = ViewportWindow()
    window.show()
    
    # 2. Initialize Background Workers
    capture_thread = CaptureThread(window)
    ocr_processor = OCRProcessor()
    
    # 3. Connect the captured frame signal directly to the OCR processor slot
    capture_thread.frame_processed.connect(ocr_processor.process_frame)
    
    # 4. Start Capture Thread
    capture_thread.start()
    
    # 5. Allow graceful exit on Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 6. Execute GUI Loop
    exit_code = app.exec()
    
    # 7. Cleanup
    capture_thread.stop()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()