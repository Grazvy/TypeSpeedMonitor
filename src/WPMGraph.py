import time
from datetime import datetime

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QPushButton, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


SPP = 1 / 5     # seconds per pixel

class WPMGraph(QFrame):
    def __init__(self, db, bin_size):
        super().__init__()
        self.setMinimumSize(600, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)

        self.back_to_start = QPushButton(f"back to current time", self)
        self.back_to_start.clicked.connect(self.reset_position)
        layout.addWidget(self.back_to_start)

        self.combo = QComboBox()
        self.combo.addItems(["1 min", "5 min", "15 min", "30 min", "60 min"])
        self.combo.currentTextChanged.connect(self.update_mult)
        layout.addWidget(self.combo)

        self.canvas = FigureCanvas(Figure(figsize=(8, 4)))
        layout.addWidget(self.canvas)

        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.canvas.setFocus()

        self.mult = 1    # normalized to one minute
        self.custom_interval = False
        self.db = db
        self.bin_size = bin_size
        self.interval_end = time.time()
        self.interval_size = self.width() * SPP

        # initial plot
        self.plot()

        # auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(5_000)

        self.canvas.mpl_connect("scroll_event", self.on_scroll)

    def resizeEvent(self, event):
        pixels = self.width()
        self.interval_size = int(pixels * SPP) * self.mult

        self.plot()
        super().resizeEvent(event)

    def update_plot(self):
        if not self.custom_interval:
            self.interval_end = time.time()
            self.plot()

    def on_scroll(self, event):
        self.custom_interval = True
        direction = event.step  # +1 for up, -1 for down
        self.interval_end += -direction * self.mult
        self.plot()

    def reset_position(self):
        self.custom_interval = False
        self.interval_end = time.time()
        self.plot()

    def get_last_bin(self):
        return (self.interval_end // self.bin_size) * self.bin_size

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

        data = self.db.read_data(interval_start, last_bin)

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
                   color='steelblue', alpha=0.8, align='center')

        ax.set_xlim(time_bins[0], time_bins[-1])

        label_positions = []
        label_strings = []
        seen_buckets = set()

        for ts in all_bin_centers:
            dt = datetime.fromtimestamp(ts)

            bucket_minute = (dt.minute // self.mult) * self.mult
            bucket_key = (dt.hour, bucket_minute)

            if bucket_key not in seen_buckets:
                seen_buckets.add(bucket_key)
                label_positions.append(ts)
                label_strings.append(dt.strftime('%H:%M'))

        if label_positions[1] - label_positions[0] < 60 * self.mult:
            # remove first label, if too close
            ax.set_xticks(label_positions[1:])
            ax.set_xticklabels(label_strings[1:], rotation=45, ha='right')
        else:
            ax.set_xticks(label_positions)
            ax.set_xticklabels(label_strings, rotation=45, ha='right')

        ax.set_title('Words Per Minute', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')

        y_max = self.db.get_max() * 1.25
        ax.set_ylim(0, y_max)

        self.canvas.figure.tight_layout
        self.canvas.draw()
