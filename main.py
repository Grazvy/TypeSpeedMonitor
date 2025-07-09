import signal
import sys
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QWidget, QPushButton

from src.keyboard_handler import KeyboardHandler
from src.db_handlers import DBReader
from src.utils import init_database, get_db_path

from ui.WPMGraph import WPMGraph

MIN_BIN_SIZE = 5

class App(QWidget):
    def __init__(self):
        super().__init__()
        init_database()
        self.db = DBReader()
        self.init_ui()

        self.keyboard_handler = KeyboardHandler(MIN_BIN_SIZE)
        self.keyboard_handler.start_monitoring()

    def init_ui(self):
        self.setWindowTitle("App")
        self.setGeometry(0, 0, 1200, 800)
        self.setStyleSheet("background-color: #3f3f63;")

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        graph = WPMGraph(self.db, bin_size=MIN_BIN_SIZE)
        layout.addWidget(graph)

        button = QPushButton("Plot", self)
        button.clicked.connect(lambda: self.get_values())
        layout.addWidget(button)

        self.setLayout(layout)

    def get_values(self):
        print(self.db.read_data(time.time() - 300, time.time()))

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
