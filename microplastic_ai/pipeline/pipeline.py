"""
=========================================================
Microplastic Pipeline Engine
=========================================================
Orchestrates the entire analysis workflow:
  Image → YOLO Detection → Particle Analysis →
  Density Estimation → Visualization → Report Generation
"""

import logging
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from tqdm import tqdm
import cv2
import numpy as np
from ultralytics import YOLO

# Try to import torch for GPU detection
try:
    import torch
except ImportError:
    torch = None

# Try to import psutil for memory monitoring
try:
    import psutil
except ImportError:
    psutil = None

from microplastic_ai.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    OUTPUT_DIR,
    SAVE_OUTPUTS,
    DEVICE,                     # <-- Now correctly imported
    IMAGE_EXTENSIONS,
)
from microplastic_ai.analysis.particle_analysis import ParticleAnalyzer
from microplastic_ai.analysis.density_estimation import DensityEstimator
from microplastic_ai.visualization.visualization_engine import VisualizationEngine
from microplastic_ai.analysis.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Structured result from a single image processing run."""
    success: bool
    image_path: str
    output_dir: Path
    total_particles: int = 0
    coverage: float = 0.0
    average_confidence: float = 0.0
    average_area: float = 0.0
    image_width: int = 0
    image_height: int = 0
    processing_times: Dict[str, float] = field(default_factory=dict)
    memory_usage: Dict[str, float] = field(default_factory=dict)
    version_info: Dict[str, str] = field(default_factory=dict)
    visualizations: Optional[Dict[str, Any]] = None
    reports: Optional[Dict[str, Any]] = None
    analyzer: Optional[ParticleAnalyzer] = None
    estimator: Optional[DensityEstimator] = None
    visualizer: Optional[VisualizationEngine] = None
    report_generator: Optional[ReportGenerator] = None
    detections: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class MicroplasticPipeline:
    """
    End‑to‑end pipeline for microplastic particle detection and analysis.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        conf_threshold: Optional[float] = None,
        save_outputs: Optional[bool] = None,
        output_dir: Optional[Path] = None,
        device: Optional[str] = None,
        extensions: Optional[tuple] = None,
    ) -> None:
        """
        Args:
            model_path: Path to the trained YOLO model weights.
            conf_threshold: Confidence threshold for detections.
            save_outputs: If True, save all outputs (visualizations, reports).
            output_dir: Root directory for saving outputs.
            device: Inference device ('cpu', 'cuda', or None for auto).
            extensions: Tuple of allowed image extensions.
        """
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.conf_threshold = conf_threshold if conf_threshold is not None else CONFIDENCE_THRESHOLD
        self.save_outputs = save_outputs if save_outputs is not None else SAVE_OUTPUTS
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.extensions = extensions or IMAGE_EXTENSIONS

        # Automatic device selection
        if device is None:
            if DEVICE == "auto":
                if torch is not None and torch.cuda.is_available():
                    self.device = "cuda"
                else:
                    self.device = "cpu"
            else:
                self.device = DEVICE
        else:
            self.device = device

        self.model = None
        self.load_model()

        logger.info(
            f"Pipeline initialized. Model: {self.model_path.name}, "
            f"Confidence: {self.conf_threshold}, Device: {self.device}, "
            f"Save outputs: {self.save_outputs}"
        )

    @property
    def model_name(self) -> str:
        """Return the model filename without extension."""
        return self.model_path.stem

    # ----------------------------------------------------------------------
    # Core components
    # ----------------------------------------------------------------------

    def load_model(self) -> None:
        """Load the YOLO model from the specified path."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        self.model = YOLO(str(self.model_path))
        logger.info(f"Model loaded from {self.model_path}")

    def load_image(self, image_path: Path) -> Tuple[np.ndarray, Path]:
        """Read an image from disk and return it as a BGR numpy array."""
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        logger.debug(f"Image loaded: {image_path} (shape={img.shape})")
        return img, image_path

    def _get_memory_usage(self) -> Dict[str, float]:
        """Collect memory usage statistics (if psutil is available)."""
        mem = {}
        if psutil is not None:
            mem["ram_used_mb"] = psutil.virtual_memory().used / (1024**2)
            mem["ram_total_mb"] = psutil.virtual_memory().total / (1024**2)
            mem["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        if self.device == "cuda" and torch is not None and torch.cuda.is_available():
            mem["gpu_memory_allocated_mb"] = torch.cuda.memory_allocated() / (1024**2)
            mem["gpu_memory_reserved_mb"] = torch.cuda.memory_reserved() / (1024**2)
            mem["gpu_memory_peak_mb"] = torch.cuda.max_memory_allocated() / (1024**2)
        return mem

    def _get_version_info(self) -> Dict[str, str]:
        """Collect software version information."""
        import sys
        import cv2
        try:
            import ultralytics
            ultralytics_version = ultralytics.__version__
        except (ImportError, AttributeError):
            ultralytics_version = "unknown"
        info = {
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
            "ultralytics": ultralytics_version,
            "torch": torch.__version__ if torch else "not installed",
            "cuda": torch.version.cuda if torch and torch.cuda.is_available() else "not available",
        }
        return info

    # ----------------------------------------------------------------------
    # Pipeline stages
    # ----------------------------------------------------------------------

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run YOLO inference on the image and return enriched detections.

        Returns:
            List of detection dicts with keys:
                'xyxy', 'confidence', 'class_id', 'class_name',
                'width', 'height', 'area', 'center_x', 'center_y'.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False
        )[0]
        detections = []

        if results.boxes is not None and len(results.boxes) > 0:
            h, w = image.shape[:2]
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                # Clamp to image boundaries
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(0, min(x2, w - 1))
                y2 = max(0, min(y2, h - 1))
                if x1 >= x2 or y1 >= y2:
                    continue
                width = x2 - x1
                height = y2 - y1
                area = width * height
                center_x = x1 + width / 2
                center_y = y1 + height / 2
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())

                detections.append({
                    "xyxy": (x1, y1, x2, y2),
                    "confidence": confidence,
                    "class_id": class_id,
                    "class_name": self.model.names.get(class_id, "unknown"),
                    "width": width,
                    "height": height,
                    "area": area,
                    "center_x": center_x,
                    "center_y": center_y,
                })

        logger.debug(f"Detected {len(detections)} particles")
        return detections

    def analyze(self, detections: List[Dict[str, Any]], image_shape: tuple) -> ParticleAnalyzer:
        """
        Create a ParticleAnalyzer and populate it with detected particles.
        """
        h, w = image_shape[:2]
        analyzer = ParticleAnalyzer()

        for det in detections:
            x1, y1, x2, y2 = det["xyxy"]
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))
            if x1 >= x2 or y1 >= y2:
                continue

            analyzer.add_particle(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                confidence=det["confidence"],
                class_id=det["class_id"],
                class_name=det["class_name"],
            )

        self.analyzer = analyzer
        logger.debug(f"ParticleAnalyzer created with {len(analyzer)} particles")
        return analyzer

    def estimate_density(self, analyzer: ParticleAnalyzer, image: np.ndarray) -> DensityEstimator:
        """
        Create a DensityEstimator from the analyzer and image.
        """
        h, w = image.shape[:2]
        estimator = DensityEstimator(analyzer, image_width=w, image_height=h)
        self.estimator = estimator
        logger.debug("DensityEstimator created")
        return estimator

    def visualize(
        self,
        analyzer: ParticleAnalyzer,
        estimator: DensityEstimator,
        image: np.ndarray,
        output_dir: Optional[Path] = None,
    ) -> VisualizationEngine:
        """
        Create a VisualizationEngine and generate all figures.
        """
        if output_dir is None:
            output_dir = self.output_dir

        vis_dir = output_dir / "visualizations"
        visualizer = VisualizationEngine(
            analyzer=analyzer,
            estimator=estimator,
            image=image,
            output_dir=vis_dir,
        )
        if self.save_outputs:
            visualizer.save_all()
            logger.debug(f"Visualizations saved to {vis_dir}")
        else:
            logger.debug("Visualizations generated but not saved (save_outputs=False)")
        self.visualizer = visualizer
        return visualizer

    def generate_reports(
        self,
        analyzer: ParticleAnalyzer,
        estimator: DensityEstimator,
        visualizer: VisualizationEngine,
        image_name: str,
        output_dir: Optional[Path] = None,
    ) -> ReportGenerator:
        """
        Create a ReportGenerator and generate all report formats.
        """
        if output_dir is None:
            output_dir = self.output_dir

        report_dir = output_dir / "reports"
        report_gen = ReportGenerator(
            analyzer=analyzer,
            estimator=estimator,
            visualizer=visualizer,
            image_name=image_name,
            output_dir=report_dir,
        )
        if self.save_outputs:
            report_gen.generate_complete_report()
            logger.debug(f"Reports saved to {report_dir}")
        else:
            logger.debug("Reports generated but not saved (save_outputs=False)")
        self.report_generator = report_gen
        return report_gen

    # ----------------------------------------------------------------------
    # Main processing methods
    # ----------------------------------------------------------------------

    def process_image(
        self,
        image_path: Union[str, Path],
        output_dir: Optional[Path] = None,
        return_objects: bool = False,
        save_original: bool = True,
    ) -> PipelineResult:
        """
        Run the full pipeline on a single image.

        Args:
            image_path: Path to the input image.
            output_dir: Custom output directory (overrides self.output_dir).
            return_objects: If True, include analyzers/estimators in result.
            save_original: If True, copy the original image to the output folder.

        Returns:
            PipelineResult object.
        """
        image_path = Path(image_path)
        start_time = time.time()
        stage_times = {}

        # Determine output directory (per image)
        if output_dir is None:
            output_dir = self.output_dir / image_path.stem
        else:
            # If output_dir is provided, it's the final directory (no extra subfolder)
            pass
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Capture memory before
        mem_before = self._get_memory_usage()
        # Reset GPU peak counters if using CUDA
        if self.device == "cuda" and torch is not None and torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        try:
            # 1. Load image
            t0 = time.time()
            image, _ = self.load_image(image_path)
            stage_times["load_image"] = (time.time() - t0) * 1000  # ms
            logger.debug(f"Loading image... {stage_times['load_image']:.1f}ms")

            # 2. Detect
            t0 = time.time()
            detections = self.detect(image)
            stage_times["detection"] = (time.time() - t0) * 1000
            logger.debug(f"Running detection... ({len(detections)} particles) in {stage_times['detection']:.1f}ms")

            # 3. Analyze
            t0 = time.time()
            analyzer = self.analyze(detections, image.shape)
            stage_times["analysis"] = (time.time() - t0) * 1000
            logger.debug(f"Analyzing particles... {stage_times['analysis']:.1f}ms")

            # 4. Estimate density
            t0 = time.time()
            estimator = self.estimate_density(analyzer, image)
            stage_times["density"] = (time.time() - t0) * 1000
            logger.debug(f"Estimating density... {stage_times['density']:.1f}ms")

            # 5. Visualize
            t0 = time.time()
            visualizer = self.visualize(analyzer, estimator, image, output_dir)
            stage_times["visualization"] = (time.time() - t0) * 1000
            logger.debug(f"Generating visualizations... {stage_times['visualization']:.1f}ms")

            # 6. Generate reports
            t0 = time.time()
            report_gen = self.generate_reports(
                analyzer, estimator, visualizer, image_path.stem, output_dir
            )
            stage_times["reports"] = (time.time() - t0) * 1000
            logger.debug(f"Generating reports... {stage_times['reports']:.1f}ms")

            # Copy original image if requested
            if self.save_outputs and save_original:
                orig_dest = output_dir / image_path.name
                shutil.copy2(str(image_path), str(orig_dest))
                logger.debug(f"Original image copied to {orig_dest}")

            # Collect memory after (peak GPU is now available)
            mem_after = self._get_memory_usage()
            mem_peak = {}
            for key in set(mem_before.keys()) | set(mem_after.keys()):
                if 'peak' in key:
                    mem_peak[key] = mem_after.get(key, 0)
                else:
                    mem_peak[key] = max(mem_before.get(key, 0), mem_after.get(key, 0))
            mem_peak.update(mem_after)

            # Extract average confidence and area from analyzer
            stats = analyzer.statistics()
            avg_conf = stats.get("average_confidence", 0.0) if stats else 0.0
            avg_area = stats.get("average_area", 0.0) if stats else 0.0

            # Build result
            result = PipelineResult(
                success=True,
                image_path=str(image_path),
                output_dir=output_dir,
                total_particles=len(analyzer),
                coverage=estimator.coverage_percentage(),
                average_confidence=avg_conf,
                average_area=avg_area,
                image_width=image.shape[1],
                image_height=image.shape[0],
                processing_times=stage_times,
                memory_usage=mem_peak,
                version_info=self._get_version_info(),
            )

            if self.save_outputs:
                vis_files = visualizer.collect_visualizations() if self.save_outputs else []
                result.visualizations = {
                    "directory": str(visualizer.output_dir),
                    "files": [str(p) for p in vis_files],
                }
                result.reports = {
                    "directory": str(report_gen.report_dir),
                    "files": [
                        "report.json",
                        "analysis_summary.csv",
                        "report.html",
                        "metadata.json",
                        "statistics.json",
                    ],
                }

            if return_objects:
                result.analyzer = analyzer
                result.estimator = estimator
                result.visualizer = visualizer
                result.report_generator = report_gen

            result.detections = detections

            logger.info(f"Successfully processed: {image_path}")

        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            result = PipelineResult(success=False, image_path=str(image_path), output_dir=output_dir, error=str(e))
        except ValueError as e:
            logger.error(f"Value error: {e}")
            result = PipelineResult(success=False, image_path=str(image_path), output_dir=output_dir, error=str(e))
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            result = PipelineResult(success=False, image_path=str(image_path), output_dir=output_dir, error=str(e))
        except OSError as e:
            logger.error(f"OS error: {e}")
            result = PipelineResult(success=False, image_path=str(image_path), output_dir=output_dir, error=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            result = PipelineResult(success=False, image_path=str(image_path), output_dir=output_dir, error=str(e))

        # Add total processing time (ms)
        result.processing_times["total"] = (time.time() - start_time) * 1000

        # Optional GPU cache cleanup
        if self.device == "cuda" and torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()

        return result

    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Path] = None,
        recursive: bool = False,
        show_progress: bool = True,
        save_original: bool = True,
    ) -> List[PipelineResult]:
        """
        Process all images in a directory.

        Args:
            input_dir: Directory containing images.
            output_dir: Root output directory (subdirectories will be created per image).
            recursive: If True, search subdirectories recursively.
            show_progress: If True, display a progress bar.
            save_original: If True, copy original images to output.

        Returns:
            List of PipelineResult objects.
        """
        input_dir = Path(input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Gather image paths
        if recursive:
            all_files = list(input_dir.rglob("*"))
        else:
            all_files = list(input_dir.glob("*"))

        image_paths = [p for p in all_files if p.suffix.lower() in self.extensions]
        if not image_paths:
            logger.warning(f"No images found in {input_dir}")
            return []

        logger.info(f"Found {len(image_paths)} images to process")
        results = []
        base_output = Path(output_dir) if output_dir else self.output_dir

        iterator = tqdm(image_paths, desc="Processing images") if show_progress else image_paths

        for img_path in iterator:
            # Create per‑image output folder
            if recursive:
                rel_path = img_path.relative_to(input_dir).parent
                img_output = base_output / rel_path / img_path.stem
            else:
                img_output = base_output / img_path.stem

            result = self.process_image(
                img_path,
                output_dir=img_output,
                return_objects=False,
                save_original=save_original,
            )
            results.append(result)

            if not result.success:
                logger.warning(f"Failed to process: {img_path}")

        # Generate batch summary
        if self.save_outputs:
            self._generate_batch_summary(results, base_output)

        successful = sum(1 for r in results if r.success)
        logger.info(f"Directory processing complete: {successful}/{len(results)} successful")
        return results

    def _generate_batch_summary(self, results: List[PipelineResult], output_dir: Path) -> None:
        """Generate a CSV summary for the entire batch."""
        import csv

        summary_path = output_dir / "batch_summary.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        rows = []
        for r in results:
            if r.success:
                rows.append({
                    "image": Path(r.image_path).name,
                    "particles": r.total_particles,
                    "coverage_%": round(r.coverage, 2),
                    "avg_confidence": round(r.average_confidence, 3),
                    "avg_area_px2": round(r.average_area, 1),
                    "image_width": r.image_width,
                    "image_height": r.image_height,
                    "detection_time_ms": round(r.processing_times.get("detection", 0), 1),
                    "total_time_ms": round(r.processing_times.get("total", 0), 1),
                    "success": True,
                })
            else:
                rows.append({
                    "image": Path(r.image_path).name,
                    "particles": 0,
                    "coverage_%": 0,
                    "avg_confidence": 0,
                    "avg_area_px2": 0,
                    "image_width": 0,
                    "image_height": 0,
                    "detection_time_ms": 0,
                    "total_time_ms": 0,
                    "success": False,
                    "error": r.error,
                })

        if not rows:
            return

        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"Batch summary saved to {summary_path}")

        # Print stats
        successful = [r for r in rows if r["success"]]
        if successful:
            avg_particles = sum(r["particles"] for r in successful) / len(successful)
            avg_coverage = sum(r["coverage_%"] for r in successful) / len(successful)
            avg_conf = sum(r["avg_confidence"] for r in successful) / len(successful)
            logger.info(f"Batch stats: {len(successful)} successful, "
                        f"avg particles: {avg_particles:.1f}, "
                        f"avg coverage: {avg_coverage:.2f}%, "
                        f"avg confidence: {avg_conf:.3f}")

    # ----------------------------------------------------------------------
    # Special methods
    # ----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"MicroplasticPipeline(model='{self.model_name}', "
            f"conf={self.conf_threshold}, device='{self.device}')"
        )


# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = MicroplasticPipeline()
    result = pipeline.process_image("sample.jpg")
    print(f"Processed: {result.image_path}, Particles: {result.total_particles}")