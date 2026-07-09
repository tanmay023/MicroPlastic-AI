"""
Styles and themes for the MicroPlastic‑AI GUI.
"""

import tkinter as tk
from tkinter import ttk

DARK_BG = "#2b2b2b"
DARK_FG = "#eeeeee"
DARK_SELECT = "#404040"
DARK_HIGHLIGHT = "#3a7bd5"
DARK_ENTRY_BG = "#3c3c3c"
DARK_ENTRY_FG = "#ffffff"
DARK_BUTTON_BG = "#3a7bd5"
DARK_BUTTON_FG = "#ffffff"

LIGHT_BG = "#f0f0f0"
LIGHT_FG = "#000000"
LIGHT_SELECT = "#c0c0c0"
LIGHT_HIGHLIGHT = "#0078d7"
LIGHT_ENTRY_BG = "#ffffff"
LIGHT_ENTRY_FG = "#000000"
LIGHT_BUTTON_BG = "#e0e0e0"
LIGHT_BUTTON_FG = "#000000"


def apply_dark_theme(root: tk.Tk) -> None:
    """Apply a dark theme to the entire application."""
    root.tk_setPalette(
        background=DARK_BG,
        foreground=DARK_FG,
        selectColor=DARK_SELECT,
        highlightColor=DARK_HIGHLIGHT,
    )
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TFrame",
        background=DARK_BG,
        foreground=DARK_FG,
    )
    style.configure(
        "TLabel",
        background=DARK_BG,
        foreground=DARK_FG,
    )
    style.configure(
        "TButton",
        background=DARK_BUTTON_BG,
        foreground=DARK_BUTTON_FG,
        borderwidth=1,
        focuscolor="none",
    )
    style.map(
        "TButton",
        background=[("active", "#4a8bd5"), ("pressed", "#2a6bb5")],
        foreground=[("active", "white"), ("pressed", "white")],
    )
    style.configure(
        "TEntry",
        fieldbackground=DARK_ENTRY_BG,
        foreground=DARK_ENTRY_FG,
    )
    style.configure(
        "TNotebook.Tab",
        background=DARK_BG,
        foreground=DARK_FG,
        padding=[8, 4],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", DARK_SELECT)],
        foreground=[("selected", DARK_FG)],
    )
    style.configure(
        "Treeview",
        background=DARK_BG,
        foreground=DARK_FG,
        fieldbackground=DARK_BG,
    )
    style.map(
        "Treeview",
        background=[("selected", DARK_SELECT)],
    )


def apply_light_theme(root: tk.Tk) -> None:
    """Apply a light theme."""
    root.tk_setPalette(
        background=LIGHT_BG,
        foreground=LIGHT_FG,
        selectColor=LIGHT_SELECT,
        highlightColor=LIGHT_HIGHLIGHT,
    )
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TFrame",
        background=LIGHT_BG,
        foreground=LIGHT_FG,
    )
    style.configure(
        "TLabel",
        background=LIGHT_BG,
        foreground=LIGHT_FG,
    )
    style.configure(
        "TButton",
        background=LIGHT_BUTTON_BG,
        foreground=LIGHT_BUTTON_FG,
        borderwidth=1,
        focuscolor="none",
    )
    style.map(
        "TButton",
        background=[("active", "#d0d0d0"), ("pressed", "#c0c0c0")],
    )
    style.configure(
        "TEntry",
        fieldbackground=LIGHT_ENTRY_BG,
        foreground=LIGHT_ENTRY_FG,
    )
    style.configure(
        "TNotebook.Tab",
        background=LIGHT_BG,
        foreground=LIGHT_FG,
        padding=[8, 4],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", LIGHT_SELECT)],
        foreground=[("selected", LIGHT_FG)],
    )
    style.configure(
        "Treeview",
        background=LIGHT_BG,
        foreground=LIGHT_FG,
        fieldbackground=LIGHT_BG,
    )
    style.map(
        "Treeview",
        background=[("selected", LIGHT_SELECT)],
    )