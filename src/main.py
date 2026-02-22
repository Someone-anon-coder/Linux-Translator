import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

# Import our custom modules
from capture_engine import capture_region
from vision_engine import get_text_bboxes
from ocr_worker import extract_text_from_boxes
from translator_bridge import process_and_translate

class MagicLens(QWidget):
    def __init__(self):
        super().__init__()
        # 1. Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 400)
        
        self.translations = [] # Stores our Mapped Boxes
        self.is_processing = False
        
        # 2. The Heartbeat: Run the pipeline every 2 seconds (to save CPU)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_pipeline)
        self.timer.start(2000) 

        self.old_pos = None
        print("--- Magic Lens Initialized ---")

    def run_pipeline(self):
        if self.is_processing: return
        self.is_processing = True

        # A. Capture
        frame = capture_region(self.x(), self.y(), self.width(), self.height())
        cv2.imwrite("debug_output/live_capture.png", frame) # Verifiable debug

        # B. Detect & OCR
        bboxes = get_text_bboxes("debug_output/live_capture.png")
        if bboxes:
            ocr_results = extract_text_from_boxes("debug_output/live_capture.png", bboxes)
            
            # C. Translate
            self.translations = process_and_translate(ocr_results, target_lang="en")
            
            # D. Trigger UI Update
            self.update() 
        
        self.is_processing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Draw the Lens Background (semi-transparent guide)
        painter.setBrush(QColor(0, 0, 0, 20)) # Very faint tint
        painter.setPen(QPen(QColor(0, 255, 0, 100), 2)) # Green border
        painter.drawRect(self.rect())

        # 2. Draw Translated Blocks
        for item in self.translations:
            x, y, w, h = item['box']
            translated_text = item['translated']

            # A. Draw "Blur" Mask (Solid background to hide original text)
            painter.setBrush(QColor(255, 255, 255, 230)) # Off-white, mostly opaque
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, w, h)

            # B. Draw Translated Text
            painter.setPen(QColor(0, 0, 0)) # Black text
            font = QFont("Arial", 10)
            # Dynamic Font Scaling: try to fit the box
            font.setPixelSize(max(12, int(h * 0.7))) 
            painter.setFont(font)
            
            # Render the text inside the original box coordinates
            painter.drawText(QRect(x, y, w, h), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, translated_text)

    # Mouse handling for dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:
            self.close()

if __name__ == "__main__":
    print("--- Starting Magic Lens ---")
    app = QApplication(sys.argv)
    window = MagicLens()
    window.show()
    
    sys.exit(app.exec())
    print("--- Magic Lens Closed ---")