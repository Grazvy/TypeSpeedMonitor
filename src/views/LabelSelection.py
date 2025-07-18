from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtWidgets import QComboBox, QStyleOptionComboBox, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QPainter, QColor


class CustomComboBox(QComboBox):
    def __init__(self, prefix):
        super().__init__()
        self.text_color = QColor("black")
        self.prefix = prefix
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opt = self.styleOption()
        self.style().drawComplexControl(self.style().ComplexControl.CC_ComboBox, opt, painter, self)

        # Prepare text styles
        value = self.currentText()

        prefix_font = QFont("Arial", 14)
        prefix_font.setPixelSize(14)
        prefix_font.setBold(False)
        value_font = QFont("Arial", 14)
        value_font.setPixelSize(14)
        value_font.setBold(True)

        painter.setFont(prefix_font)
        prefix_width = painter.fontMetrics().horizontalAdvance(self.prefix)

        rect = self.rect().adjusted(10, 0, -30, 0)

        # Draw prefix
        painter.setFont(prefix_font)
        painter.setPen(self.text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.prefix)

        # Draw value
        painter.setFont(value_font)
        painter.setPen(self.text_color)
        value_rect = QRect(rect.left() + prefix_width, rect.top(), rect.width() - prefix_width, rect.height())
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, value)

    def styleOption(self):
        option = QStyleOptionComboBox()
        option.initFrom(self)
        option.currentText = self.currentText()
        option.iconSize = self.iconSize()
        option.editable = self.isEditable()
        option.frame = self.hasFrame()
        return option


class LabelSelection(CustomComboBox):
    def __init__(self, prefix):
        super().__init__(prefix)

        self.BLUR_RADIUS = 15
        self.OFFSET = 3
        self.setupShadow()
        self.setupAnimation()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QComboBox {
                background-color: #0a3b3b;
                color: #eceff4;
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                max-width: 120px;
                height: 24px;
                padding-right: 30px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                height: 10px;
                width: 20px;
                margin: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #699191;
                border: None;
            }
        """)
        self.shadow.setColor(QColor(0, 117, 117, 200))
        self.text_color = QColor("#eceff4")
        self.update()

    def apply_light_theme(self):
        self.setStyleSheet("""
            QComboBox {
                background-color: #cbe7e3;
                color: #3B4252;
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                max-width: 120px;
                height: 24px;
                padding-right: 30px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                height: 10px;
                width: 20px;
                margin: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: None;
            }
        """)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.text_color = QColor("#3B4252")
        self.update()

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

