"""
About window with detailed system information.
"""

import tkinter as tk
from tkinter import ttk
import platform
import sys
import torch
import cv2
import ultralytics

from microplastic_ai.config import MODEL_NAME


class AboutWindow:
    """About dialog displaying project and system information."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About MicroPlastic-AI")
        self.dialog.geometry("420x380")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        main = ttk.Frame(self.dialog, padding=20)
        main.pack(fill="both", expand=True)

        # Project info
        ttk.Label(main, text="MicroPlastic-AI", font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(main, text="YOLO11-based microplastic particle analysis", font=("Segoe UI", 10)).pack(pady=2)
        ttk.Label(main, text="Version 1.0", font=("Segoe UI", 9)).pack(pady=2)
        ttk.Label(main, text=f"Model: {MODEL_NAME}", font=("Segoe UI", 9)).pack(pady=2)

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=10)

        # System info
        info_frame = ttk.Frame(main)
        info_frame.pack(fill="x", pady=5)

        try:
            gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
        except Exception:
            gpu_name = "Unknown"

        sys_info = (
            f"Python: {sys.version.split()[0]}\n"
            f"OpenCV: {cv2.__version__}\n"
            f"Ultralytics: {ultralytics.__version__}\n"
            f"PyTorch: {torch.__version__ if torch else 'N/A'}\n"
            f"CUDA: {torch.version.cuda if torch and torch.cuda.is_available() else 'Not available'}\n"
            f"GPU: {gpu_name}\n"
            f"Platform: {platform.system()} {platform.release()}"
        )
        info_label = ttk.Label(info_frame, text=sys_info, font=("Segoe UI", 9), justify="left")
        info_label.pack(anchor="w")

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=10)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Copy System Info", command=lambda: self._copy_sys_info(sys_info)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side="right", padx=5)

        ttk.Label(main, text="© 2026 MicroPlastic-AI", font=("Segoe UI", 8)).pack(pady=10)

    def _copy_sys_info(self, info: str):
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(info)