from datetime import datetime

import numpy as np
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QHBoxLayout, QComboBox, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.views.TimeRangeSlider import TimeRangeSlider
from src.views.ToggleDarkmodeButton import ToggleDarkmodeButton
from src.utils import apply_dark_theme

class SummaryGraph(QFrame):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        controls = QWidget()
        controls_layout = QHBoxLayout()

        # workaround to remove autofocus
        dummy = QWidget()
        dummy.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        dummy.setFixedWidth(0)
        controls_layout.addWidget(dummy)

        self.toggle = ToggleDarkmodeButton()
        controls_layout.addWidget(self.toggle)

        self.slider = TimeRangeSlider()
        self.slider.rangeChanged.connect(self.set_interval)

        self.label_selection = QComboBox()
        self.label_selection.addItems(["day", "month", "year"])
        self.label_selection.currentTextChanged.connect(self.slider.update_format)

        controls_layout.addWidget(self.label_selection)
        controls_layout.addWidget(self.slider)
        controls.setLayout(controls_layout)
        controls.setFixedHeight(80)
        controls.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(controls)

        self.canvas = FigureCanvas(Figure(figsize=(8, 4)))
        self.canvas.setMaximumHeight(500)
        layout.addWidget(self.canvas)

        self.start_time, self.end_time = self.slider.get_interval()
        self.title_from = datetime.fromtimestamp(self.start_time).strftime("%H:%M")
        self.title_to = datetime.fromtimestamp(self.end_time).strftime("%H:%M")

        timer = QTimer(self)
        timer.timeout.connect(self.plot_summary)
        timer.start(500)



        # initial plot
        self.plot_summary()

    def set_interval(self, start, end):
        self.start_time = start
        self.end_time = end
        current = self.label_selection.currentText()
        if current == "today":
            self.title_from = datetime.fromtimestamp(start).strftime("%H:%M")
            self.title_to = datetime.fromtimestamp(end).strftime("%H:%M")
        elif current == "last year":
            self.title_from = datetime.fromtimestamp(start).strftime("%d %b %Y")
            self.title_to = datetime.fromtimestamp(end).strftime("%d %b %Y")

    def plot_summary(self, bin_width=5):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        data = self.db.read_data(self.start_time, self.end_time)
        wpm_values = [val for _, val in data if val is not None]

        if not wpm_values:
            ax.set_title("No data available")
            self.canvas.draw_idle()
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

        ax.set_title(f"Distribution from {self.title_from} to {self.title_to}", fontsize=13, fontweight='bold')
        ax.set_xlabel("WPM")
        ax.set_ylabel("Percentage (%)")
        ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')
        ax.set_ylim(0, max(percentages) * 1.1)

        apply_dark_theme(ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()