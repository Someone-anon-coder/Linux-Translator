import sys
import signal
from PyQt6.QtWidgets import QApplication
from viewport import ViewportWindow
from capture import CaptureThread

def main():
    print("=== STARTING ON-SCREEN TRANSLATOR ===")
    app = QApplication(sys.argv)
    
    # 1. Initialize and show the Viewport UI
    window = ViewportWindow()
    window.show()
    
    # 2. Initialize and start the background Screen Capture Thread
    # We pass the window reference so the thread knows where to look
    capture_thread = CaptureThread(window)
    capture_thread.start()
    
    # 3. Allow graceful exit when pressing Ctrl+C in the terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 4. Start the blocking GUI loop
    exit_code = app.exec()
    
    # 5. Cleanup when the application is closed
    capture_thread.stop()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()