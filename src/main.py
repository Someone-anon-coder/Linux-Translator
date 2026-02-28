import sys
import signal
from PyQt6.QtWidgets import QApplication
from viewport import ViewportWindow
from capture import CaptureThread
from ocr import OCRProcessor

def main():
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    # 1. Initialize UI
    window = ViewportWindow()
    window.show()
    
    # 2. Initialize Background Workers
    capture_thread = CaptureThread(window)
    ocr_processor = OCRProcessor()
    
    # 3. Connect Signals
    # Capture -> OCR
    capture_thread.frame_processed.connect(ocr_processor.process_frame)
    
    # OCR -> Viewport (Rendering)
    # This replaces the print verification we did in the last step
    ocr_processor.data_processed.connect(window.update_overlay)
    
    # 4. Start Capture
    capture_thread.start()
    
    # 5. Handle Exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    exit_code = app.exec()
    
    capture_thread.stop()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()