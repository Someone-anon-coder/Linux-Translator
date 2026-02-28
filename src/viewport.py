import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics

class ViewportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.oldPos = None
        self.overlay_data = [] # Store the latest translation data
        self.is_dragging = False # Track if user is moving the window
        self.initUI()

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
        print("[SYSTEM] Viewport Initialized.")

    @pyqtSlot(list)
    def update_overlay(self, data):
        """Receives new translation data from the main thread."""
        # If the user is currently dragging the window, ignore updates to prevent ghosting
        if self.is_dragging:
            return
            
        self.overlay_data = data
        self.update() # Triggers paintEvent

    def clear_overlay(self):
        """Instantly clears the text when moving starts."""
        self.overlay_data = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Draw the Red Border
        pen = QPen(QColor(255, 0, 0, 255), 4)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # 2. Draw the Translations
        # We use a semi-transparent black box to 'blur'/'obscure' the original text
        bg_color = QColor(0, 0, 0, 200) 
        text_color = QColor(255, 255, 255, 255)
        
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)

        for item in self.overlay_data:
            x, y, w, h = item['coords']
            text = item['translated']
            
            # Define the bounding box for the text
            # We add a small padding/margin adjustment
            rect = QRect(x, y, w, h)
            
            # Draw the background box (obscuring original text)
            painter.fillRect(rect, bg_color)
            
            # Draw the translated text centered in the box
            painter.setPen(text_color)
            
            # Auto-scale font if needed (simple heuristic)
            if h < 20: 
                font.setPointSize(8)
            elif h < 40: 
                font.setPointSize(10)
            else: 
                font.setPointSize(12)
            painter.setFont(font)
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.TextWordWrap, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            self.is_dragging = True
            self.clear_overlay() # Hides text immediately on click

    def mouseMoveEvent(self, event):
        if self.oldPos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
            # Ensure it stays clear while moving
            if self.overlay_data: 
                self.clear_overlay()

    def mouseReleaseEvent(self, event):
        self.oldPos = None
        self.is_dragging = False
        # The text will reappear automatically when the next OCR frame arrives (approx 100-200ms)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ViewportWindow()
    window.show()
    sys.exit(app.exec())