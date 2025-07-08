import signal
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("App")
        self.setGeometry(0, 0, 1200, 800)
        self.setStyleSheet("background-color: #3f3f63;")

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = App()
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())
