import time
import cv2
import mss
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class CaptureThread(QThread):
    # This signal will later be used to pass the processed image to the OCR engine
    frame_processed = pyqtSignal(np.ndarray) 

    def __init__(self, viewport):
        super().__init__()
        self.viewport = viewport
        self.running = True

    def run(self):
        print("[SYSTEM] Capture Thread started. Grabbing frames at ~10 FPS.")
        with mss.mss() as sct:
            loop_count = 0
            while self.running:
                # 1. Get current geometry from the viewport
                rect = self.viewport.geometry()
                
                # We add a 4-pixel offset to avoid capturing the red border itself
                x = rect.x() + 4
                y = rect.y() + 4
                w = max(1, rect.width() - 8)
                h = max(1, rect.height() - 8)
                
                # 2. Define the capture region for mss
                monitor = {"top": y, "left": x, "width": w, "height": h}
                
                try:
                    # 3. Capture the screen directly from the OS window manager
                    sct_img = sct.grab(monitor)
                    
                    # 4. Convert raw mss pixels to an OpenCV numpy array (dropping the Alpha channel)
                    img_bgr = np.array(sct_img)[:, :, :3]
                    
                    # 5. Pre-process: Convert to Grayscale (removes distracting colors for OCR)
                    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                    
                    # 6. Pre-process: Upscale by 2x using Cubic Interpolation (makes small text readable)
                    img_processed = cv2.resize(img_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    
                    # 7. Emit the frame (we will connect this to OCR in the next step)
                    self.frame_processed.emit(img_processed)
                    
                    # 8. Verification: Print and save an image roughly every 3 seconds (30 frames)
                    if loop_count % 30 == 0:
                        cv2.imwrite("assets/debug_capture.png", img_processed)
                        print(f"[CAPTURE] Grabbed at X:{x} Y:{y}. Original: {img_bgr.shape} -> Processed: {img_processed.shape}. Saved to assets/debug_capture.png")
                    
                    loop_count += 1
                    time.sleep(0.1) # Sleep to limit capture to ~10 FPS, preventing CPU burnout
                    
                except Exception as e:
                    print(f"[ERROR] Capture loop encountered an issue: {e}")
                    time.sleep(1)

    def stop(self):
        """Safely terminates the background thread."""
        print("[SYSTEM] Stopping Capture Thread...")
        self.running = False
        self.wait()