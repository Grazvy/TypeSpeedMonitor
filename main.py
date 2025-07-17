import sys

from PyQt6.QtWidgets import QApplication

from App import App

app = QApplication(sys.argv)
window = App()
window.show()

sys.exit(app.exec())
