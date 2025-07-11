import signal
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QWidget, QTabWidget

from src.keyboard_handler import KeyboardHandler
from src.db_handlers import DBReader
from src.utils import init_database

from src.views.WPMGraph import WPMGraph
from src.views.SummaryGraph import SummaryGraph

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
        #self.setStyleSheet("background-color: #3f3f63;")

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tabs = QTabWidget()

        wpm_graph = WPMGraph(self.db, bin_size=MIN_BIN_SIZE)
        tabs.addTab(wpm_graph, "Monitoring")

        summary_graph = SummaryGraph(self.db)
        tabs.addTab(summary_graph, "Summary")

        layout.addWidget(tabs)
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
