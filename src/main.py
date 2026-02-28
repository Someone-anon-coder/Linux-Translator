import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from viewport import ViewportWindow
from capture import CaptureThread
from ocr import OCRProcessor

def get_user_settings():
    print("=== LANGUAGE SELECTION ===")
    print("1. Source: Japanese -> Target: English")
    print("2. Source: English  -> Target: Spanish")
    print("3. Source: English  -> Target: French")
    print("4. Source: French   -> Target: English")
    print("5. Custom (Enter codes manually)")
    
    choice = input("Select an option (1-5): ").strip()
    
    # Defaults
    tess = "jpn"
    lib_src = "ja"
    lib_tgt = "en"
    joinER = "" # No space for Japanese
    
    if choice == '1':
        tess, lib_src, lib_tgt, joinER = "jpn", "ja", "en", ""
    elif choice == '2':
        tess, lib_src, lib_tgt, joinER = "eng", "en", "es", " "
    elif choice == '3':
        tess, lib_src, lib_tgt, joinER = "eng", "en", "fr", " "
    elif choice == '4':
        tess, lib_src, lib_tgt, joinER = "fra", "fr", "en", " "
    elif choice == '5':
        print("\n--- Custom Configuration ---")
        tess = input("Tesseract Code (jpn, eng, fra): ").strip()
        lib_src = input("LibreTranslate Source (ja, en, fr): ").strip()
        lib_tgt = input("LibreTranslate Target (en, es, fr): ").strip()
        use_space = input("Use space between words? (y/n): ").lower().strip()
        joinER = " " if use_space == 'y' else ""
        
    print(f"\n[CONFIG] Tesseract: '{tess}' | Libre: '{lib_src}' -> '{lib_tgt}' | Separator: '{'SPACE' if joinER == ' ' else 'NONE'}'")
    return tess, lib_src, lib_tgt, joinER

def main():
    # 1. Get Configuration BEFORE starting UI
    tess_lang, lib_source, lib_target, join_char = get_user_settings()
    
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    # 2. UI
    window = ViewportWindow()
    window.show()
    
    # 3. Threads
    capture_thread = CaptureThread(window)
    
    ocr_thread = QThread()
    # Pass the configuration to the OCR Processor
    ocr_processor = OCRProcessor(tess_lang, lib_source, lib_target, join_char)
    ocr_processor.moveToThread(ocr_thread)
    
    # 4. Connections
    capture_thread.frame_processed.connect(ocr_processor.process_frame)
    ocr_processor.data_processed.connect(window.update_overlay)
    ocr_processor.finished.connect(capture_thread.set_ready)
    
    # 5. Start
    ocr_thread.start()
    capture_thread.start()
    
    def cleanup():
        capture_thread.stop()
        ocr_thread.quit()
        ocr_thread.wait()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()