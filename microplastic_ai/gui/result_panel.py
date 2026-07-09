"""
Result panel with tabs for statistics, detection, plots, and reports.
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
import numpy as np
from typing import Optional, Dict, Any


class ResultPanel(ttk.Frame):
    """Right panel with notebook tabs for all results."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=2, pady=2)

        # Create tabs
        self.stats_tab = ttk.Frame(self.notebook)
        self.detection_tab = ttk.Frame(self.notebook)
        self.hist_tab = ttk.Frame(self.notebook)
        self.heatmap_tab = ttk.Frame(self.notebook)
        self.scatter_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.detection_tab, text="Detection")
        self.notebook.add(self.hist_tab, text="Histograms")
        self.notebook.add(self.heatmap_tab, text="Heatmap")
        self.notebook.add(self.scatter_tab, text="Scatter")
        self.notebook.add(self.reports_tab, text="Reports")

        self._build_stats_tab()

    def _build_stats_tab(self):
        """Build the statistics grid."""
        frame = self.stats_tab
        self.stats_labels = {}
        stat_fields = [
            ("Total Particles", "total"),
            ("Coverage", "coverage"),
            ("Particle Density", "density"),
            ("Average Area (px²)", "avg_area"),
            ("Average Diameter (px)", "avg_diam"),
            ("Average Confidence", "avg_conf"),
            ("Largest Particle", "largest"),
            ("Smallest Particle", "smallest"),
            ("Std. Dev. Area", "std_area"),
        ]
        for i, (label, key) in enumerate(stat_fields):
            row, col = divmod(i, 2)
            ttk.Label(frame, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(
                row=row, column=col*2, sticky="e", padx=5, pady=2
            )
            self.stats_labels[key] = ttk.Label(frame, text="—", font=("Segoe UI", 10))
            self.stats_labels[key].grid(row=row, column=col*2+1, sticky="w", padx=5, pady=2)

    def update_statistics(self, stats: Dict[str, Any]) -> None:
        """Update statistics labels from a dictionary."""
        if stats is None:
            return
        mapping = {
            "total": stats.get("total_particles", 0),
            "coverage": f"{stats.get('coverage_percentage', 0):.2f} %",
            "density": f"{stats.get('particle_density_per_pixel', 0):.6f}",
            "avg_area": f"{stats.get('average_area', 0):.1f}",
            "avg_diam": f"{stats.get('average_equivalent_diameter', 0):.2f}",
            "avg_conf": f"{stats.get('average_confidence', 0):.3f}",
            "largest": f"{stats.get('largest_particle', 0)}",
            "smallest": f"{stats.get('smallest_particle', 0)}",
            "std_area": f"{stats.get('std_area', 0):.1f}",
        }
        for key, value in mapping.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))

    def _clear_tab(self, tab):
        for child in tab.winfo_children():
            child.destroy()

    def display_detection(self, image: np.ndarray) -> None:
        """Display detection result image in the Detection tab."""
        self._clear_tab(self.detection_tab)
        if image is None:
            return
        if image.ndim == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.imshow(image)
        ax.axis("off")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.detection_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_histogram(self, fig: Figure) -> None:
        self._clear_tab(self.hist_tab)
        canvas = FigureCanvasTkAgg(fig, master=self.hist_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_heatmap(self, fig: Figure) -> None:
        self._clear_tab(self.heatmap_tab)
        canvas = FigureCanvasTkAgg(fig, master=self.heatmap_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_scatter(self, fig: Figure) -> None:
        self._clear_tab(self.scatter_tab)
        canvas = FigureCanvasTkAgg(fig, master=self.scatter_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_reports(self, report_dir: str) -> None:
        """Show report links in the Reports tab."""
        self._clear_tab(self.reports_tab)
        frame = self.reports_tab
        ttk.Label(frame, text="Generated Reports", font=("Segoe UI", 12, "bold")).pack(pady=10)
        report_files = ["report.html", "report.json", "analysis_summary.csv", "metadata.json"]
        for fname in report_files:
            btn = ttk.Button(frame, text=f"Open {fname}", command=lambda f=fname: self._open_report(report_dir, f))
            btn.pack(pady=2)

    def _open_report(self, report_dir, filename):
        import subprocess
        import sys
        import os
        path = os.path.join(report_dir, filename)
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.run(["xdg-open", path], check=False)