import time
import numpy as np
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SummaryGraph(QFrame):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        controls_layout = QHBoxLayout()
        # todo start/stop selection

        self.canvas = FigureCanvas(Figure(figsize=(8, 4)))
        self.canvas.setMaximumHeight(500)
        layout.addWidget(self.canvas)

        self.plot_summary(time.time() - 10000000, time.time())

    def plot_summary(self, start_time, end_time, bin_width=5):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        data = self.db.read_data(start_time, end_time)
        wpm_values = [val for _, val in data if val is not None]

        if not wpm_values:
            ax.set_title("No data available")
            self.canvas.draw()
            return

        bins = np.arange(min(wpm_values), max(wpm_values) + bin_width, bin_width)
        counts, bin_edges = np.histogram(wpm_values, bins=bins)

        percentages = (counts / sum(counts)) * 100
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        ax.bar(bin_centers, percentages, width=bin_width,
               color='darkgreen', alpha=0.7, align='center')

        x_min, x_max = min(wpm_values), max(wpm_values)
        x_pad = (x_max - x_min) * 0.1
        ax.set_xlim(x_min - x_pad, x_max + x_pad)

        ax.set_title("WPM Distribution", fontsize=13, fontweight='bold')
        ax.set_xlabel("WPM")
        ax.set_ylabel("Percentage (%)")
        ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')
        ax.set_ylim(0, max(percentages) * 1.1)

        self.canvas.figure.tight_layout()
        self.canvas.draw()