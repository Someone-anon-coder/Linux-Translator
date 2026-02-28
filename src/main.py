import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from viewport import ViewportWindow
from capture import CaptureThread
from ocr import OCRProcessor

def main():
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    # 1. UI
    window = ViewportWindow()
    window.show()
    
    # 2. Threads & Workers
    # Create the Capture Thread (inherits QThread)
    capture_thread = CaptureThread(window)
    
    # Create a separate thread for OCR
    ocr_thread = QThread()
    ocr_processor = OCRProcessor()
    ocr_processor.moveToThread(ocr_thread)
    
    # 3. Connect Signals
    
    # Pipeline: Capture -> OCR -> Viewport
    capture_thread.frame_processed.connect(ocr_processor.process_frame)
    ocr_processor.data_processed.connect(window.update_overlay)
    
    # Flow Control (The Handshake): OCR Finished -> Capture Ready
    ocr_processor.finished.connect(capture_thread.set_ready)
    
    # 4. Start Threads
    ocr_thread.start()      # Start the background thread for OCR
    capture_thread.start()  # Start the capture loop
    
    # 5. Cleanup Logic
    def cleanup():
        capture_thread.stop()
        ocr_thread.quit()
        ocr_thread.wait()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()