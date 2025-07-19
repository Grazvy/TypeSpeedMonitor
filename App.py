from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QOperatingSystemVersion, QEvent
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTabWidget

from src.keyboard_handler import KeyboardHandler
from src.db_handlers import DBReader
from src.utils import init_database, load_config, save_config, get_resource_path

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

        self.summary_graph = None

        timer = QTimer()
        timer.singleShot(10000, self.post_init)

        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.check_focus)
        self.focus_timer.start(1000)

    def post_init(self):
        if self.summary_graph is None:
            from src.views.SummaryGraph import SummaryGraph
            self.summary_graph = SummaryGraph(self, self.db)
            self.summary_container_layout.addWidget(self.summary_graph)

    def init_ui(self):
        self.setWindowTitle("TypeSpeedMonitor")
        icon_path = get_resource_path("resources/icon.iconset/icon_128x128.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(0, 0, 1200, 800)

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tabs = QTabWidget()
        self.wpm_graph = WPMGraph(self, self.db, bin_size=MIN_BIN_SIZE)
        self.tabs.addTab(self.wpm_graph, "Monitoring")

        # Placeholder widget for summary tab
        self.summary_container = QWidget()
        self.summary_container_layout = QVBoxLayout(self.summary_container)
        self.tabs.addTab(self.summary_container, "Summary")

        def on_tab_changed(index):
            if self.summary_graph is None and self.tabs.tabText(index) == "Summary":
                from src.views.SummaryGraph import SummaryGraph  # Lazy import
                self.summary_graph = SummaryGraph(self, self.db)
                self.summary_container_layout.addWidget(self.summary_graph)

        self.tabs.currentChanged.connect(on_tab_changed)

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.set_style()

    def check_focus(self):
        if self.isActiveWindow():
            self.wpm_graph.resume()
            if self.summary_graph:
                self.summary_graph.resume()
        else:
            self.wpm_graph.pause()
            if self.summary_graph:
                self.summary_graph.pause()

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

        self.set_tabs_style()

    def set_tabs_style(self):
        bg = "#0a3b3b" if self.dark_mode else "#11b2b8"
        if QOperatingSystemVersion.current().type() == QOperatingSystemVersion.OSType.MacOS:
            self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background: transparent;
                border: none;
            }
            QTabBar {
                background: transparent;
            }
            """)
        else:
            self.tabs.tabBar().setFont(QFont("Arial", 10))
            self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: transparent;
                border: none;
            }}
            QTabBar {{
                background: transparent;
            }}
            QTabBar::tab {{
                background: {bg};
                color: white;
                font-weight: bold;
                padding: 4px 16px;
                min-width: 60px;
            }}
            QTabBar::tab::first {{
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }}
            QTabBar::tab::last {{
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
            background: #2b46d6;
            }}
            """)

    def closeEvent(self, event):
        self.keyboard_handler.stop()
        self.db.close()
        event.accept()
