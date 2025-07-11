from PyQt6.QtWidgets import QPushButton

class ToggleDarkmodeButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.setText("🌙")
        self.clicked.connect(self.toggle_mode)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setText("☀️")
        else:
            self.setText("🌙")
