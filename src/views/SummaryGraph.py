from datetime import datetime

import numpy as np
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QHBoxLayout, QComboBox, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.views.TimeRangeSlider import TimeRangeSlider
from src.views.ToggleDarkmodeButton import ToggleDarkmodeButton
from src.utils import apply_dark_theme, apply_light_theme


class SummaryGraph(QFrame):
    def __init__(self, main, db):
        super().__init__()
        self.db = db
        self.main_window = main
        self.color = '#537575' if main.dark_mode else 'steelblue'

        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        controls = QWidget()
        controls_layout = QHBoxLayout()

        # workaround to remove autofocus
        dummy = QWidget()
        dummy.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        dummy.setFixedWidth(0)
        controls_layout.addWidget(dummy)

        self.toggle = ToggleDarkmodeButton(self.main_window)
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

        self.main_window.modeToggled.connect(self.apply_style)

        self.start_time, self.end_time = self.slider.get_interval()
        self.title_from = datetime.fromtimestamp(self.start_time).strftime("%H:%M")
        self.title_to = datetime.fromtimestamp(self.end_time).strftime("%H:%M")

        # initial plot and theme setting
        self.apply_style()

        timer = QTimer(self)
        timer.timeout.connect(self.plot_summary)
        timer.start(500)

    def apply_style(self):
        if self.main_window.dark_mode:
            self.label_selection.setStyleSheet("background: #0a3b3b; color: #eceff4;")
            self.slider.apply_dark_theme()
            self.color = '#537575'
        else:
            self.label_selection.setStyleSheet("background: #cbe7e3; color: black;")
            self.slider.apply_light_theme()
            self.color = 'steelblue'

        self.toggle.setIcon()
        self.plot_summary()

    def set_interval(self, start, end):
        self.start_time = start
        self.end_time = end
        current = self.label_selection.currentText()
        if current == "day":
            self.title_from = datetime.fromtimestamp(start).strftime("%H:%M")
            self.title_to = datetime.fromtimestamp(end).strftime("%H:%M")
        else:
            self.title_from = datetime.fromtimestamp(start).strftime("%d %b %Y")
            self.title_to = datetime.fromtimestamp(end).strftime("%d %b %Y")

    def plot_summary(self, bin_width=5):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        data = self.db.read_data(self.start_time, self.end_time)
        wpm_values = [val for _, val in data if val is not None]

        if len(set(wpm_values)) <= 1:
            ax.set_title("Not enough data available")

        else:
            bins = np.arange(min(wpm_values), max(wpm_values) + bin_width, bin_width)
            counts, bin_edges = np.histogram(wpm_values, bins=bins)

            percentages = (counts / sum(counts)) * 100
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            ax.bar(bin_centers, percentages, width=bin_width,
                   color=self.color, alpha=0.7, align='center')

            x_min, x_max = min(wpm_values), max(wpm_values)
            x_pad = (x_max - x_min) * 0.1
            ax.set_xlim(x_min - x_pad, x_max + x_pad)

            ax.set_title(f"Distribution from {self.title_from} to {self.title_to}", fontsize=13, fontweight='bold')
            ax.set_xlabel("WPM")
            ax.set_ylabel("Percentage (%)")
            ax.grid(axis='y', alpha=0.6, linewidth=1.2, color='gray')
            ax.set_ylim(0, max(percentages) * 1.1)

        if self.main_window.dark_mode:
            apply_dark_theme(ax)
        else:
            apply_light_theme(ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()
