from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect

from src.utils import get_resource_path
class ToggleDarkmodeButton(QPushButton):
    def __init__(self, main):
        super().__init__()
        self.main_window = main
        self.clicked.connect(self.toggle_mode)
        self.setFixedSize(40, 40)

        self.BLUR_RADIUS = 15
        self.OFFSET = 3
        self.setupShadow()
        self.setupAnimation()

        self.apply_style()

    def toggle_mode(self):
        self.main_window.toggle_darkmode()

    def apply_style(self):
        self.setText("")

        if self.main_window.dark_mode:
            svg_path = get_resource_path("resources/sun.svg")
            self.shadow.setColor(QColor(0, 117, 117, 200))
            self.setStyleSheet("background-color: #0a3b3b;"
                                   "border-radius: 10px;")
        else:
            svg_path = get_resource_path("resources/moon.svg")
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.setStyleSheet("background-color: #cbe7e3;"
                                   "border-radius: 10px;")

        icon = QIcon(svg_path)
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))

    def setupShadow(self):
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(self.BLUR_RADIUS)
        self.shadow.setXOffset(self.OFFSET)
        self.shadow.setYOffset(self.OFFSET)
        self.setGraphicsEffect(self.shadow)

    def setupAnimation(self):
        # pressed animation
        self.pressed_animation = QPropertyAnimation(self, b"shadowOffset")
        self.pressed_animation.setDuration(100)
        self.pressed_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # released animation
        self.released_animation = QPropertyAnimation(self, b"shadowOffset")
        self.released_animation.setDuration(400)
        self.released_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    # Property for shadow offset animation
    @pyqtProperty(float)
    def shadowOffset(self):
        return self.shadow.xOffset()

    @shadowOffset.setter
    def shadowOffset(self, value):
        self.shadow.setXOffset(value)
        self.shadow.setYOffset(value)

    def mousePressEvent(self, event):
        self.pressed_animation.setStartValue(self.OFFSET)
        self.pressed_animation.setEndValue(1)
        self.pressed_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.released_animation.setStartValue(1)
        self.released_animation.setEndValue(self.OFFSET)
        self.released_animation.start()

        super().mouseReleaseEvent(event)
