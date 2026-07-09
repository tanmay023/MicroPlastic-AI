"""
=========================================================
Visualization Engine for Microplastic Analysis
=========================================================
"""

import logging
import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Configuration
from microplastic_ai.config import (
    VISUALIZATION_DIR,
    FIGURE_DPI,
    FIGURE_FORMAT,
    HISTOGRAM_BINS,
    HEATMAP_KERNEL_SIZE,
    SCATTER_POINT_SIZE,
    FIG_SIZE,
    HIST_SIZE,
    USE_TIMESTAMP,
    DEFAULT_COLORMAP,
)

from microplastic_ai.analysis.particle_analysis import ParticleAnalyzer
from microplastic_ai.analysis.density_estimation import DensityEstimator

# Type alias
Color = tuple[int, int, int]

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Generate publication‑quality visualizations from particle analysis results.
    """

    def __init__(
        self,
        analyzer: ParticleAnalyzer,
        estimator: DensityEstimator,
        image: np.ndarray,
        output_dir: Optional[Path] = None,
        dpi: Optional[int] = None,
        figure_format: Optional[str] = None,
        histogram_bins: Optional[int] = None,
        heatmap_kernel: Optional[int] = None,
        scatter_size: Optional[int] = None,
        fig_size: Optional[Tuple[int, int]] = None,
        hist_size: Optional[Tuple[int, int]] = None,
        colormap: Optional[str] = None,
    ) -> None:
        """
        Args:
            analyzer: ParticleAnalyzer with detection results.
            estimator: DensityEstimator with computed density metrics.
            image: Original image (RGB or BGR; will be converted internally).
            output_dir: Directory to save all figures. Defaults to VISUALIZATION_DIR.
            dpi: Resolution for saved figures. Defaults to FIGURE_DPI.
            figure_format: File extension (e.g., 'png', 'svg'). Defaults to FIGURE_FORMAT.
            histogram_bins: Number of bins for histograms. Defaults to HISTOGRAM_BINS.
            heatmap_kernel: Kernel size for Gaussian blur (must be odd). Defaults to HEATMAP_KERNEL_SIZE.
            scatter_size: Marker size for scatter plots. Defaults to SCATTER_POINT_SIZE.
            fig_size: Size of main figures (width, height) in inches. Defaults to FIG_SIZE.
            hist_size: Size of histogram figures. Defaults to HIST_SIZE.
            colormap: Colormap for heatmap and scatter. Defaults to DEFAULT_COLORMAP.
        """
        self.analyzer = analyzer
        self.estimator = estimator
        self.original_image = image.copy()
        self.image = self._prepare_image(image)

        self.height, self.width = self.image.shape[:2]

        # Resolve output directory with optional timestamp
        base_dir = output_dir or VISUALIZATION_DIR
        if USE_TIMESTAMP:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            self.output_dir = base_dir / date_str
        else:
            self.output_dir = base_dir

        self.dpi = dpi or FIGURE_DPI
        self.figure_format = figure_format or FIGURE_FORMAT
        self.histogram_bins = histogram_bins or HISTOGRAM_BINS
        self.heatmap_kernel = heatmap_kernel or HEATMAP_KERNEL_SIZE
        self.scatter_size = scatter_size or SCATTER_POINT_SIZE
        self.fig_size = fig_size or FIG_SIZE
        self.hist_size = hist_size or HIST_SIZE
        self.colormap = colormap or DEFAULT_COLORMAP

        # Ensure the kernel is odd
        if self.heatmap_kernel % 2 == 0:
            self.heatmap_kernel += 1

        self._ensure_output_dir()
        self._set_publication_style()

        self._figure_counter = 1
        logger.info(f"VisualizationEngine initialized. Output: {self.output_dir}")

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        """Convert image to RGB (if BGR) and store a copy for drawing."""
        if image.ndim == 3 and image.shape[2] == 3:
            # Assume BGR (OpenCV default) -> convert to RGB for matplotlib
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image.copy()

    def _ensure_output_dir(self) -> None:
        """Create the output directory if it does not exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _set_publication_style(self) -> None:
        """Set matplotlib defaults for publication‑quality figures."""
        plt.rcParams.update({
            "font.size": 12,
            "figure.dpi": self.dpi,
            "axes.labelsize": 12,
            "axes.titlesize": 14,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "figure.titlesize": 16,
        })

    def _save_figure(self, fig: Figure, name: str) -> Path:
        """Save a matplotlib figure with automatic numbering and publication settings."""
        numbered_name = f"{self._figure_counter:02d}_{name}"
        self._figure_counter += 1
        path = self.output_dir / f"{numbered_name}.{self.figure_format}"
        fig.savefig(path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.debug(f"Saved figure: {path}")
        return path

    def _save_opencv_image(self, img: np.ndarray, name: str) -> Path:
        """Save an OpenCV image (BGR) directly to disk."""
        numbered_name = f"{self._figure_counter:02d}_{name}"
        self._figure_counter += 1
        path = self.output_dir / f"{numbered_name}.{self.figure_format}"
        # OpenCV expects BGR; our image is RGB, so convert if needed.
        if img.ndim == 3 and img.shape[2] == 3:
            bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            bgr = img
        cv2.imwrite(str(path), bgr, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        logger.debug(f"Saved OpenCV image: {path}")
        return path

    def has_particles(self) -> bool:
        """Return True if there are any detected particles."""
        return len(self.analyzer) > 0

    # ----------------------------------------------------------------------
    # Phase 1: Core visualizations
    # ----------------------------------------------------------------------

    def draw_bounding_boxes(
        self,
        show_labels: bool = True,
        color: Color = (0, 255, 0),
        thickness: int = 2,
    ) -> Path:
        """
        Draw bounding boxes around all detected particles on the original image.
        Saves as a raw image (OpenCV) for maximum quality.

        Args:
            show_labels: If True, display class name and confidence above the box.
            color: RGB tuple for the box.
            thickness: Line thickness.

        Returns:
            Path to the saved image.
        """
        img = self.image.copy()  # RGB

        for particle in self.analyzer:
            x1, y1, x2, y2 = particle.x1, particle.y1, particle.x2, particle.y2
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            if show_labels:
                label = f"{particle.class_name} {particle.confidence:.2f}"
                cv2.putText(
                    img,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA,
                )

        return self._save_opencv_image(img, "bounding_boxes")

    def draw_particle_centers(
        self,
        marker: str = "o",
        color: Color = (255, 0, 0),
        size: Optional[int] = None,
    ) -> Path:
        """
        Draw the center points of all particles on the image (matplotlib).

        Args:
            marker: Matplotlib marker style.
            color: RGB tuple (0-255).
            size: Marker size; defaults to SCATTER_POINT_SIZE.

        Returns:
            Path to the saved figure.
        """
        size = size or self.scatter_size
        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.imshow(self.image)

        centers_x = [p.center_x for p in self.analyzer]
        centers_y = [p.center_y for p in self.analyzer]
        # Convert color to [0,1] for matplotlib
        c_norm = tuple(c / 255 for c in color)
        ax.scatter(centers_x, centers_y, c=[c_norm], s=size, marker=marker, alpha=0.8)

        ax.set_title("Particle Centers")
        ax.axis("off")
        return self._save_figure(fig, "particle_centers")

    # ----------------------------------------------------------------------
    # Phase 2: Histograms
    # ----------------------------------------------------------------------

    def plot_area_histogram(self) -> Path:
        return self._plot_histogram(
            data=[p.area for p in self.analyzer],
            title="Particle Area Distribution",
            xlabel="Area (px²)",
            ylabel="Count",
            filename="area_histogram",
        )

    def plot_width_histogram(self) -> Path:
        return self._plot_histogram(
            data=[p.width for p in self.analyzer],
            title="Particle Width Distribution",
            xlabel="Width (px)",
            ylabel="Count",
            filename="width_histogram",
        )

    def plot_height_histogram(self) -> Path:
        return self._plot_histogram(
            data=[p.height for p in self.analyzer],
            title="Particle Height Distribution",
            xlabel="Height (px)",
            ylabel="Count",
            filename="height_histogram",
        )

    def plot_confidence_histogram(self) -> Path:
        return self._plot_histogram(
            data=[p.confidence for p in self.analyzer],
            title="Confidence Distribution",
            xlabel="Confidence",
            ylabel="Count",
            filename="confidence_histogram",
        )

    def plot_equivalent_diameter(self) -> Path:
        return self._plot_histogram(
            data=[p.equivalent_diameter for p in self.analyzer],
            title="Equivalent Diameter Distribution",
            xlabel="Diameter (px)",
            ylabel="Count",
            filename="equivalent_diameter",
        )

    def plot_aspect_ratio(self) -> Path:
        return self._plot_histogram(
            data=[p.aspect_ratio for p in self.analyzer],
            title="Aspect Ratio Distribution",
            xlabel="Aspect Ratio (width/height)",
            ylabel="Count",
            filename="aspect_ratio",
        )

    def _plot_histogram(
        self,
        data: list,
        title: str,
        xlabel: str,
        ylabel: str,
        filename: str,
        color: str = "blue",
        mean_line: bool = True,
        grid: bool = True,
    ) -> Path:
        """
        Generic histogram plotter with optional mean line and grid.

        Args:
            data: List of values.
            title, xlabel, ylabel: Axis labels.
            filename: Base filename (without extension).
            color: Histogram colour.
            mean_line: If True, draw a vertical line at the mean.
            grid: If True, show grid.
        """
        fig, ax = plt.subplots(figsize=self.hist_size)

        if not data:
            ax.text(0.5, 0.5, "No particles to display", ha="center", va="center", fontsize=14)
            ax.set_title(title)
            return self._save_figure(fig, filename)

        ax.hist(data, bins=self.histogram_bins, edgecolor="black", alpha=0.7, color=color)

        if mean_line and data:
            mean_val = np.mean(data)
            ax.axvline(mean_val, color="red", linestyle="--", linewidth=2, label=f"Mean = {mean_val:.2f}")
            ax.legend()

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if grid:
            ax.grid(True, linestyle="--", alpha=0.5)

        return self._save_figure(fig, filename)

    # ----------------------------------------------------------------------
    # Phase 3: Research‑grade visualizations
    # ----------------------------------------------------------------------

    def plot_density_heatmap(
        self,
        colormap: Optional[str] = None,
        alpha: float = 0.6,
        blur_radius: Optional[int] = None,
        spread_radius: int = 3,
    ) -> Path:
        """
        Generate a density heatmap using Gaussian blur over particle centers,
        weighted by confidence and spread with circles.

        Args:
            colormap: Matplotlib colormap name; defaults to self.colormap.
            alpha: Transparency of the heatmap overlay.
            blur_radius: Kernel size; defaults to HEATMAP_KERNEL_SIZE.
            spread_radius: Radius (in pixels) for confidence spreading via cv2.circle.

        Returns:
            Path to the saved figure.
        """
        colormap = colormap or self.colormap

        if not self.has_particles():
            fig, ax = plt.subplots(figsize=self.fig_size)
            ax.imshow(self.image)
            ax.set_title("Density Heatmap (no particles)")
            ax.axis("off")
            return self._save_figure(fig, "density_heatmap")

        h, w = self.image.shape[:2]
        mask = np.zeros((h, w), dtype=np.float32)

        for p in self.analyzer:
            x, y = int(round(p.center_x)), int(round(p.center_y))
            if 0 <= x < w and 0 <= y < h:
                # Spread confidence using a filled circle
                cv2.circle(mask, (x, y), spread_radius, p.confidence, -1)

        # Normalise to [0,255] for OpenCV
        if mask.max() > 0:
            mask = (mask / mask.max()) * 255
        mask = mask.astype(np.uint8)

        # Apply Gaussian blur
        kernel = blur_radius or self.heatmap_kernel
        if kernel % 2 == 0:
            kernel += 1
        heatmap = cv2.GaussianBlur(mask, (kernel, kernel), 0)

        # Normalize to [0,1]
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        # FIX: Use plt.get_cmap instead of plt.cm.get_cmap
        cmap = plt.get_cmap(colormap)
        heatmap_colored = cmap(heatmap)[:, :, :3]  # RGB only

        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.imshow(self.image)
        ax.imshow(heatmap_colored, alpha=alpha, interpolation="bilinear")
        ax.set_title("Density Heatmap (Confidence‑Weighted, Spread)")
        ax.axis("off")
        return self._save_figure(fig, "density_heatmap")

    def plot_particle_distribution(self) -> Path:
        """
        Scatter plot of particle centers: size ∝ area, color ∝ confidence.
        Y‑axis is inverted to match image coordinates.

        Returns:
            Path to the saved figure.
        """
        if not self.has_particles():
            fig, ax = plt.subplots(figsize=self.fig_size)
            ax.text(0.5, 0.5, "No particles to display", ha="center", va="center", fontsize=14)
            ax.set_title("Particle Distribution")
            return self._save_figure(fig, "particle_distribution")

        fig, ax = plt.subplots(figsize=self.fig_size)
        centers_x = [p.center_x for p in self.analyzer]
        centers_y = [p.center_y for p in self.analyzer]
        areas = [p.area for p in self.analyzer]
        confidences = [p.confidence for p in self.analyzer]

        max_area = max(areas) if areas else 1
        sizes = [self.scatter_size * (a / max_area + 0.3) for a in areas]

        sc = ax.scatter(
            centers_x,
            centers_y,
            s=sizes,
            c=confidences,
            cmap=self.colormap,
            alpha=0.8,
            edgecolors="black",
            linewidth=0.5,
        )
        ax.set_title("Particle Distribution (size ∝ area, color ∝ confidence)")
        ax.set_xlabel("X (pixels)")
        ax.set_ylabel("Y (pixels)")
        ax.invert_yaxis()  # Match image coordinates
        ax.grid(True, linestyle="--", alpha=0.3)
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label("Confidence")
        return self._save_figure(fig, "particle_distribution")

    # ----------------------------------------------------------------------
    # Phase 4: Automated batch export
    # ----------------------------------------------------------------------

    def save_all(self) -> Dict[str, Path]:
        """
        Generate and save all visualizations, printing/logging the list of generated files.

        Returns:
            Dictionary mapping visualization name to file path.
        """
        self._figure_counter = 1
        result = {
            "bounding_boxes": self.draw_bounding_boxes(),
            "particle_centers": self.draw_particle_centers(),
            "area_histogram": self.plot_area_histogram(),
            "width_histogram": self.plot_width_histogram(),
            "height_histogram": self.plot_height_histogram(),
            "confidence_histogram": self.plot_confidence_histogram(),
            "equivalent_diameter": self.plot_equivalent_diameter(),
            "aspect_ratio": self.plot_aspect_ratio(),
            "density_heatmap": self.plot_density_heatmap(),
            "particle_distribution": self.plot_particle_distribution(),
        }

        logger.info(f"Generated {len(result)} visualizations in {self.output_dir}")
        for name, path in result.items():
            logger.info(f"   - {path.name}")
        return result

    def collect_visualizations(self) -> List[Path]:
        """
        Scan the output directory for image files and return sorted list.
        Supports .png, .jpg, .jpeg.
        """
        vis_dir = self.output_dir
        if not vis_dir.exists():
            return []
        extensions = ("*.png", "*.jpg", "*.jpeg")
        files = []
        for ext in extensions:
            files.extend(vis_dir.glob(ext))
        return sorted(files)

    # ----------------------------------------------------------------------
    # Special methods
    # ----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"VisualizationEngine("
            f"particles={len(self.analyzer)}, "
            f"image={self.width}x{self.height}, "
            f"dpi={self.dpi}, "
            f"format='{self.figure_format}')"
        )