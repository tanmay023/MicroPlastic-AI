
# INTIAL FILE (08/JULY/2026)

# """
# =========================================================
# MicroPlastic-AI Configuration
# =========================================================
# """

# from pathlib import Path

# # --------------------------------------------------
# # Project Root
# # --------------------------------------------------

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# # --------------------------------------------------
# # Dataset Paths
# # --------------------------------------------------

# DATASET_DIR = PROJECT_ROOT / "dataset"

# ORIGINAL_DATASET = DATASET_DIR / "original"
# YOLO_DATASET = DATASET_DIR / "yolo"

# TRAIN_DIR = ORIGINAL_DATASET / "train"
# VALID_DIR = ORIGINAL_DATASET / "valid"

# YOLO_TRAIN_IMAGES = YOLO_DATASET / "train" / "images"
# YOLO_TRAIN_LABELS = YOLO_DATASET / "train" / "labels"

# YOLO_VALID_IMAGES = YOLO_DATASET / "valid" / "images"
# YOLO_VALID_LABELS = YOLO_DATASET / "valid" / "labels"

# DATA_YAML = YOLO_DATASET / "data.yaml"

# # --------------------------------------------------
# # Output Paths
# # --------------------------------------------------

# OUTPUT_DIR = PROJECT_ROOT / "outputs"

# REPORTS_DIR = OUTPUT_DIR / "reports"
# GRAPHS_DIR = OUTPUT_DIR / "graphs"
# DETECTIONS_DIR = OUTPUT_DIR / "detections"
# LOGS_DIR = OUTPUT_DIR / "logs"

# # --------------------------------------------------
# # Models
# # --------------------------------------------------

# MODEL_DIR = PROJECT_ROOT / "models"

# WEIGHTS_DIR = MODEL_DIR / "weights"
# CHECKPOINT_DIR = MODEL_DIR / "checkpoints"

# # --------------------------------------------------
# # Class Mapping
# # --------------------------------------------------

# CLASSES = {
#     "Microplastic": 0
# }

# NUM_CLASSES = len(CLASSES)



# FIRST UPDATE AFTER FIRST TRAINING (09/JULY/2026)

# """
# =========================================================
# MicroPlastic-AI Configuration

# Author : Tanmay
# Project : MicroPlastic-AI
# =========================================================
# """

# from pathlib import Path

# # ======================================================
# # Project Root
# # ======================================================

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# # ======================================================
# # Dataset Paths
# # ======================================================

# DATASET_DIR = PROJECT_ROOT / "dataset"

# ORIGINAL_DATASET = DATASET_DIR / "original"
# YOLO_DATASET = DATASET_DIR / "yolo"

# TRAIN_DIR = ORIGINAL_DATASET / "train"
# VALID_DIR = ORIGINAL_DATASET / "valid"

# YOLO_TRAIN_IMAGES = YOLO_DATASET / "train" / "images"
# YOLO_TRAIN_LABELS = YOLO_DATASET / "train" / "labels"

# YOLO_VALID_IMAGES = YOLO_DATASET / "valid" / "images"
# YOLO_VALID_LABELS = YOLO_DATASET / "valid" / "labels"

# DATA_YAML = YOLO_DATASET / "data.yaml"

# # ======================================================
# # Image Directories
# # ======================================================

# IMAGES_DIR = PROJECT_ROOT / "images"

# TEST_IMAGES_DIR = IMAGES_DIR / "test"
# OUTPUT_IMAGES_DIR = IMAGES_DIR / "output"

# # ======================================================
# # Output Directories
# # ======================================================

# OUTPUT_DIR = PROJECT_ROOT / "outputs"

# REPORTS_DIR = OUTPUT_DIR / "reports"
# GRAPHS_DIR = OUTPUT_DIR / "graphs"
# DETECTIONS_DIR = OUTPUT_DIR / "detections"
# LOGS_DIR = OUTPUT_DIR / "logs"

# # ======================================================
# # Model Directories
# # ======================================================

# MODEL_DIR = PROJECT_ROOT / "models"

# WEIGHTS_DIR = MODEL_DIR / "weights"
# CHECKPOINT_DIR = MODEL_DIR / "checkpoints"

# # ======================================================
# # YOLO Training Results
# # ======================================================

# RUNS_DIR = PROJECT_ROOT / "runs"

# YOLO_RUN_DIR = (
#     RUNS_DIR
#     / "detect"
#     / "models"
#     / "microplastic_yolo11n"
# )

# YOLO_WEIGHT_DIR = YOLO_RUN_DIR / "weights"

# BEST_MODEL = YOLO_WEIGHT_DIR / "best.pt"
# LAST_MODEL = YOLO_WEIGHT_DIR / "last.pt"

# # ======================================================
# # Classes
# # ======================================================

# CLASS_NAMES = [
#     "Microplastic"
# ]

# CLASSES = {
#     "Microplastic": 0
# }

# NUM_CLASSES = len(CLASS_NAMES)

# # ======================================================
# # Detection Parameters
# # ======================================================

# IMAGE_SIZE = 640

# CONFIDENCE_THRESHOLD = 0.25
# IOU_THRESHOLD = 0.45
# MAX_DETECTIONS = 1000

# # ======================================================
# # Drawing Parameters
# # ======================================================

# BOX_COLOR = (0, 255, 0)          # Green
# TEXT_COLOR = (255, 255, 255)     # White
# TEXT_BACKGROUND = (0, 150, 0)

# BOX_THICKNESS = 2
# FONT_SCALE = 0.6
# FONT_THICKNESS = 2

# # ======================================================
# # Particle Analysis
# # ======================================================

# MICRONS_PER_PIXEL = None

# # Set after microscope calibration
# # Example:
# # MICRONS_PER_PIXEL = 0.82

# # ======================================================
# # Supported File Types
# # ======================================================

# IMAGE_EXTENSIONS = (
#     ".jpg",
#     ".jpeg",
#     ".png",
#     ".bmp",
#     ".tif",
#     ".tiff"
# )

# # ======================================================
# # Dashboard
# # ======================================================

# APP_TITLE = "MicroPlastic-AI"

# APP_DESCRIPTION = (
#     "AI-powered Microplastic Detection, "
#     "Particle Counting and Density Estimation"
# )

# # ======================================================
# # Device
# # ======================================================

# DEFAULT_DEVICE = 0       # GPU

# # Use:
# # DEFAULT_DEVICE = "cpu"
# # if CUDA is unavailable.


# AFTER FIRST TRAINING (09/JULY/2026) AND ADDING GUI (09/JULY/2026)

"""
=========================================================
MicroPlastic-AI Configuration

Author : Tanmay
Project : MicroPlastic-AI
=========================================================
"""

from pathlib import Path

# ======================================================
# Project Root
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ======================================================
# Dataset Paths
# ======================================================

DATASET_DIR = PROJECT_ROOT / "dataset"

ORIGINAL_DATASET = DATASET_DIR / "original"
YOLO_DATASET = DATASET_DIR / "yolo"

TRAIN_DIR = ORIGINAL_DATASET / "train"
VALID_DIR = ORIGINAL_DATASET / "valid"

YOLO_TRAIN_IMAGES = YOLO_DATASET / "train" / "images"
YOLO_TRAIN_LABELS = YOLO_DATASET / "train" / "labels"

YOLO_VALID_IMAGES = YOLO_DATASET / "valid" / "images"
YOLO_VALID_LABELS = YOLO_DATASET / "valid" / "labels"

DATA_YAML = YOLO_DATASET / "data.yaml"

# ======================================================
# Image Directories
# ======================================================

IMAGES_DIR = PROJECT_ROOT / "images"

TEST_IMAGES_DIR = IMAGES_DIR / "test"
OUTPUT_IMAGES_DIR = IMAGES_DIR / "output"

# ======================================================
# Output Directories
# ======================================================

OUTPUT_DIR = PROJECT_ROOT / "outputs"

REPORTS_DIR = OUTPUT_DIR / "reports"
GRAPHS_DIR = OUTPUT_DIR / "graphs"
DETECTIONS_DIR = OUTPUT_DIR / "detections"
LOGS_DIR = OUTPUT_DIR / "logs"

# ======================================================
# Model Directories
# ======================================================

MODEL_DIR = PROJECT_ROOT / "models"

WEIGHTS_DIR = MODEL_DIR / "weights"
CHECKPOINT_DIR = MODEL_DIR / "checkpoints"

# ======================================================
# YOLO Training Results
# ======================================================

RUNS_DIR = PROJECT_ROOT / "runs"

YOLO_RUN_DIR = (
    RUNS_DIR
    / "detect"
    / "models"
    / "microplastic_yolo11n"
)

YOLO_WEIGHT_DIR = YOLO_RUN_DIR / "weights"

BEST_MODEL = YOLO_WEIGHT_DIR / "best.pt"
LAST_MODEL = YOLO_WEIGHT_DIR / "last.pt"

# Alias for pipeline
MODEL_PATH = BEST_MODEL

# ======================================================
# Classes
# ======================================================

CLASS_NAMES = [
    "Microplastic"
]

CLASSES = {
    "Microplastic": 0
}

NUM_CLASSES = len(CLASS_NAMES)

# ======================================================
# Detection Parameters
# ======================================================

IMAGE_SIZE = 640

CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
MAX_DETECTIONS = 1000

# ======================================================
# Drawing Parameters
# ======================================================

BOX_COLOR = (0, 255, 0)          # Green
TEXT_COLOR = (255, 255, 255)     # White
TEXT_BACKGROUND = (0, 150, 0)

BOX_THICKNESS = 2
FONT_SCALE = 0.6
FONT_THICKNESS = 2

# ======================================================
# Particle Analysis
# ======================================================

MICRONS_PER_PIXEL = None

# Set after microscope calibration
# Example:
# MICRONS_PER_PIXEL = 0.82

# ======================================================
# Supported File Types
# ======================================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
)

# ======================================================
# Pipeline Configuration
# ======================================================

SAVE_OUTPUTS = True
DEFAULT_DEVICE = "auto"          # 'auto', 'cpu', or 'cuda'
DEVICE = DEFAULT_DEVICE          # <-- FIX: Alias for backward compatibility
USE_TIMESTAMP = False            # Add date to output folders

# ======================================================
# Visualization Configuration
# ======================================================

VISUALIZATION_DIR = OUTPUT_DIR / "visualizations"
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
HISTOGRAM_BINS = 20
HEATMAP_KERNEL_SIZE = 51         # Must be odd
SCATTER_POINT_SIZE = 40
FIG_SIZE = (10, 10)
HIST_SIZE = (8, 6)
DEFAULT_COLORMAP = "inferno"

# ======================================================
# Report Configuration
# ======================================================

REPORT_DIR = OUTPUT_DIR / "reports"
PROJECT_NAME = "MicroPlastic-AI"
AUTHOR = "Tanmay"
MODEL_NAME = "YOLO11n"

# ======================================================
# GUI Configuration
# ======================================================

APP_TITLE = "MicroPlastic-AI"
APP_DESCRIPTION = (
    "AI-powered Microplastic Detection, "
    "Particle Counting and Density Estimation"
)

# ======================================================
# Logging
# ======================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ======================================================
# Device (Legacy Support)
# ======================================================

# Kept for backward compatibility
DEFAULT_DEVICE_LEGACY = 0        # GPU