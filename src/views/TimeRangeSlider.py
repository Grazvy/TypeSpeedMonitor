from PyQt6.QtGui import QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect

import time


class TimeRangeSlider(QWidget):
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setMouseTracking(True)

        self.handle_width = 10
        self.duration_minutes = 12 * 60
        self.current_time = int(time.time())

        self.start_val = self.duration_minutes - 4 * 60  # 8 hours ago
        self.end_val = self.duration_minutes             # now

        self.dragging_start = False
        self.dragging_end = False

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

        track_rect = QRect(
            self.handle_width, self.height() // 2 - 4,
            self.width() - 2 * self.handle_width, 8
        )

        # Background track
        painter.setBrush(Qt.GlobalColor.lightGray)
        painter.drawRect(track_rect)

        # Active range
        pixel_per_min = track_rect.width() / self.duration_minutes
        x1 = self.handle_width + int(self.start_val * pixel_per_min)
        x2 = self.handle_width + int(self.end_val * pixel_per_min)

        active_rect = QRect(x1, track_rect.top(), x2 - x1, track_rect.height())
        painter.setBrush(Qt.GlobalColor.darkCyan)
        painter.drawRect(active_rect)

        # Draw handles
        for x in [x1, x2]:
            painter.setBrush(Qt.GlobalColor.black)
            painter.drawRect(x - self.handle_width // 2, track_rect.top() - 6,
                             self.handle_width, track_rect.height() + 12)

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().x()
        handle_pos_start = self._val_to_pixel(self.start_val)
        handle_pos_end = self._val_to_pixel(self.end_val)

        if abs(pos - handle_pos_start) < 10:
            self.dragging_start = True
        elif abs(pos - handle_pos_end) < 10:
            self.dragging_end = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (self.dragging_start or self.dragging_end):
            return

        pixel = event.position().x()
        val = self._pixel_to_val(pixel)
        val = max(0, min(self.duration_minutes, val))

        if self.dragging_start:
            self.start_val = min(val, self.end_val - 1)
        elif self.dragging_end:
            self.end_val = max(val, self.start_val + 1)

        self.rangeChanged.emit(self._val_to_ts(self.start_val), self._val_to_ts(self.end_val))
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging_start = False
        self.dragging_end = False

    def _val_to_pixel(self, val):
        return self.handle_width + int(val * (self.width() - 2 * self.handle_width) / self.duration_minutes)

    def _pixel_to_val(self, px):
        track_width = self.width() - 2 * self.handle_width
        return int((px - self.handle_width) * self.duration_minutes / track_width)

    def _val_to_ts(self, val):
        return self.current_time - (self.duration_minutes - val) * 60

    def set_range(self, start_ts, end_ts):
        now = int(time.time())
        self.current_time = now

        offset_start = now - start_ts
        offset_end = now - end_ts

        self.start_val = self.duration_minutes - offset_start // 60
        self.end_val = self.duration_minutes - offset_end // 60
        self.update()
        self.rangeChanged.emit(start_ts, end_ts)
