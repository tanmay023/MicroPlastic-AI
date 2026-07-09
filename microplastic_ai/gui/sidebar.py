"""
Sidebar panel with action buttons.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class Sidebar(ttk.Frame):
    """Left sidebar with buttons for main actions."""

    def __init__(
        self,
        parent,
        on_open_image: Callable,
        on_open_folder: Callable,
        on_analyze: Callable,
        on_generate_report: Callable,
        on_show_settings: Callable,
        on_exit: Callable,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.on_open_image = on_open_image
        self.on_open_folder = on_open_folder
        self.on_analyze = on_analyze
        self.on_generate_report = on_generate_report
        self.on_show_settings = on_show_settings
        self.on_exit = on_exit

        self._create_widgets()
        self.set_model_loaded(False)

    def _create_widgets(self):
        ttk.Label(self, text="MicroPlastic-AI", font=("Segoe UI", 14, "bold")).pack(
            pady=(15, 25), padx=10
        )

        self.btn_open = ttk.Button(self, text="📂 Open Image", command=self.on_open_image, width=18)
        self.btn_open.pack(pady=5, padx=10)

        self.btn_folder = ttk.Button(self, text="📁 Open Folder", command=self.on_open_folder, width=18)
        self.btn_folder.pack(pady=5, padx=10)

        self.btn_analyze = ttk.Button(self, text="▶ Analyze", command=self.on_analyze, width=18)
        self.btn_analyze.pack(pady=5, padx=10)

        self.btn_report = ttk.Button(self, text="📊 Generate Report", command=self.on_generate_report, width=18)
        self.btn_report.pack(pady=5, padx=10)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15, padx=10)

        self.btn_settings = ttk.Button(self, text="⚙ Settings", command=self.on_show_settings, width=18)
        self.btn_settings.pack(pady=5, padx=10)

        self.btn_exit = ttk.Button(self, text="❌ Exit", command=self.on_exit, width=18)
        self.btn_exit.pack(pady=5, padx=10)

        self.status_label = ttk.Label(self, text="Ready", font=("Segoe UI", 9), wraplength=150)
        self.status_label.pack(side="bottom", pady=15, padx=10)

    def set_model_loaded(self, loaded: bool) -> None:
        """Enable/disable analysis and report buttons based on model status."""
        state = "normal" if loaded else "disabled"
        self.btn_analyze.config(state=state)
        self.btn_report.config(state=state)

    def set_status(self, message: str) -> None:
        """Update the status label."""
        self.status_label.config(text=message)