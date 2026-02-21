import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint

class TranslationLens(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translation Lens")
        
        # 1. Window Properties: Frameless, Always on Top, Semi-Transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.5) # 50% transparency to see text underneath
        
        self.setGeometry(100, 100, 400, 200) # Default size
        
        # UI Elements
        self.layout = QVBoxLayout()
        self.label = QLabel("DRAG ME OVER TEXT\nPress 'Q' to Quit")
        self.label.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.old_pos = None

    # Handle dragging the frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            # VERIFIABLE OUTPUT: Print coordinates as we move
            print(f"Lens Geometry: X={self.x()} Y={self.y()} W={self.width()} H={self.height()}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q or event.key() == Qt.Key.Key_Escape:
            print("Closing Lens...")
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    lens = TranslationLens()
    lens.show()
    print("--- UI Lens Active ---")
    sys.exit(app.exec())