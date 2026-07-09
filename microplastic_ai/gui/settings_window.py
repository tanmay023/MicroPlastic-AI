"""
Settings window with persistence to settings.json.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import json
from pathlib import Path

from microplastic_ai.config import (
    CONFIDENCE_THRESHOLD,
    OUTPUT_DIR,
    SAVE_OUTPUTS,
    FIGURE_DPI,
)


class SettingsWindow:
    """Dialog for user settings, saved to settings.json."""

    SETTINGS_FILE = Path(__file__).parent.parent / "config" / "settings.json"

    def __init__(self, parent):
        self.parent = parent
        self.settings = self._load_settings()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("480x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self._build_ui()
        self._load_values()

    def _load_settings(self):
        if self.SETTINGS_FILE.exists():
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_settings(self):
        self.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def _build_ui(self):
        main = ttk.Frame(self.dialog, padding=20)
        main.pack(fill="both", expand=True)

        # Confidence threshold
        ttk.Label(main, text="Confidence Threshold:").grid(row=0, column=0, sticky="w", pady=5)
        self.conf_var = tk.DoubleVar(value=self.settings.get("confidence", CONFIDENCE_THRESHOLD))
        scale = ttk.Scale(main, from_=0.0, to=1.0, variable=self.conf_var, orient="horizontal", length=200)
        scale.grid(row=0, column=1, padx=10, pady=5)
        self.conf_label = ttk.Label(main, text=f"{self.conf_var.get():.2f}")
        self.conf_label.grid(row=0, column=2, padx=5)
        self.conf_var.trace("w", lambda *args: self.conf_label.config(text=f"{self.conf_var.get():.2f}"))

        # Output folder
        ttk.Label(main, text="Output Folder:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_var = tk.StringVar(value=self.settings.get("output_dir", str(OUTPUT_DIR)))
        entry = ttk.Entry(main, textvariable=self.output_var, width=25)
        entry.grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(main, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=5)

        # Save outputs
        self.save_var = tk.BooleanVar(value=self.settings.get("save_outputs", SAVE_OUTPUTS))
        ttk.Checkbutton(main, text="Save Visualizations & Reports", variable=self.save_var).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=5
        )

        # DPI
        ttk.Label(main, text="Figure DPI:").grid(row=3, column=0, sticky="w", pady=5)
        self.dpi_var = tk.IntVar(value=self.settings.get("dpi", FIGURE_DPI))
        ttk.Entry(main, textvariable=self.dpi_var, width=10).grid(row=3, column=1, sticky="w", padx=10)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=20)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side="left", padx=5)

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)

    def _load_values(self):
        pass

    def _save(self):
        self.settings["confidence"] = self.conf_var.get()
        self.settings["output_dir"] = self.output_var.get()
        self.settings["save_outputs"] = self.save_var.get()
        self.settings["dpi"] = self.dpi_var.get()
        self._save_settings()
        self.dialog.destroy()