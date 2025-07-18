from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QBrush, QPen
from PyQt6.QtWidgets import QPushButton


class InfoButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                border: None;
            }
            QToolTip {
                color: black;
                background: #cbe7e3;
                font-size: 12px;
            }
        """)
        self.setToolTip("Input is recorded if: \n • time between keystrokes is < 1 sec \n • at least 8 keystrokes in a 5 sec interval")
        self.circle_color = QColor("white")
        self.i_color = QColor("white")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        btn_width = self.width()
        btn_height = self.height()
        min_dimension = min(btn_width, btn_height)


        circle_scale = 0.8
        line_width_scale = 0.08
        line_height_scale = 0.23
        line_offset_scale = 0.5
        dot_size_scale = 0.08
        dot_offset_scale = 0.26

        # Calculate sizes
        circle_size = int(min_dimension * circle_scale)
        line_width = int(min_dimension * line_width_scale)
        line_height = int(min_dimension * line_height_scale)
        dot_size = int(min_dimension * dot_size_scale)

        circle_x = (btn_width - circle_size) // 2
        circle_y = (btn_height - circle_size) // 2

        # Draw outer circle
        path = QPainterPath()
        path.addEllipse(circle_x, circle_y, circle_size, circle_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.circle_color))
        painter.drawPath(path)

        # Calculate centering for "i"
        i_center_x = int(btn_width // 2)
        line_x = int(i_center_x - (line_width // 2))  # Center the line horizontally
        line_y = int(circle_y + (circle_size * line_offset_scale))  # Center line vertically in circle
        dot_x = int(i_center_x - (dot_size // 2))  # Center the dot horizontally
        dot_y = int(circle_y + (circle_size * dot_offset_scale))  # Position dot near top

        # Draw "i"
        painter.setPen(QPen(self.i_color, line_width))
        painter.setBrush(QBrush(self.i_color))
        painter.drawRect(line_x, line_y, line_width, line_height)
        painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)

    def apply_dark_theme(self):
        self.circle_color = QColor("#004a4a")
        self.i_color = QColor("#082026")
        self.update()

    def apply_light_theme(self):
        self.circle_color = QColor("#cbe7e3")
        self.i_color = QColor("#05999e")
        self.update()