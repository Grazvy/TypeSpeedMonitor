import signal
import sys

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QWidget, QTabWidget

from src.keyboard_handler import KeyboardHandler
from src.db_handlers import DBReader
from src.utils import init_database

from src.views.WPMGraph import WPMGraph
from src.views.SummaryGraph import SummaryGraph

MIN_BIN_SIZE = 5

class App(QWidget):
    modeToggled = pyqtSignal()
    def __init__(self):
        super().__init__()
        init_database()
        self.db = DBReader()
        self.dark_mode = False
        self.init_ui()

        self.keyboard_handler = KeyboardHandler(MIN_BIN_SIZE)
        self.keyboard_handler.start_monitoring()

    def init_ui(self):
        self.setWindowTitle("App")
        self.setGeometry(0, 0, 1200, 800)

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
        QTabWidget::pane {
            background: transparent;
            border: none;
        }
        QTabBar {
            background: transparent;
        }
        """)

        wpm_graph = WPMGraph(self, self.db, bin_size=MIN_BIN_SIZE)
        tabs.addTab(wpm_graph, "Monitoring")

        summary_graph = SummaryGraph(self, self.db)
        tabs.addTab(summary_graph, "Summary")

        layout.addWidget(tabs)
        self.setLayout(layout)

        self.set_style()

    def toggle_darkmode(self):
        self.dark_mode = not self.dark_mode
        self.set_style()
        self.modeToggled.emit()

    def set_style(self):
        if self.dark_mode:
            # dark arctic
            self.setStyleSheet(f"background-color: qlineargradient(x1: 0, y1: 1, stop: 0.1 #004a4a, stop: 0.6 #082026);")
        else:
            # light aquatic
            self.setStyleSheet(f"background-color: qlineargradient(x1: 0, y1: 1, stop: 0.3 #cbe7e3, stop: 0.85 #05999e);")
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
