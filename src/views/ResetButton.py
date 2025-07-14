from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor


class ResetButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.BLUR_RADIUS = 15
        self.OFFSET = 3
        self.setupShadow()
        self.setupAnimation()

    def apply_dark_theme(self):
        self.shadow.setColor(QColor(0, 117, 117, 200))
        self.setStyleSheet("background: #0a3b3b;"
                           "color: #eceff4;"
                           "border-radius: 12px;"
                           "font-size: 14px;"
                           "height: 24px;"
                           "padding: 8px;")

    def apply_light_theme(self):
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setStyleSheet("background: #cbe7e3;"
                           "color: #3B4252;"
                           "border-radius: 12px;"
                           "font-size: 14px;"
                           "height: 20px;"
                           "padding: 10px;")

    def setupShadow(self):
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(self.BLUR_RADIUS)
        self.shadow.setXOffset(self.OFFSET)
        self.shadow.setYOffset(self.OFFSET)
        self.shadow.setColor(QColor(0, 0, 0, 80))
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
