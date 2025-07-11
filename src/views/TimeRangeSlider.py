from datetime import datetime

from PyQt6.QtGui import QMouseEvent, QPainter, QFont
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect

import time


class TimeRangeSlider(QWidget):
    rangeChanged = pyqtSignal(float, float)

    def __init__(self, interval="day"):
        super().__init__()
        self.setMouseTracking(True)

        self.update_format(interval)

        # UI state
        self.handle_radius = 7
        self.padding = 20
        self.margin = self.handle_radius + self.padding
        self.dragging_start = False
        self.dragging_end = False

        timer = QTimer(self)
        timer.timeout.connect(self.sync_time)
        timer.start(30_000)

    def update_format(self, text):
        if text == "day":
            self.step_minutes = 5
            self.duration_minutes = 24 * 60

            # default size = 4 hours
            self.start_val = self.duration_minutes - 4 * 60

        elif text == "month":
            self.step_minutes = 60 * 24
            self.duration_minutes = 60 * 24 * 30

            # default size = 1 week
            self.start_val = self.duration_minutes - 60 * 24 * 7

        elif text == "year":
            self.step_minutes = 60 * 24
            self.duration_minutes = 60 * 24 * 30 * 12

            # default size = 1 month
            self.start_val = self.duration_minutes - 60 * 24 * 30

        else:
            raise ValueError(f"Unrecognized text {text}")

        self.current_time = (time.time() // (self.step_minutes * 60) + 1) * self.step_minutes * 60
        self.end_val = self.duration_minutes
        self.rangeChanged.emit(self._val_to_ts(self.start_val), self._val_to_ts(self.end_val))

        self.update()

    def sync_time(self):
        self.current_time = (time.time() // (self.step_minutes * 60) + 1) * self.step_minutes * 60
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Track
        track_rect = QRect(self.margin, height // 2 - 4, width - 2 * self.margin, 8)
        painter.setBrush(Qt.GlobalColor.lightGray)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(track_rect)

        # Pixel-per-minute conversion
        pixel_per_min = track_rect.width() / self.duration_minutes
        x1 = self.margin + int(self.start_val * pixel_per_min)
        x2 = self.margin + int(self.end_val * pixel_per_min)

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

        # Time values from timestamps
        ts_start = self._val_to_ts(self.start_val)
        ts_end = self._val_to_ts(self.end_val)

        if self.step_minutes > 5:
            t_start = datetime.fromtimestamp(ts_start).strftime('%m.%d')
            t_end = datetime.fromtimestamp(ts_end).strftime('%m.%d')
        else:
            t_start = datetime.fromtimestamp(ts_start).strftime("%H:%M")
            t_end = datetime.fromtimestamp(ts_end).strftime("%H:%M")

        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 14))

        # Get text widths for alignment
        start_text_width = painter.fontMetrics().horizontalAdvance(t_start)
        end_text_width = painter.fontMetrics().horizontalAdvance(t_end)

        # Vertical position just above the handles
        label_y = self.height() // 2 - self.handle_radius - 8

        # Draw start time label
        painter.drawText(int(x1 - start_text_width / 2), label_y, t_start)

        # Draw end time label
        painter.drawText(int(x2 - end_text_width / 2), label_y, t_end)


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
        track_width = self.width() - 2 * self.margin
        return self.margin + val * track_width / self.duration_minutes

    def _pixel_to_val(self, px):
        track_width = self.width() - 2 * self.margin
        return int((px - self.margin) * self.duration_minutes / track_width)

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
