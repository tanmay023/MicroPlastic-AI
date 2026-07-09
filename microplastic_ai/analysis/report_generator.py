"""
=========================================================
Report Generator for Microplastic Analysis
=========================================================
"""

import json
import csv
import datetime
import logging
import platform
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from microplastic_ai.config import (
    REPORT_DIR,
    PROJECT_NAME,
    AUTHOR,
    MODEL_NAME,
)
from microplastic_ai.analysis.particle_analysis import ParticleAnalyzer
from microplastic_ai.analysis.density_estimation import DensityEstimator
from microplastic_ai.visualization.visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate comprehensive reports from particle analysis results.
    Supports JSON, CSV, and HTML outputs (PDF planned for Phase 2).
    """

    REPORT_VERSION = "1.0"

    def __init__(
        self,
        analyzer: ParticleAnalyzer,
        estimator: DensityEstimator,
        visualizer: VisualizationEngine,
        image_name: str = "unknown",
        output_dir: Optional[Path] = None,
    ) -> None:
        """
        Args:
            analyzer: ParticleAnalyzer with detection results.
            estimator: DensityEstimator with computed density metrics.
            visualizer: VisualizationEngine (can be None if visualizations are not available).
            image_name: Filename or identifier of the original image.
            output_dir: Directory to save all report files. Defaults to REPORT_DIR.
        """
        self.analyzer = analyzer
        self.estimator = estimator
        self.visualizer = visualizer
        self.image_name = image_name

        self.report_dir = output_dir or REPORT_DIR
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Log warnings if components are missing
        if len(self.analyzer) == 0:
            logger.warning("ParticleAnalyzer contains no particles.")
        if self.estimator is None:
            logger.warning("DensityEstimator is not provided. Density statistics will be empty.")
        if self.visualizer is None:
            logger.warning("VisualizationEngine is not provided. Visualizations will be empty.")

        logger.info(f"ReportGenerator initialized. Output directory: {self.report_dir}")

    # ----------------------------------------------------------------------
    # Data collection
    # ----------------------------------------------------------------------

    def collect_metadata(self) -> Dict[str, Any]:
        """
        Return a dictionary with project, image, and environment metadata.
        """
        import sys
        import cv2
        try:
            import ultralytics
            ultralytics_version = ultralytics.__version__
        except (ImportError, AttributeError):
            ultralytics_version = "unknown"

        return {
            "report_version": self.REPORT_VERSION,
            "project": PROJECT_NAME,
            "author": AUTHOR,
            "model": MODEL_NAME,
            "image_name": self.image_name,
            "image_resolution": f"{self.visualizer.width}x{self.visualizer.height}" if self.visualizer else "unknown",
            "generated_on": datetime.datetime.now().isoformat(),
            "python_version": sys.version.split()[0],
            "opencv_version": cv2.__version__,
            "ultralytics_version": ultralytics_version,
            "platform": platform.platform(),
            "os": platform.system(),
            "processor": platform.processor(),
            "machine": platform.machine(),
        }

    def collect_statistics(self) -> Dict[str, Any]:
        """
        Merge particle and density statistics into a single flat dictionary.
        """
        particle_stats = self.analyzer.statistics()
        density_stats = self.estimator.statistics() if self.estimator else None

        # If no particles, provide defaults
        if particle_stats is None:
            particle_stats = {
                "total_particles": 0,
                "average_area": 0.0,
                "largest_particle": 0,
                "smallest_particle": 0,
                "average_confidence": 0.0,
                "median_confidence": 0.0,
                "highest_confidence": 0.0,
                "lowest_confidence": 0.0,
                "average_equivalent_diameter": 0.0,
                "average_aspect_ratio": 0.0,
                "std_area": 0.0,
                "variance_area": 0.0,
            }

        if density_stats is None:
            density_stats = {
                "coverage_percentage": 0.0,
                "particle_density": 0.0,
                "particle_density_per_pixel": 0.0,
                "occupied_area": 0,
                "empty_area": 0,
                "occupied_fraction": 0.0,
            }

        # Merge both dictionaries (particle stats take precedence on conflicts)
        merged = {**density_stats, **particle_stats}
        return merged

    def collect_visualizations(self) -> List[Path]:
        """
        Scan the visualizer's output directory for image files and return sorted list.
        Supports .png, .jpg, .jpeg.
        """
        if self.visualizer is None:
            return []

        vis_dir = self.visualizer.output_dir
        if not vis_dir.exists():
            logger.warning(f"Visualization directory not found: {vis_dir}")
            return []

        extensions = ("*.png", "*.jpg", "*.jpeg")
        files = []
        for ext in extensions:
            files.extend(vis_dir.glob(ext))
        return sorted(files)

    # ----------------------------------------------------------------------
    # Export methods
    # ----------------------------------------------------------------------

    def generate_json(self) -> Path:
        """
        Write a comprehensive JSON report with metadata, statistics, and visualizations.
        Optionally, also write separate metadata.json and statistics.json for API use.
        """
        data = {
            "metadata": self.collect_metadata(),
            "statistics": self.collect_statistics(),
            "visualizations": [str(p) for p in self.collect_visualizations()],
        }
        path = self.report_dir / "report.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"JSON report written to {path}")

        # Optionally write metadata and statistics separately
        metadata_path = self.report_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(data["metadata"], f, indent=4, ensure_ascii=False)
        stats_path = self.report_dir / "statistics.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(data["statistics"], f, indent=4, ensure_ascii=False)

        return path

    def generate_csv(self) -> Path:
        """
        Generate a summary CSV with one row containing the most important metrics.
        """
        stats = self.collect_statistics()
        row = {
            "image": self.image_name,
            "total_particles": stats.get("total_particles", 0),
            "coverage_%": stats.get("coverage_percentage", 0.0),
            "particle_density": stats.get("particle_density", 0.0),
            "density_per_pixel": stats.get("particle_density_per_pixel", 0.0),
            "average_area_px2": stats.get("average_area", 0.0),
            "average_confidence": stats.get("average_confidence", 0.0),
            "largest_particle_px2": stats.get("largest_particle", 0),
            "smallest_particle_px2": stats.get("smallest_particle", 0),
        }
        path = self.report_dir / "analysis_summary.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
            writer.writerow(row)
        logger.info(f"CSV summary written to {path}")
        return path

    def generate_html(self) -> Path:
        """
        Generate a self-contained HTML report with embedded statistics and
        links to all visualisation images (if available).
        """
        metadata = self.collect_metadata()
        stats = self.collect_statistics()
        vis_files = self.collect_visualizations()

        # Build a gallery of images
        gallery_html = ""
        if vis_files:
            for img_path in vis_files:
                # Use relpath to get path relative to the report directory
                rel_path = os.path.relpath(str(img_path), start=str(self.report_dir))
                gallery_html += (
                    f'<div class="gallery-item">'
                    f'<img src="{rel_path}" alt="{img_path.stem}" loading="lazy"/>'
                    f'<p>{img_path.stem}</p>'
                    f'</div>'
                )
        else:
            gallery_html = "<p>No visualizations available.</p>"

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MicroPlastic-AI Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
            color: #333;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .metadata table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .metadata td {{
            padding: 4px 8px;
            border-bottom: 1px solid #ddd;
        }}
        .metadata td:first-child {{
            font-weight: bold;
            width: 30%;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-box {{
            background: #e8f4f8;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
            border: 1px solid #bee5eb;
        }}
        .summary-box .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #0c5460;
        }}
        .summary-box .label {{
            font-size: 0.85em;
            color: #0c5460;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        .stat-box .value {{
            font-size: 1.6em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-box .label {{
            font-size: 0.85em;
            color: #6c757d;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .gallery-item {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        .gallery-item img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .gallery-item p {{
            margin-top: 8px;
            font-size: 0.9em;
            color: #495057;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.8em;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MicroPlastic‑AI Analysis Report</h1>
        <p style="text-align:center; color:#6c757d;">Generated on {metadata['generated_on']}</p>

        <div class="metadata">
            <h3>Metadata</h3>
            <table>
                <tr><td>Project</td><td>{metadata['project']}</td></tr>
                <tr><td>Author</td><td>{metadata['author']}</td></tr>
                <tr><td>Model</td><td>{metadata['model']}</td></tr>
                <tr><td>Image</td><td>{metadata['image_name']}</td></tr>
                <tr><td>Resolution</td><td>{metadata['image_resolution']}</td></tr>
                <tr><td>OpenCV</td><td>{metadata['opencv_version']}</td></tr>
                <tr><td>Ultralytics</td><td>{metadata['ultralytics_version']}</td></tr>
                <tr><td>Platform</td><td>{metadata['platform']}</td></tr>
                <tr><td>OS</td><td>{metadata['os']}</td></tr>
                <tr><td>Processor</td><td>{metadata['processor']}</td></tr>
                <tr><td>Machine</td><td>{metadata['machine']}</td></tr>
            </table>
        </div>

        <h2>Analysis Summary</h2>
        <div class="summary-grid">
            <div class="summary-box"><span class="value">{stats.get('total_particles', 0)}</span><div class="label">Particles</div></div>
            <div class="summary-box"><span class="value">{stats.get('coverage_percentage', 0):.2f}%</span><div class="label">Coverage</div></div>
            <div class="summary-box"><span class="value">{stats.get('particle_density', 0):.2f}</span><div class="label">Particles / Image</div></div>
            <div class="summary-box"><span class="value">{stats.get('average_confidence', 0):.2f}</span><div class="label">Avg. Confidence</div></div>
        </div>

        <h2>Detailed Statistics</h2>
        <div class="stats-grid">
            <div class="stat-box"><span class="value">{stats.get('average_area', 0):.1f}</span><div class="label">Avg. Area (px²)</div></div>
            <div class="stat-box"><span class="value">{stats.get('largest_particle', 0)}</span><div class="label">Largest (px²)</div></div>
            <div class="stat-box"><span class="value">{stats.get('smallest_particle', 0)}</span><div class="label">Smallest (px²)</div></div>
            <div class="stat-box"><span class="value">{stats.get('particle_density_per_pixel', 0):.6f}</span><div class="label">Density / px²</div></div>
            <div class="stat-box"><span class="value">{stats.get('occupied_area', 0):,}</span><div class="label">Occupied Area (px²)</div></div>
            <div class="stat-box"><span class="value">{stats.get('empty_area', 0):,}</span><div class="label">Empty Area (px²)</div></div>
            <div class="stat-box"><span class="value">{stats.get('average_equivalent_diameter', 0):.2f}</span><div class="label">Avg. Diameter (px)</div></div>
            <div class="stat-box"><span class="value">{stats.get('average_aspect_ratio', 0):.2f}</span><div class="label">Avg. Aspect Ratio</div></div>
        </div>

        <h2>Visualizations</h2>
        <div class="gallery">
            {gallery_html}
        </div>

        <div class="footer">
            Report generated by MicroPlastic‑AI • {datetime.datetime.now().year}
        </div>
    </div>
</body>
</html>
        """

        path = self.report_dir / "report.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"HTML report written to {path}")
        return path

    # ----------------------------------------------------------------------
    # Combined report generation
    # ----------------------------------------------------------------------

    def generate_complete_report(self) -> Dict[str, Path]:
        """
        Generate all report formats (JSON, CSV, HTML) and return their paths.
        Prints a summary banner to the console.
        """
        paths = {
            "json": self.generate_json(),
            "csv": self.generate_csv(),
            "html": self.generate_html(),
        }

        print("\n" + "=" * 50)
        print("         REPORT GENERATED SUCCESSFULLY")
        print("=" * 50)
        print(f"  JSON  : {paths['json']}")
        print(f"  CSV   : {paths['csv']}")
        print(f"  HTML  : {paths['html']}")
        print(f"  Directory: {self.report_dir}")
        print("=" * 50 + "\n")

        logger.info(f"Complete report generated in {self.report_dir}")
        return paths

    # ----------------------------------------------------------------------
    # Special methods
    # ----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ReportGenerator("
            f"image='{self.image_name}', "
            f"particles={len(self.analyzer)}, "
            f"reports='{self.report_dir}')"
        )