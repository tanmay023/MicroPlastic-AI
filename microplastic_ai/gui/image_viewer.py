"""
High-performance image viewer with correct viewport model, zoom, pan, and keyboard shortcuts.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class ImageViewer(ttk.Frame):
    """Optimised image viewer with viewport-based rendering."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.image = None          # Original BGR numpy array
        self.tk_image = None
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Viewport state
        self.zoom = 1.0
        self.view_x = 0.0   # top-left corner of visible region in image coords
        self.view_y = 0.0

        # Image dimensions (original)
        self.orig_w = 0
        self.orig_h = 0

        # Mouse position label
        self.mouse_label = ttk.Label(self, text="X: 0  Y: 0", font=("Segoe UI", 9))
        self.mouse_label.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

        # Bind events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-3>", self._reset_view)
        self.canvas.bind("<Double-Button-1>", self._fit_to_window)
        self.canvas.bind("<Motion>", self._on_mouse_move)

        # Keyboard shortcuts (bound to canvas, not globally)
        self.canvas.focus_set()
        self.canvas.bind("<Control-plus>", lambda e: self._zoom_in())
        self.canvas.bind("<Control-equal>", lambda e: self._zoom_in())
        self.canvas.bind("<Control-minus>", lambda e: self._zoom_out())
        self.canvas.bind("<Control-0>", lambda e: self._reset_view())
        self.canvas.bind("<Control-f>", lambda e: self._fit_to_window())
        self.canvas.bind("<Control-s>", lambda e: self._save_image())

    def set_image(self, image: np.ndarray) -> None:
        """Set a new image (BGR numpy array)."""
        if image is None:
            self.image = None
            self.orig_w = self.orig_h = 0
            self.zoom = 1.0
            self.view_x = self.view_y = 0.0
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="No image loaded",
                fill="#666",
                font=("Segoe UI", 16),
            )
            self.mouse_label.config(text="X: 0  Y: 0")
            return

        self.image = image
        self.orig_h, self.orig_w = image.shape[:2]
        self.zoom = 1.0
        self.view_x = 0.0
        self.view_y = 0.0
        self._render()

    def _render(self) -> None:
        """Render the visible portion of the image."""
        if self.image is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        # Compute visible rectangle in image coordinates
        visible_w = canvas_w / self.zoom
        visible_h = canvas_h / self.zoom

        # Clamp to image bounds
        x1 = int(max(0, self.view_x))
        y1 = int(max(0, self.view_y))
        x2 = int(min(self.orig_w, self.view_x + visible_w))
        y2 = int(min(self.orig_h, self.view_y + visible_h))

        # If we're out of bounds, adjust view
        if x2 <= x1 or y2 <= y1:
            # fallback: show full image
            x1, y1, x2, y2 = 0, 0, self.orig_w, self.orig_h
            self.view_x = 0
            self.view_y = 0
            self.zoom = min(canvas_w / self.orig_w, canvas_h / self.orig_h, 10.0)

        # Crop the image
        crop = self.image[y1:y2, x1:x2]
        if crop.size == 0:
            return

        # Convert to PIL and resize to canvas size
        display_w = int((x2 - x1) * self.zoom)
        display_h = int((y2 - y1) * self.zoom)

        # Limit resizing to 2x canvas size for performance
        if display_w > canvas_w * 2:
            display_w = canvas_w * 2
        if display_h > canvas_h * 2:
            display_h = canvas_h * 2

        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        resized = pil_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        # Center the image on the canvas
        self.canvas.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=self.tk_image,
            anchor="center",
        )

    def _on_mousewheel(self, event):
        delta = 1.1 if event.delta > 0 else 0.9
        new_zoom = self.zoom * delta
        if 0.1 <= new_zoom <= 20.0:
            # Zoom towards mouse position
            mouse_x = event.x
            mouse_y = event.y
            # Image coordinates under mouse (before zoom)
            img_x = self.view_x + mouse_x / self.zoom
            img_y = self.view_y + mouse_y / self.zoom

            self.zoom = new_zoom
            # After zoom, set view so that the same image point is under mouse
            self.view_x = img_x - mouse_x / self.zoom
            self.view_y = img_y - mouse_y / self.zoom
            self._render()

    def _on_press(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.drag_start_view_x = self.view_x
        self.drag_start_view_y = self.view_y
        self.is_dragging = True

    def _on_drag(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.view_x = self.drag_start_view_x - dx / self.zoom
            self.view_y = self.drag_start_view_y - dy / self.zoom
            # Clamp to image bounds
            self.view_x = max(0, min(self.view_x, self.orig_w - self.canvas.winfo_width() / self.zoom))
            self.view_y = max(0, min(self.view_y, self.orig_h - self.canvas.winfo_height() / self.zoom))
            self._render()

    def _on_release(self, event):
        self.is_dragging = False

    def _reset_view(self, event=None):
        self.zoom = 1.0
        self.view_x = 0.0
        self.view_y = 0.0
        self._render()

    def _fit_to_window(self, event=None):
        if self.image is None:
            return
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return
        zoom_x = canvas_w / self.orig_w
        zoom_y = canvas_h / self.orig_h
        self.zoom = min(zoom_x, zoom_y, 10.0)
        self.view_x = 0.0
        self.view_y = 0.0
        self._render()

    def _on_resize(self, event):
        self._render()

    def _on_mouse_move(self, event):
        if self.image is None:
            self.mouse_label.config(text="X: 0  Y: 0")
            return
        # Convert canvas coordinates to image coordinates
        img_x = self.view_x + event.x / self.zoom
        img_y = self.view_y + event.y / self.zoom
        if 0 <= img_x < self.orig_w and 0 <= img_y < self.orig_h:
            self.mouse_label.config(text=f"X: {int(img_x)}  Y: {int(img_y)}")
        else:
            self.mouse_label.config(text="X: —  Y: —")

    def _zoom_in(self):
        self.zoom = min(20.0, self.zoom * 1.2)
        # Keep centre fixed
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cx = canvas_w / 2
        cy = canvas_h / 2
        img_center_x = self.view_x + cx / self.zoom
        img_center_y = self.view_y + cy / self.zoom
        self.view_x = img_center_x - cx / self.zoom
        self.view_y = img_center_y - cy / self.zoom
        self._render()

    def _zoom_out(self):
        self.zoom = max(0.1, self.zoom / 1.2)
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cx = canvas_w / 2
        cy = canvas_h / 2
        img_center_x = self.view_x + cx / self.zoom
        img_center_y = self.view_y + cy / self.zoom
        self.view_x = img_center_x - cx / self.zoom
        self.view_y = img_center_y - cy / self.zoom
        self._render()

    def _save_image(self):
        """Save the current viewport as an image."""
        if self.image is None:
            return
        filetypes = [("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        if not path:
            return

        # Render the current viewport into a PIL image
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        # Compute visible crop
        visible_w = canvas_w / self.zoom
        visible_h = canvas_h / self.zoom
        x1 = int(max(0, self.view_x))
        y1 = int(max(0, self.view_y))
        x2 = int(min(self.orig_w, self.view_x + visible_w))
        y2 = int(min(self.orig_h, self.view_y + visible_h))

        if x2 <= x1 or y2 <= y1:
            return

        crop = self.image[y1:y2, x1:x2]
        # Resize to canvas size
        display_w = int((x2 - x1) * self.zoom)
        display_h = int((y2 - y1) * self.zoom)
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        if display_w > 0 and display_h > 0:
            pil_img = pil_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
        pil_img.save(path)