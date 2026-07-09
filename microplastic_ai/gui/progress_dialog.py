"""
Progress dialog with stage messages and progress steps.
"""

import tkinter as tk
from tkinter import ttk


class ProgressDialog:
    """Modal progress dialog with message and progress bar."""

    def __init__(self, parent, title="Processing", message="Please wait...", total_stages=None):
        self.parent = parent
        self.cancelled = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x140")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.message_label = ttk.Label(self.dialog, text=message, font=("Segoe UI", 10))
        self.message_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.dialog, mode="determinate", length=400, maximum=100)
        self.progress.pack(pady=5)
        self.progress["value"] = 0

        self.cancel_btn = ttk.Button(self.dialog, text="Cancel", command=self.on_cancel)
        self.cancel_btn.pack(pady=5)

        self.total_stages = total_stages
        self.current_stage = 0

    def update(self, message: str, value: int = None, stage: int = None, total_stages: int = None):
        """Update message and progress value (0-100), optionally with stage/total."""
        if total_stages is not None:
            self.total_stages = total_stages
        if stage is not None and self.total_stages is not None:
            self.current_stage = stage
            message = f"{message} ({stage}/{self.total_stages})"
        self.message_label.config(text=message)
        if value is not None:
            self.progress["value"] = value
        self.dialog.update_idletasks()

    def on_cancel(self):
        self.cancelled = True
        self.dialog.destroy()

    def close(self):
        self.dialog.destroy()

    def is_cancelled(self):
        return self.cancelled