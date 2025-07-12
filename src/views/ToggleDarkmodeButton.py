from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton

class ToggleDarkmodeButton(QPushButton):
    modeToggled = pyqtSignal()
    def __init__(self, main):
        super().__init__()
        self.main_window = main
        self.clicked.connect(self.toggle_mode)
        self.setIcon()
        self.setFixedSize(40, 40)

    def toggle_mode(self):
        self.main_window.toggle_darkmode()
        self.setIcon()
        self.modeToggled.emit()

    def setIcon(self):
        if self.main_window.dark_mode:
            self.setText("☀️")
        else:
            self.setText("🌙")
