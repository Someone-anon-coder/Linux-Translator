import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor

class ViewportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.oldPos = None
        self.initUI()

    def initUI(self):
        # 1. Set window flags to remove standard OS borders and keep it always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # 2. Make the background of the widget transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 3. Set initial position and size (X, Y, Width, Height)
        self.setGeometry(100, 100, 600, 200)

        # 4. Add a layout to hold the resize grip
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 5. Add a QSizeGrip to the bottom-right corner to allow resizing
        grip = QSizeGrip(self)
        # Style the grip so it's visible on the transparent background
        grip.setStyleSheet("background-color: rgba(255, 0, 0, 150); width: 15px; height: 15px;")
        layout.addWidget(grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        print("[SYSTEM] Viewport Initialized. Drag the window or resize via the bottom-right corner.")

    def paintEvent(self, event):
        """Draws a visible border around the transparent window."""
        painter = QPainter(self)
        # Red border, 4 pixels thick
        pen = QPen(QColor(255, 0, 0, 255), 4)
        painter.setPen(pen)
        # Draw the rectangle just inside the widget boundaries
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        """Records the initial mouse position for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Calculates the drag distance and moves the window."""
        if self.oldPos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Clears the drag position."""
        self.oldPos = None

    def moveEvent(self, event):
        """Fired automatically by PyQt6 when the window is moved."""
        self.print_geometry("MOVED")

    def resizeEvent(self, event):
        """Fired automatically by PyQt6 when the window is resized."""
        self.print_geometry("RESIZED")

    def print_geometry(self, action):
        """Prints the exact coordinates and dimensions to the terminal for verification."""
        rect = self.geometry()
        print(f"[VIEWPORT {action}] X: {rect.x():04d}, Y: {rect.y():04d} | Width: {rect.width():04d}, Height: {rect.height():04d}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ViewportWindow()
    window.show()
    
    # Graceful exit on terminal Ctrl+C
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec())