import signal
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QWidget

from src.keyboard_handler import KeyboardHandler
from src.db_handler import DBHandler

class App(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.db = DBHandler()

        self.keyboard_handler = KeyboardHandler(self.db)
        self.keyboard_handler.start_monitoring()

    def init_ui(self):
        self.setWindowTitle("App")
        self.setGeometry(0, 0, 1200, 800)
        self.setStyleSheet("background-color: #3f3f63;")

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.keyboard_handler.stop()
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()

    signal.signal(signal.SIGINT, lambda s, f: QApplication.quit())

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec())
