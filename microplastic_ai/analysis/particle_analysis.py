# """
# =========================================================
# Particle Analysis

# Author : Tanmay
# __version__ = "1.0.0"
# Project : MicroPlastic-AI
# =========================================================
# """

# from dataclasses import dataclass, asdict
# import pandas as pd
# from typing import List, Iterator, Any
# from statistics import mean, median, stdev, variance
# from math import pi, sqrt
# import json
# from pathlib import Path


# @dataclass(slots=True)
# class Particle:
#     """
#     Represents one detected microplastic particle.
#     """

#     particle_id: int
#     class_id: int
#     class_name: str

#     x1: int
#     y1: int
#     x2: int
#     y2: int

#     width: int
#     height: int

#     area: int

#     confidence: float

#     center_x: float
#     center_y: float

#     aspect_ratio: float
#     perimeter: float
#     equivalent_diameter: float


# class ParticleAnalyzer:
#     """
#     Analyze detected particles.
#     """

#     def __init__(self) -> None:
#         self.particles: List[Particle] = []

#     def add_particle(
#         self,
#         x1: int,
#         y1: int,
#         x2: int,
#         y2: int,
#         confidence: float,
#         class_id: int = 0,
#         class_name: str = "Microplastic",
#     ) -> None:

#         width = max(0, x2 - x1)
#         height = max(0, y2 - y1)

#         area = width * height

#         aspect_ratio = width / height if height > 0 else 0

#         perimeter = 2 * (width + height)

#         equivalent_diameter = sqrt(4 * area / pi) if area > 0 else 0

#         center_x = round(x1 + width / 2, 2)
#         center_y = round(y1 + height / 2, 2)

#         particle = Particle(
#             particle_id=self.particle_count() + 1,
#             class_id=class_id,
#             class_name=class_name,
#             x1=x1,
#             y1=y1,
#             x2=x2,
#             y2=y2,
#             width=width,
#             height=height,
#             area=area,
#             confidence=round(confidence, 4),
#             center_x=center_x,
#             center_y=center_y,
#             aspect_ratio=round(aspect_ratio, 4),
#             perimeter=round(perimeter, 4),
#             equivalent_diameter=round(equivalent_diameter, 4),
#         )

#         self.particles.append(particle)

#     def statistics(self) -> dict[str, Any] | None:
#         if not self.particles:
#             return None

#         areas = [p.area for p in self.particles]
#         widths = [p.width for p in self.particles]
#         heights = [p.height for p in self.particles]
#         confidences = [p.confidence for p in self.particles]
#         aspect_ratios = [p.aspect_ratio for p in self.particles]
#         perimeters = [p.perimeter for p in self.particles]
#         diameters = [p.equivalent_diameter for p in self.particles]

#         return {
#             "total_particles": self.particle_count(),
#             "average_area": round(mean(areas), 2),
#             "largest_particle": max(areas),
#             "smallest_particle": min(areas),
#             "average_width": round(mean(widths), 2),
#             "average_height": round(mean(heights), 2),
#             "average_confidence": round(mean(confidences), 4),
#             "median_area": round(median(areas), 2),
#             "std_area": round(stdev(areas) if len(areas) > 1 else 0, 2),
#             "variance_area": round(variance(areas) if len(areas) > 1 else 0, 2),
#             "median_width": round(median(widths), 2),
#             "median_height": round(median(heights), 2),
#             "median_confidence": round(median(confidences), 4),
#             "highest_confidence": round(max(confidences), 4),
#             "lowest_confidence": round(min(confidences), 4),
#             "average_aspect_ratio": round(mean(aspect_ratios), 4),
#             "average_perimeter": round(mean(perimeters), 2),
#             "average_equivalent_diameter": round(mean(diameters), 2),
#         }

#     def summary(self) -> dict[str, Any] | None:
#         return self.statistics()

#     def print_summary(self) -> None:
#         summary = self.summary()
#         if summary is None:
#             print("No particles detected.")
#             return

#         print("=" * 60)
#         print("PARTICLE ANALYSIS REPORT")
#         print("=" * 60)
#         print(f"Particles                 : {summary['total_particles']}")
#         print(f"Average Area              : {summary['average_area']:.2f} px²")
#         print(f"Median Area               : {summary['median_area']:.2f} px²")
#         print(f"Std. Dev. Area            : {summary['std_area']:.2f} px²")
#         print(f"Variance Area             : {summary['variance_area']:.2f} px²")
#         print(f"Largest Particle          : {summary['largest_particle']} px²")
#         print(f"Smallest Particle         : {summary['smallest_particle']} px²")
#         print(f"Average Width             : {summary['average_width']:.2f} px")
#         print(f"Median Width              : {summary['median_width']:.2f} px")
#         print(f"Average Height            : {summary['average_height']:.2f} px")
#         print(f"Median Height             : {summary['median_height']:.2f} px")
#         print(f"Average Confidence        : {summary['average_confidence']:.3f}")
#         print(f"Median Confidence         : {summary['median_confidence']:.3f}")
#         print(f"Highest Confidence        : {summary['highest_confidence']:.3f}")
#         print(f"Lowest Confidence         : {summary['lowest_confidence']:.3f}")
#         print(f"Average Aspect Ratio      : {summary['average_aspect_ratio']:.4f}")
#         print(f"Average Perimeter         : {summary['average_perimeter']:.2f} px")
#         print(f"Average Equivalent Diam.  : {summary['average_equivalent_diameter']:.2f} px")
#         print("=" * 60)

#     def clear(self) -> None:
#         """Remove all particles from the analyzer."""
#         self.particles.clear()

#     def get_particle(self, particle_id: int) -> Particle | None:
#         """Retrieve a particle by its ID."""
#         for particle in self.particles:
#             if particle.particle_id == particle_id:
#                 return particle
#         return None

#     def get_particles(self) -> List[Particle]:
#         """Return a copy of the list of particles."""
#         return self.particles.copy()

#     def particle_count(self) -> int:
#         """Return total detected particles."""
#         return len(self)

#     def to_dataframe(self) -> pd.DataFrame:
#         """Convert particle data to a pandas DataFrame."""
#         if not self.particles:
#             return pd.DataFrame()
#         return pd.DataFrame([asdict(p) for p in self.particles])

#     def export_csv(self, output_path: Path) -> None:
#         """Export particle data to CSV."""
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#         self.to_dataframe().to_csv(output_path, index=False)

#     def export_json(self, output_path: Path) -> None:
#         """Export particle data to a JSON file."""
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(output_path, "w", encoding="utf-8") as file:
#             json.dump([asdict(p) for p in self.particles], file, indent=4, ensure_ascii=False)

#     def __iter__(self) -> Iterator[Particle]:
#         """Iterate over particles."""
#         return iter(self.particles)

#     def __len__(self) -> int:
#         """Return the number of particles."""
#         return len(self.particles)

#     def save_statistics(self, output_path: Path) -> None:
#         """Save summary statistics to JSON."""
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(output_path, "w", encoding="utf-8") as file:
#             json.dump(self.statistics(), file, indent=4, ensure_ascii=False)

#     def __getitem__(self, index: int) -> Particle:
#         """Get a particle by index."""
#         return self.particles[index]

#     def __repr__(self) -> str:
#         return (
#             f"ParticleAnalyzer("
#             f"particles={self.particle_count()}, "
#             f"classes=1)"
#         )

#     def __bool__(self) -> bool:
#         """Return True if there are particles."""
#         return bool(self.particles)


# if __name__ == "__main__":
#     analyzer = ParticleAnalyzer()
#     # Example usage
#     analyzer.add_particle(
#         x1=10, y1=20, x2=30, y2=40,
#         confidence=0.95
#     )
#     analyzer.add_particle(
#         x1=50, y1=60, x2=90, y2=100,
#         confidence=0.88
#     )
#     analyzer.print_summary()

#     # Verify DataFrame output
#     print("\nDataFrame preview:")
#     print(analyzer.to_dataframe())


"""
=========================================================
Particle Analysis

Author : Tanmay
Project : MicroPlastic-AI
=========================================================
"""

from dataclasses import dataclass, asdict
import pandas as pd
from typing import List, Iterator
from statistics import mean, median, stdev, variance
from math import pi, sqrt
import json
from pathlib import Path


@dataclass
class Particle:
    """
    Represents one detected microplastic particle.
    """

    particle_id: int
    class_id: int
    class_name: str

    x1: int
    y1: int
    x2: int
    y2: int

    width: int
    height: int

    area: int

    confidence: float

    center_x: float
    center_y: float

    aspect_ratio: float
    perimeter: float
    equivalent_diameter: float


class ParticleAnalyzer:
    """
    Analyze detected particles.
    """

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def add_particle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        confidence: float,
        class_id: int = 0,
        class_name: str = "Microplastic",
    ) -> None:

        width = int(max(0, x2 - x1))      # ensure Python int
        height = int(max(0, y2 - y1))     # ensure Python int

        area = width * height

        aspect_ratio = width / height if height > 0 else 0

        perimeter = 2 * (width + height)

        equivalent_diameter = sqrt(4 * area / pi) if area > 0 else 0

        center_x = round(x1 + width / 2, 2)
        center_y = round(y1 + height / 2, 2)

        particle = Particle(
            particle_id=self.particle_count() + 1,
            class_id=class_id,
            class_name=class_name,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            width=width,
            height=height,
            area=area,
            confidence=round(confidence, 4),
            center_x=center_x,
            center_y=center_y,
            aspect_ratio=round(aspect_ratio, 4),
            perimeter=round(perimeter, 4),
            equivalent_diameter=round(equivalent_diameter, 4),
        )

        self.particles.append(particle)

    def statistics(self) -> dict | None:
        if not self.particles:
            return None

        # Convert to Python ints to avoid numpy int64 issues with statistics module
        areas = [int(p.area) for p in self.particles]
        widths = [int(p.width) for p in self.particles]
        heights = [int(p.height) for p in self.particles]
        confidences = [p.confidence for p in self.particles]
        aspect_ratios = [p.aspect_ratio for p in self.particles]
        perimeters = [p.perimeter for p in self.particles]
        diameters = [p.equivalent_diameter for p in self.particles]

        return {
            "total_particles": self.particle_count(),
            "average_area": round(mean(areas), 2),
            "largest_particle": max(areas),
            "smallest_particle": min(areas),
            "average_width": round(mean(widths), 2),
            "average_height": round(mean(heights), 2),
            "average_confidence": round(mean(confidences), 4),
            "median_area": round(median(areas), 2),
            "std_area": round(stdev(areas) if len(areas) > 1 else 0, 2),
            "variance_area": round(variance(areas) if len(areas) > 1 else 0, 2),
            "median_width": round(median(widths), 2),
            "median_height": round(median(heights), 2),
            "median_confidence": round(median(confidences), 4),
            "highest_confidence": round(max(confidences), 4),
            "lowest_confidence": round(min(confidences), 4),
            "average_aspect_ratio": round(mean(aspect_ratios), 4),
            "average_perimeter": round(mean(perimeters), 2),
            "average_equivalent_diameter": round(mean(diameters), 2),
        }

    def summary(self) -> dict | None:
        return self.statistics()

    def print_summary(self) -> None:
        summary = self.summary()
        if summary is None:
            print("No particles detected.")
            return

        print("=" * 60)
        print("PARTICLE ANALYSIS REPORT")
        print("=" * 60)
        print(f"Particles                 : {summary['total_particles']}")
        print(f"Average Area              : {summary['average_area']:.2f} px²")
        print(f"Median Area               : {summary['median_area']:.2f} px²")
        print(f"Std. Dev. Area            : {summary['std_area']:.2f} px²")
        print(f"Variance Area             : {summary['variance_area']:.2f} px²")
        print(f"Largest Particle          : {summary['largest_particle']} px²")
        print(f"Smallest Particle         : {summary['smallest_particle']} px²")
        print(f"Average Width             : {summary['average_width']:.2f} px")
        print(f"Median Width              : {summary['median_width']:.2f} px")
        print(f"Average Height            : {summary['average_height']:.2f} px")
        print(f"Median Height             : {summary['median_height']:.2f} px")
        print(f"Average Confidence        : {summary['average_confidence']:.3f}")
        print(f"Median Confidence         : {summary['median_confidence']:.3f}")
        print(f"Highest Confidence        : {summary['highest_confidence']:.3f}")
        print(f"Lowest Confidence         : {summary['lowest_confidence']:.3f}")
        print(f"Average Aspect Ratio      : {summary['average_aspect_ratio']:.4f}")
        print(f"Average Perimeter         : {summary['average_perimeter']:.2f} px")
        print(f"Average Equivalent Diam.  : {summary['average_equivalent_diameter']:.2f} px")
        print("=" * 60)

    def clear(self) -> None:
        """Remove all particles from the analyzer."""
        self.particles.clear()

    def get_particle(self, particle_id: int) -> Particle | None:
        """Retrieve a particle by its ID."""
        for particle in self.particles:
            if particle.particle_id == particle_id:
                return particle
        return None

    def get_particles(self) -> List[Particle]:
        """Return a copy of the list of particles."""
        return self.particles.copy()

    def particle_count(self) -> int:
        """Return total detected particles."""
        return len(self)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert particle data to a pandas DataFrame."""
        if not self.particles:
            return pd.DataFrame()
        return pd.DataFrame([asdict(p) for p in self.particles])

    def export_csv(self, output_path: Path) -> None:
        """Export particle data to CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(output_path, index=False)

    def export_json(self, output_path: Path) -> None:
        """Export particle data to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump([asdict(p) for p in self.particles], file, indent=4, ensure_ascii=False)

    def __iter__(self) -> Iterator[Particle]:
        """Iterate over particles."""
        return iter(self.particles)

    def __len__(self) -> int:
        """Return the number of particles."""
        return len(self.particles)

    def save_statistics(self, output_path: Path) -> None:
        """Save summary statistics to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(self.statistics(), file, indent=4, ensure_ascii=False)

    def __getitem__(self, index: int) -> Particle:
        """Get a particle by index."""
        return self.particles[index]

    def __repr__(self) -> str:
        return (
            f"ParticleAnalyzer("
            f"particles={self.particle_count()}, "
            f"classes=1)"
        )

    def __bool__(self) -> bool:
        """Return True if there are particles."""
        return bool(self.particles)