from datetime import datetime

from PyQt6.QtGui import QMouseEvent, QPainter, QFont
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect

import time


class TimeRangeSlider(QWidget):
    rangeChanged = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMouseTracking(True)

        # Time configuration
        self.step_minutes = 5
        self.duration_minutes = 12 * 60
        self.current_time = (time.time() // (self.step_minutes * 60) + 1) * self.step_minutes * 60

        # Default interval: last 4 hours
        self.start_val = self.duration_minutes - 4 * 60
        self.end_val = self.duration_minutes

        # UI state
        self.handle_radius = 7
        self.dragging_start = False
        self.dragging_end = False

        # Live time sync
        timer = QTimer(self)
        timer.timeout.connect(self.sync_time)
        timer.start(60_000)

    def update_format(self):
        pass

    def sync_time(self):
        self.current_time = int(time.time())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        margin = self.handle_radius + 5

        # Track
        track_rect = QRect(margin, height // 2 - 4, width - 2 * margin, 8)
        painter.setBrush(Qt.GlobalColor.lightGray)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(track_rect)

        # Pixel-per-minute conversion
        pixel_per_min = track_rect.width() / self.duration_minutes
        x1 = margin + int(self.start_val * pixel_per_min)
        x2 = margin + int(self.end_val * pixel_per_min)

        # Active range
        active_rect = QRect(x1, track_rect.top(), x2 - x1, track_rect.height())
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawRect(active_rect)

        # Draw circular handles
        painter.setBrush(Qt.GlobalColor.gray)
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawEllipse(x1 - self.handle_radius, height // 2 - self.handle_radius,
                            2 * self.handle_radius, 2 * self.handle_radius)
        painter.drawEllipse(x2 - self.handle_radius, height // 2 - self.handle_radius,
                            2 * self.handle_radius, 2 * self.handle_radius)

        # Draw time range label
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 14))

        ts_start = self._val_to_ts(self.start_val)
        ts_end = self._val_to_ts(self.end_val)

        t_start = datetime.fromtimestamp(ts_start).strftime("%H:%M")
        t_end = datetime.fromtimestamp(ts_end).strftime("%H:%M")

        label = f"summarize from {t_start} to {t_end}"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignTop, label)


    def get_interval(self):
        return self._val_to_ts(self.start_val), self._val_to_ts(self.end_val)
    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().x()
        x1 = self._val_to_pixel(self.start_val)
        x2 = self._val_to_pixel(self.end_val)

        if abs(pos - x1) < 2 * self.handle_radius:
            self.dragging_start = True
        elif abs(pos - x2) < 2 * self.handle_radius:
            self.dragging_end = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (self.dragging_start or self.dragging_end):
            return

        val = self._pixel_to_val(event.position().x())
        val = max(0, min(self.duration_minutes, val))
        val = (val // self.step_minutes) * self.step_minutes  # Snap to 5-minute step

        if self.dragging_start:
            self.start_val = min(val, self.end_val - self.step_minutes)
        elif self.dragging_end:
            self.end_val = max(val, self.start_val + self.step_minutes)

        self.rangeChanged.emit(self._val_to_ts(self.start_val), self._val_to_ts(self.end_val))
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging_start = False
        self.dragging_end = False

    def _val_to_pixel(self, val):
        track_width = self.width() - 2 * (self.handle_radius + 5)
        return (self.handle_radius + 5) + val * track_width / self.duration_minutes

    def _pixel_to_val(self, px):
        track_width = self.width() - 2 * (self.handle_radius + 5)
        return int((px - (self.handle_radius + 5)) * self.duration_minutes / track_width)

    def _val_to_ts(self, val):
        return self.current_time - (self.duration_minutes - val) * 60

    def set_range(self, start_ts, end_ts):
        self.current_time = int(time.time())

        offset_start = self.current_time - start_ts
        offset_end = self.current_time - end_ts

        self.start_val = self.duration_minutes - offset_start // 60
        self.end_val = self.duration_minutes - offset_end // 60
        self.update()
        self.rangeChanged.emit(start_ts, end_ts)
