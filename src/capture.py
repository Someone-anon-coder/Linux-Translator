import time
import cv2
import mss
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

class CaptureThread(QThread):
    frame_processed = pyqtSignal(np.ndarray) 

    def __init__(self, viewport):
        super().__init__()
        self.viewport = viewport
        self.running = True
        self.can_process = True # NEW: Flag to control backpressure

    @pyqtSlot()
    def set_ready(self):
        """Called when OCR finishes. Allows us to capture the next frame."""
        self.can_process = True

    def run(self):
        print("[SYSTEM] Capture Thread started.")
        with mss.mss() as sct:
            while self.running:
                # 1. FLOW CONTROL: Only capture if the previous frame is finished
                if not self.can_process:
                    time.sleep(0.05) # Wait a bit and check again
                    continue

                rect = self.viewport.geometry()
                x, y, w, h = rect.x() + 4, rect.y() + 4, max(1, rect.width() - 8), max(1, rect.height() - 8)
                monitor = {"top": y, "left": x, "width": w, "height": h}
                
                try:
                    sct_img = sct.grab(monitor)
                    img_bgr = np.array(sct_img)[:, :, :3]
                    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                    img_processed = cv2.resize(img_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    
                    # 2. Lock the gate
                    self.can_process = False 
                    
                    self.frame_processed.emit(img_processed)
                    
                    # No need to sleep manually anymore; the speed is dictated by OCR speed now
                    
                except Exception as e:
                    print(f"[ERROR] Capture failed: {e}")
                    self.can_process = True # Reset on error so we don't get stuck
                    time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()