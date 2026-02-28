import sys
import cv2
import mss
import numpy as np
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class ViewportWindow(QWidget):
    # NEW: Signal to send the clean captured frame to the OCR thread
    frame_captured = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.oldPos = None
        self.overlay_data =[]
        self.is_dragging = False
        
        # State flags for our Blink Capture
        self.hide_temp = False
        self.ocr_processing = False
        
        self.initUI()
        
        # Capture Timer: Runs the screen grab routine every 1.5 seconds
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture_routine)
        self.capture_timer.start(1500)

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 200)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        grip = QSizeGrip(self)
        grip.setStyleSheet("background-color: rgba(255, 0, 0, 150); width: 15px; height: 15px;")
        layout.addWidget(grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
        print("[SYSTEM] Viewport Initialized with Blink Capture.")

    @pyqtSlot()
    def ocr_finished(self):
        """Called when the background OCR thread is done processing."""
        self.ocr_processing = False

    @pyqtSlot(list)
    def update_overlay(self, data):
        if self.is_dragging: return
        self.overlay_data = data
        self.update()

    def clear_overlay(self):
        self.overlay_data =[]
        self.update()

    def capture_routine(self):
        """Safely hides the translation, captures the raw screen, and restores translation."""
        # Don't capture if user is dragging or if OCR is still busy with the last frame
        if self.is_dragging or self.ocr_processing:
            return

        # 1. HIDE the translations
        self.hide_temp = True
        self.repaint() # Synchronous paint request
        QApplication.processEvents() # Force OS to process the paint
        time.sleep(0.05) # Give the OS compositor 50ms to physically clear the screen
        QApplication.processEvents()

        # 2. CAPTURE the clean screen
        rect = self.geometry()
        x, y = rect.x() + 4, rect.y() + 4
        w, h = max(1, rect.width() - 8), max(1, rect.height() - 8)
        
        try:
            with mss.mss() as sct:
                sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
        except Exception as e:
            print(f"[ERROR] Capture failed: {e}")
            self.hide_temp = False
            self.update()
            return
            
        # 3. RESTORE the translations immediately
        self.hide_temp = False
        self.update()

        # 4. PRE-PROCESS and EMIT to the background OCR thread
        img_bgr = np.array(sct_img)[:, :, :3]
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        img_processed = cv2.resize(img_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        self.ocr_processing = True
        self.frame_captured.emit(img_processed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Always draw the Red Border
        pen = QPen(QColor(255, 0, 0, 255), 4)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # If we are in the middle of a screenshot, DO NOT draw the text!
        if self.hide_temp:
            return

        # Draw the Translations
        bg_color = QColor(0, 0, 0, 200) 
        text_color = QColor(255, 255, 255, 255)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)

        for item in self.overlay_data:
            x, y, w, h = item['coords']
            
            # FIX: Add +4 to X and Y to perfectly align the translation 
            # with the red border offset we used during capture!
            rect = QRect(x + 4, y + 4, w, h)
            
            painter.fillRect(rect, bg_color)
            painter.setPen(text_color)
            
            if h < 20: font.setPointSize(8)
            elif h < 40: font.setPointSize(10)
            else: font.setPointSize(12)
            painter.setFont(font)
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, item['translated'])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            self.is_dragging = True
            self.clear_overlay()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
            if self.overlay_data: 
                self.clear_overlay()

    def mouseReleaseEvent(self, event):
        self.oldPos = None
        self.is_dragging = False