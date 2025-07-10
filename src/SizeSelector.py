from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen

class SizeSelector(QWidget):
    intervalChanged = pyqtSignal(int)

    def __init__(self, size):
        super().__init__()
        self.current_size = size
        self.MIN_SIZE = 2
        self.MAX_SIZE = 7

        self.setup_ui()
        self.update_buttons()

    def setup_ui(self):
        layout = QHBoxLayout()
        # todo fix layout
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self.decrease_button = QPushButton()
        self.decrease_button.setFixedSize(40, 40)
        self.decrease_button.setIcon(self.create_widen_icon())
        self.decrease_button.setToolTip("decrease content")
        self.decrease_button.clicked.connect(self.decrease_content)
        self.decrease_button.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton:hover:!disabled {
                background-color: #b8b8b8;
            }
            QPushButton:pressed:!disabled {
                background-color: #b8b8b8;
            }
            QPushButton:disabled {
                border-color: #8f8f8f;
                background-color: #b8b8b8;
                color: #9ca3af;
            }
        """)

        self.increase_button = QPushButton()
        self.increase_button.setFixedSize(40, 40)
        self.increase_button.setIcon(self.create_narrow_icon())
        self.increase_button.setToolTip("increase content")
        self.increase_button.clicked.connect(self.increase_content)
        self.increase_button.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton:hover:!disabled {
                background-color: #b8b8b8;
            }
            QPushButton:pressed:!disabled {
                background-color: #b8b8b8;
            }
            QPushButton:disabled {
                border-color: #8f8f8f;
                background-color: #b8b8b8;
                color: #9ca3af;
            }
        """)

        layout.addWidget(self.decrease_button)
        layout.addWidget(self.increase_button)

        self.setLayout(layout)

    def create_narrow_icon(self):
        """Create a narrowing/decreasing icon (arrows pointing inward)"""
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        # Draw left arrow pointing right (inward)
        painter.drawLine(4, 15, 12, 15)  # Arrow shaft
        painter.drawLine(9, 11, 12, 15)  # Arrow head top
        painter.drawLine(9, 19, 12, 15)  # Arrow head bottom

        # Draw right arrow pointing left (inward)
        painter.drawLine(26, 15, 18, 15)  # Arrow shaft
        painter.drawLine(21, 11, 18, 15)  # Arrow head top
        painter.drawLine(21, 19, 18, 15)  # Arrow head bottom

        painter.end()
        return QIcon(pixmap)

    def create_widen_icon(self):
        """Create a widening/increasing icon (arrows pointing outward)"""
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        # Draw left arrow pointing left (outward)
        painter.drawLine(12, 15, 4, 15)  # Arrow shaft
        painter.drawLine(7, 11, 4, 15)  # Arrow head top
        painter.drawLine(7, 19, 4, 15)  # Arrow head bottom

        # Draw right arrow pointing right (outward)
        painter.drawLine(18, 15, 26, 15)  # Arrow shaft
        painter.drawLine(23, 11, 26, 15)  # Arrow head top
        painter.drawLine(23, 19, 26, 15)  # Arrow head bottom

        painter.end()
        return QIcon(pixmap)

    def decrease_content(self):
        """Increase the interval size"""
        if self.current_size < self.MAX_SIZE:
            self.current_size = min(self.current_size + 1, self.MAX_SIZE)
            self.update_buttons()
            self.intervalChanged.emit(self.current_size)

    def increase_content(self):
        """Decrease the interval size"""
        if self.current_size > self.MIN_SIZE:
            self.current_size = max(self.current_size - 1, self.MIN_SIZE)
            self.update_buttons()
            self.intervalChanged.emit(self.current_size)

    def update_buttons(self):
        """Update button enabled/disabled states"""
        self.increase_button.setEnabled(self.current_size > self.MIN_SIZE)
        self.decrease_button.setEnabled(self.current_size < self.MAX_SIZE)

    def set_interval_size(self, size):
        """Set the interval size programmatically"""
        if self.MIN_SIZE <= size <= self.MAX_SIZE:
            self.current_size = size
            self.update_buttons()
            self.intervalChanged.emit(self.current_size)
