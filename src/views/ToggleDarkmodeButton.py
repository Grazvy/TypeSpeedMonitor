from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect


class ToggleDarkmodeButton(QPushButton):
    def __init__(self, main):
        super().__init__()
        self.main_window = main
        self.clicked.connect(self.toggle_mode)
        self.setFixedSize(40, 40)

        self.BLUR_RADIUS = 15
        self.OFFSET = 2
        self.setupShadow()
        self.setupAnimation()

        self.setIcon()

    def toggle_mode(self):
        self.main_window.toggle_darkmode()

    def setIcon(self):
        if self.main_window.dark_mode:
            self.setText("☀️")
            self.shadow.setColor(QColor(0, 117, 117, 200))
            self.setStyleSheet("background-color: #0a3b3b;"
                               "border-radius: 10px;")
        else:
            self.setText("🌙")
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.setStyleSheet("background-color: #cbe7e3;"
                               "border-radius: 10px;")

    def setupShadow(self):
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(self.BLUR_RADIUS)
        self.shadow.setXOffset(self.OFFSET)
        self.shadow.setYOffset(self.OFFSET)
        self.setGraphicsEffect(self.shadow)

    def setupAnimation(self):
        # pressed animation
        self.pressed_animation = QPropertyAnimation(self, b"shadowOffset")
        self.pressed_animation.setDuration(50)
        self.pressed_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # released animation
        self.released_animation = QPropertyAnimation(self, b"shadowOffset")
        self.released_animation.setDuration(300)
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
