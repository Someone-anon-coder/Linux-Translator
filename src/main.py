import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from viewport import ViewportWindow
from ocr import OCRProcessor

def get_user_settings():
    print("=== LANGUAGE SELECTION ===")
    print("1. Source: Japanese -> Target: English")
    print("2. Source: English  -> Target: Spanish")
    print("3. Custom")
    choice = input("Select an option (1-3): ").strip()
    
    if choice == '1':
        return "jpn", "ja", "en", ""
    elif choice == '2':
        return "eng", "en", "es", " "
    else:
        t = input("Tesseract Code (jpn, eng): ").strip()
        s = input("Source (ja, en): ").strip()
        e = input("Target (en, es): ").strip()
        return t, s, e, " "

def main():
    tess_lang, lib_source, lib_target, join_char = get_user_settings()
    
    app = QApplication(sys.argv)
    
    # 1. Initialize UI (which now contains the capture timer)
    window = ViewportWindow()
    window.show()
    
    # 2. Initialize Background OCR Thread
    ocr_thread = QThread()
    ocr_processor = OCRProcessor(tess_lang, lib_source, lib_target, join_char)
    ocr_processor.moveToThread(ocr_thread)
    
    # 3. Connect Signals Directly Between UI and OCR
    window.frame_captured.connect(ocr_processor.process_frame)
    ocr_processor.data_processed.connect(window.update_overlay)
    ocr_processor.finished.connect(window.ocr_finished)
    
    # 4. Start
    ocr_thread.start()
    
    def cleanup():
        ocr_thread.quit()
        ocr_thread.wait()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()