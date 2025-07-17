from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTabWidget

from src.keyboard_handler import KeyboardHandler
from src.db_handlers import DBReader
from src.utils import init_database, load_config, save_config

from src.views.WPMGraph import WPMGraph

MIN_BIN_SIZE = 5


class App(QWidget):
    modeToggled = pyqtSignal()

    def __init__(self):
        super().__init__()
        init_database()
        self.db = DBReader()
        self.config = load_config()
        self.dark_mode = self.config['dark_mode']
        self.init_ui()

        self.keyboard_handler = KeyboardHandler(MIN_BIN_SIZE)
        self.keyboard_handler.start_monitoring()

        self.summary_tab_loaded = False

        timer = QTimer()
        timer.singleShot(10000, self.post_init)

    def post_init(self):
        if not self.summary_tab_loaded:
            from src.views.SummaryGraph import SummaryGraph
            summary_graph = SummaryGraph(self, self.db)
            self.summary_container_layout.addWidget(summary_graph)
            self.summary_tab_loaded = True

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

        # Placeholder widget for summary tab
        self.summary_container = QWidget()
        self.summary_container_layout = QVBoxLayout(self.summary_container)
        tabs.addTab(self.summary_container, "Summary")

        def on_tab_changed(index):
            if not self.summary_tab_loaded and tabs.tabText(index) == "Summary":
                from src.views.SummaryGraph import SummaryGraph  # Lazy import
                summary_graph = SummaryGraph(self, self.db)
                self.summary_container_layout.addWidget(summary_graph)
                self.summary_tab_loaded = True

        tabs.currentChanged.connect(on_tab_changed)

        layout.addWidget(tabs)
        self.setLayout(layout)

        self.set_style()

    def toggle_darkmode(self):
        self.dark_mode = not self.dark_mode
        self.set_style()
        self.modeToggled.emit()
        self.config["dark_mode"] = self.dark_mode
        save_config(self.config)

    def set_style(self):
        if self.dark_mode:
            # dark arctic
            self.setStyleSheet(
                f"background-color: qlineargradient(x1: 0, y1: 1, stop: 0.1 #004a4a, stop: 0.6 #082026);")
        else:
            # light aquatic
            self.setStyleSheet(
                f"background-color: qlineargradient(x1: 0, y1: 1, stop: 0.3 #cbe7e3, stop: 0.85 #05999e);")

    def closeEvent(self, event):
        self.keyboard_handler.stop()
        self.db.close()
        event.accept()