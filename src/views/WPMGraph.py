import time
from datetime import datetime, timedelta

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QPushButton, QComboBox, QHBoxLayout, QToolTip, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.views.ToggleDarkmodeButton import ToggleDarkmodeButton
from src.utils import apply_dark_theme, apply_light_theme

SPP = 1/ 5

class WPMGraph(QFrame):
    def __init__(self, main, db, bin_size, mult=15):
        super().__init__()
        self.main_window = main
        self.color = '#537575' if main.dark_mode else 'steelblue'
        self.mult = mult    # normalized = one minute
        self.seconds_per_pixel = SPP
        self.custom_interval = False
        self.db = db
        self.bin_size = bin_size * mult
        self.interval_end = time.time() + bin_size
        self.interval_size = self.width() * self.seconds_per_pixel * mult

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip("scroll to change the interval")
        QToolTip.setFont(QFont("Arial", 18))

        layout = QVBoxLayout(self)
        controls_layout = QHBoxLayout()

        self.toggle = ToggleDarkmodeButton(self.main_window)
        controls_layout.addWidget(self.toggle)

        self.label_selection = QComboBox()
        all_mults = [1, 5, 15, 30, 60, 24 * 60, 7 * 24 * 60, 30 * 24 * 60, 12 * 30 * 24 * 60]
        self.label_selection.addItems(["1 min", "5 min", "15 min", "30 min", "60 min", "1 day", "1 week", "1 month", "1 year"])
        self.label_selection.setCurrentIndex(all_mults.index(mult))
        self.label_selection.currentTextChanged.connect(self.update_mult)
        controls_layout.addWidget(self.label_selection)

        self.back_to_start = QPushButton("reset position")
        self.back_to_start.clicked.connect(self.reset_position)
        controls_layout.addWidget(self.back_to_start)

        layout.addLayout(controls_layout)

        self.canvas = FigureCanvas(Figure(figsize=(8, 4)))
        self.canvas.setMinimumSize(600, 500)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.canvas.setFocus()
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        layout.addWidget(self.canvas)

        self.main_window.modeToggled.connect(self.toggle_darkmode)

        # initial plot
        self.plot()

        # auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(2_000)

    def toggle_darkmode(self):
        self.color = '#537575' if self.main_window.dark_mode else 'steelblue'
        self.toggle.setIcon()
        self.plot()

    def resizeEvent(self, event):
        self.interval_size = self.width() * self.seconds_per_pixel * self.mult
        self.plot()
        super().resizeEvent(event)

    def update_plot(self):
        if not self.custom_interval:
            self.interval_end = time.time() + self.bin_size
            self.plot()

    def on_scroll(self, event):
        self.custom_interval = True
        self.setToolTip("")
        direction = event.step  # +1 for up, -1 for down
        self.interval_end += -direction * self.mult
        self.plot()

    def reset_position(self):
        self.custom_interval = False
        self.interval_end = time.time() + self.bin_size
        self.plot()

    def get_last_bin(self):
        return (self.interval_end // self.bin_size) * self.bin_size

    def update_spp(self, num_pixels):
        self.seconds_per_pixel = 1 / num_pixels
        self.interval_size = self.width() * self.seconds_per_pixel * self.mult
        self.plot()

    def update_mult(self, text):
        if text == "1 min":
            new_mult = 1
        elif text == "5 min":
            new_mult = 5
        elif text == "15 min":
            new_mult = 15
        elif text == "30 min":
            new_mult = 30
        elif text == "60 min":
            new_mult = 60
        elif text == "1 day":
            new_mult = 24 * 60
        elif text == "1 week":
            new_mult = 7 * 24 * 60
        elif text == "1 month":
            new_mult = 30 * 24 * 60
        elif text == "1 year":
            new_mult = 12 * 30 * 24 * 60
        else:
            raise ValueError(f"Unrecognized text {text}")

        self.bin_size = (self.bin_size // self.mult) * new_mult
        self.interval_size = (self.interval_size // self.mult) * new_mult
        self.mult = new_mult
        self.plot()


    def plot(self):
        last_bin = self.get_last_bin()
        interval_start = last_bin - self.interval_size
        time_bins = np.arange(interval_start, last_bin + self.bin_size, self.bin_size)

        data = self.db.read_data(interval_start, time_bins[-1])

        all_bin_centers = []
        all_wpm_values = []

        for i in range(len(time_bins) - 1):
            bin_start = time_bins[i]
            bin_end = time_bins[i + 1]
            bin_center = (bin_start + bin_end) / 2

            all_bin_centers.append(bin_center)
            bin_data = [val for ts, val in data if bin_start <= ts < bin_end]
            all_wpm_values.append(np.mean(bin_data) if bin_data else np.nan)

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        x_vals = np.array(all_bin_centers)
        y_vals = np.array(all_wpm_values)
        valid_mask = ~np.isnan(y_vals)

        if valid_mask.any():
            ax.bar(x_vals[valid_mask], y_vals[valid_mask], width=self.bin_size,
                   color=self.color, alpha=0.8, align='center')

        ax.set_xlim(time_bins[0], time_bins[-1])

        label_positions = []
        label_strings = []
        seen_keys = set()

        for ts in all_bin_centers:
            dt = datetime.fromtimestamp(ts)

            if self.mult <= 60:  # Minute-level (1s, 5s, etc.)
                bucket_minute = (dt.minute // self.mult) * self.mult
                key = (dt.hour, bucket_minute, dt.date())
                label = dt.strftime('%H:%M')
            elif self.mult == 60 * 24:  # Daily
                key = dt.date()
                label = dt.strftime('%a %d')
            elif self.mult == 7 * 24 * 60:  # Weekly
                key = dt.date() - timedelta(days=dt.weekday())
                label = key.strftime('%m.%d')
            elif self.mult == 30 * 24 * 60:  # Monthly
                key = dt.replace(day=1).date()
                label = key.strftime('%b')
            elif self.mult == 12 * 30 * 24 * 60:  # Yearly
                key = dt.year
                label = key
            else:
                raise ValueError(f"Unrecognized multiplier {self.mult}")

            if key not in seen_keys:
                seen_keys.add(key)
                label_positions.append(ts)
                label_strings.append(label)

        if len(label_positions) > 1:
            too_close = label_positions[1] - label_positions[0] < 60 * self.mult
            first_label = 1 if too_close else 0
        else:
            first_label = 0

        ax.set_xticks(label_positions[first_label:])
        ax.set_xticklabels(label_strings[first_label:], rotation=45, ha='right')

        title = ""
        center_ts = (time_bins[0] + time_bins[-1]) / 2
        dt = datetime.fromtimestamp(center_ts)
        if self.mult <= 60:
            today = datetime.now()
            if dt.day == today.day:
                title = "today"
            else:
                title = dt.strftime("%d %b %Y")

        elif self.mult <= 60 * 24 * 7:
            title = dt.strftime("%b %Y")

        elif self.mult == 60 * 24 * 30:
            title = dt.strftime("%Y")

        ax.set_ylabel('Words Per Minute (WPM)', fontsize=12)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')

        y_max = self.db.get_max() * 1.25
        ax.set_ylim(0, y_max)

        if self.main_window.dark_mode:
            apply_dark_theme(ax)
        else:
            apply_light_theme(ax)

        self.canvas.figure.tight_layout
        self.canvas.draw_idle()
