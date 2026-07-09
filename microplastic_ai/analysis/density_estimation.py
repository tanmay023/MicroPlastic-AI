"""
=========================================================
Density Estimation for Microplastic Particles
=========================================================
"""

from typing import Any, Iterator
from pathlib import Path
import json
import pandas as pd

from .particle_analysis import Particle, ParticleAnalyzer


class DensityEstimator:
    """
    Compute density and coverage statistics from a ParticleAnalyzer.
    """

    def __init__(
        self,
        analyzer: ParticleAnalyzer,
        image_width: int,
        image_height: int,
        pixel_size_um: float | None = None,   # future calibration
    ) -> None:
        """
        Initialize the density estimator.

        Args:
            analyzer: ParticleAnalyzer containing detected particles.
            image_width: Width of the image (pixels).
            image_height: Height of the image (pixels).
            pixel_size_um: Physical size of one pixel in micrometres (optional).
        """
        self.analyzer = analyzer
        self.image_width = image_width
        self.image_height = image_height
        self.image_area = image_width * image_height
        self.pixel_size_um = pixel_size_um
        self.unit = "pixel" if pixel_size_um is None else "µm"

    @property
    def image_resolution(self) -> str:
        """Return the image resolution as a string (e.g., '640x640')."""
        return f"{self.image_width}x{self.image_height}"

    def is_calibrated(self) -> bool:
        """Return True if microscope calibration (pixel size) is set."""
        return self.pixel_size_um is not None

    # ----------------------------------------------------------------------
    # Core computations
    # ----------------------------------------------------------------------

    def particle_density(self) -> float:
        """Return number of particles per image, rounded to 2 decimals."""
        return round(float(self.analyzer.particle_count()), 2)

    def particle_density_per_pixel(self) -> float:
        """Return number of particles per square pixel."""
        if self.image_area == 0:
            return 0.0
        return round(
            self.analyzer.particle_count() / self.image_area,
            8
        )

    def particle_density_per_1000_pixels(self) -> float:
        """Return number of particles per 1000 square pixels."""
        return round(
            self.particle_density_per_pixel() * 1000,
            6
        )

    def occupied_area(self) -> int:
        """Return total area occupied by all particles (sum of their areas)."""
        return sum(p.area for p in self.analyzer)

    def empty_area(self) -> int:
        """Return image area not covered by particles."""
        return max(0, self.image_area - self.occupied_area())

    def coverage_percentage(self) -> float:
        """Return percentage of image area covered by particles."""
        if self.image_area == 0:
            return 0.0
        return round(
            (self.occupied_area() / self.image_area) * 100.0,
            2
        )

    def occupied_percentage(self) -> float:
        """Alias for coverage_percentage (research‑oriented)."""
        return self.coverage_percentage()

    def empty_percentage(self) -> float:
        """Return percentage of image area not covered by particles."""
        if self.image_area == 0:
            return 0.0
        return round(
            (self.empty_area() / self.image_area) * 100.0,
            2
        )

    def field_of_view(self) -> int:
        """Return the image area in pixels (later convertible to µm²)."""
        return self.image_area

    def occupied_fraction(self) -> float:
        """Return the fraction of image area covered by particles (0–1)."""
        if self.image_area == 0:
            return 0.0
        return round(self.occupied_area() / self.image_area, 6)

    # ----------------------------------------------------------------------
    # Comprehensive statistics (caches all computed values)
    # ----------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:
        """
        Return a dictionary with all density and area metrics,
        plus a subset of particle statistics from the analyzer.
        """
        # Get particle summary from the analyzer
        particle_stats = self.analyzer.statistics()
        if particle_stats is None:
            # No particles – return zero-filled metrics
            return {
                "total_particles": 0,
                "image_width": self.image_width,
                "image_height": self.image_height,
                "image_resolution": self.image_resolution,
                "image_area": self.image_area,
                "field_of_view": self.field_of_view(),
                "particle_density": 0.0,
                "particle_density_per_pixel": 0.0,
                "particle_density_per_1000_pixels": 0.0,
                "occupied_area": 0,
                "empty_area": self.image_area,
                "coverage_percentage": 0.0,
                "occupied_percentage": 0.0,
                "occupied_fraction": 0.0,
                "empty_percentage": 100.0,
                "average_particle_area": 0.0,
                "largest_particle": 0,
                "smallest_particle": 0,
                "average_equivalent_diameter": 0.0,
                "average_aspect_ratio": 0.0,
                "unit": self.unit,
                "pixel_size_um": None,
            }

        # --- Compute all metrics once and reuse ---
        total_particles = particle_stats["total_particles"]
        particle_density = round(float(total_particles), 2)

        density_per_pixel = (
            round(total_particles / self.image_area, 8)
            if self.image_area else 0.0
        )
        density_per_1000 = round(density_per_pixel * 1000, 6)

        occupied = self.occupied_area()
        empty = max(0, self.image_area - occupied)
        coverage = round((occupied / self.image_area) * 100.0, 2) if self.image_area else 0.0
        empty_pct = round((empty / self.image_area) * 100.0, 2) if self.image_area else 0.0
        occupied_frac = round(occupied / self.image_area, 6) if self.image_area else 0.0

        # Round calibration value if present
        calibrated_pixel_size = (
            round(self.pixel_size_um, 4)
            if self.pixel_size_um is not None
            else None
        )

        return {
            # Basic metrics
            "total_particles": total_particles,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "image_resolution": self.image_resolution,
            "image_area": self.image_area,
            "field_of_view": self.field_of_view(),
            "particle_density": particle_density,
            "particle_density_per_pixel": density_per_pixel,
            "particle_density_per_1000_pixels": density_per_1000,
            # Area metrics
            "occupied_area": occupied,
            "empty_area": empty,
            "coverage_percentage": coverage,
            "occupied_percentage": coverage,
            "occupied_fraction": occupied_frac,
            "empty_percentage": empty_pct,
            # Size metrics (from analyzer)
            "average_particle_area": particle_stats["average_area"],
            "largest_particle": particle_stats["largest_particle"],
            "smallest_particle": particle_stats["smallest_particle"],
            "average_equivalent_diameter": particle_stats["average_equivalent_diameter"],
            "average_aspect_ratio": particle_stats["average_aspect_ratio"],
            # Units & calibration
            "unit": self.unit,
            "pixel_size_um": calibrated_pixel_size,
        }

    def summary(self) -> dict[str, Any]:
        """Alias for statistics()."""
        return self.statistics()

    # ----------------------------------------------------------------------
    # Reporting and output
    # ----------------------------------------------------------------------

    def print_summary(self) -> None:
        """Print a formatted report of density statistics."""
        stats = self.statistics()
        print("=" * 60)
        print("DENSITY ESTIMATION REPORT")
        print("=" * 60)
        print(f"Image dimensions      : {self.image_width} x {self.image_height} px")
        print(f"Image area            : {self.image_area:,} px²")
        print(f"Field of view         : {stats['field_of_view']} px²")
        print(f"Total particles       : {stats['total_particles']}")
        print(f"Particle density      : {stats['particle_density']:.2f} particles/image")
        print(f"Density per pixel     : {stats['particle_density_per_pixel']:.6f} px⁻²")
        print(f"Density per 1000 px²  : {stats['particle_density_per_1000_pixels']:.6f}")
        print(f"Occupied area         : {stats['occupied_area']:,} px²")
        print(f"Empty area            : {stats['empty_area']:,} px²")
        print(f"Coverage percentage   : {stats['coverage_percentage']:.2f} %")
        print(f"Occupied fraction     : {stats['occupied_fraction']:.6f}")
        print(f"Empty percentage      : {stats['empty_percentage']:.2f} %")
        print(f"Average particle area : {stats['average_particle_area']:.2f} px²")
        print(f"Largest particle      : {stats['largest_particle']} px²")
        print(f"Smallest particle     : {stats['smallest_particle']} px²")
        print(f"Avg. equiv. diameter  : {stats['average_equivalent_diameter']:.2f} px")
        print(f"Avg. aspect ratio     : {stats['average_aspect_ratio']:.4f}")
        print(f"Unit                  : {stats['unit']}")
        if stats['pixel_size_um'] is not None:
            print(f"Pixel size (µm)       : {stats['pixel_size_um']}")
        print("=" * 60)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Return a DataFrame containing the density statistics (one row).
        Useful for batch processing of multiple images.
        """
        return pd.DataFrame([self.statistics()])

    def export_csv(self, output_path: Path) -> None:
        """Export density statistics to a CSV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(output_path, index=False)

    def export_json(self, output_path: Path) -> None:
        """Export density statistics to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(self.statistics(), file, indent=4, ensure_ascii=False)

    def save_statistics(self, output_path: Path) -> None:
        """Save summary statistics to JSON (identical to export_json)."""
        self.export_json(output_path)

    # ----------------------------------------------------------------------
    # Special methods (delegated to the analyzer)
    # ----------------------------------------------------------------------

    def __len__(self) -> int:
        """Return number of particles (delegated to the analyzer)."""
        return len(self.analyzer)

    def __iter__(self) -> Iterator[Particle]:
        """Iterate over particles (delegated to the analyzer)."""
        return iter(self.analyzer)

    def __getitem__(self, index: int) -> Particle:
        """Get a particle by index (delegated to the analyzer)."""
        return self.analyzer[index]

    def __contains__(self, particle: Particle) -> bool:
        """Check if a particle is present (delegated to the analyzer)."""
        return particle in self.analyzer

    def __bool__(self) -> bool:
        """Return True if there are particles."""
        return bool(self.analyzer)

    def __repr__(self) -> str:
        return (
            f"DensityEstimator("
            f"particles={len(self)}, "
            f"density={self.particle_density():.2f}, "
            f"coverage={self.coverage_percentage():.2f}%, "
            f"resolution={self.image_resolution}, "
            f"unit='{self.unit}')"
        )

    def __str__(self) -> str:
        """User‑friendly string representation."""
        return (
            "Density Estimator\n"
            f"Particles : {len(self)}\n"
            f"Coverage  : {self.coverage_percentage():.2f}%\n"
            f"Resolution: {self.image_resolution}"
        )


# ----------------------------------------------------------------------
# Example usage (if run as standalone)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # For testing outside the package, adjust the import accordingly.
    # Create a sample analyzer with a few particles
    analyzer = ParticleAnalyzer()
    analyzer.add_particle(x1=10, y1=20, x2=30, y2=40, confidence=0.95)
    analyzer.add_particle(x1=50, y1=60, x2=90, y2=100, confidence=0.88)
    analyzer.add_particle(x1=120, y1=30, x2=180, y2=80, confidence=0.92)

    estimator = DensityEstimator(
        analyzer,
        image_width=640,
        image_height=640,
        pixel_size_um=0.5   # optional calibration
    )

    estimator.print_summary()
    print("\nDataFrame preview:")
    print(estimator.to_dataframe())
    print(f"\nRepr: {estimator}")
    print(f"Contains first particle? {analyzer[0] in estimator}")

    print("\nStr representation:")
    print(estimator)
    print(f"Is calibrated? {estimator.is_calibrated()}")