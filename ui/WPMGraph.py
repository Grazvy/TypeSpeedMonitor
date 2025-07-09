import time
from datetime import datetime

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


SPP = 1 / 5     # seconds per pixel

class WPMGraph(QFrame):
    def __init__(self, db, bin_size):
        super().__init__()
        self.setMinimumSize(600, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure(figsize=(8, 4)))
        layout.addWidget(self.canvas)

        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.canvas.setFocus()

        self.custom_interval = False
        self.db = db
        self.bin_size = bin_size
        self.interval_end = (time.time() // bin_size) * bin_size
        self.interval_size = self.width() * SPP

        # initial plot
        self.plot()

        # auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10_000)

        self.canvas.mpl_connect("scroll_event", self.on_scroll)

    def resizeEvent(self, event):
        pixels = self.width()
        self.interval_size = int(pixels * SPP)

        self.plot()
        super().resizeEvent(event)

    def update_plot(self):
        if not self.custom_interval:
            self.interval_end = (time.time() // self.bin_size) * self.bin_size
            self.plot()

    def on_scroll(self, event):
        self.custom_interval = True
        direction = event.step  # +1 for up, -1 for down
        self.interval_end += -direction * self.bin_size
        self.plot()

    def plot(self):
        interval_start = self.interval_end - self.interval_size
        time_bins = np.arange(interval_start, self.interval_end + self.bin_size, self.bin_size)

        data = self.db.read_data(interval_start, self.interval_end)

        all_bin_centers = []
        all_wpm_values = []
        all_time_labels = []

        for i in range(len(time_bins) - 1):
            bin_start = time_bins[i]
            bin_end = time_bins[i + 1]
            bin_center = (bin_start + bin_end) / 2

            all_bin_centers.append(bin_center)
            bin_data = [val for ts, val in data if bin_start <= ts < bin_end]

            all_wpm_values.append(np.mean(bin_data) if bin_data else np.nan)
            dt = datetime.fromtimestamp(bin_center)
            all_time_labels.append(dt.strftime('%H:%M'))

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        x_positions = np.arange(len(all_bin_centers))
        valid_mask = ~np.isnan(all_wpm_values)
        ax.bar(x_positions[valid_mask], np.array(all_wpm_values)[valid_mask],
               color='steelblue', alpha=0.8, width=1.0)

        ax.set_title('Words Per Minute', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')

        step = 12
        ax.set_xticks(x_positions[::step])
        ax.set_xticklabels([all_time_labels[i] for i in range(0, len(all_time_labels), step)],
                           rotation=45)

        y_max = self.db.get_max() * 1.25
        ax.set_ylim(0, y_max)

        self.canvas.figure.tight_layout()
        self.canvas.draw()
