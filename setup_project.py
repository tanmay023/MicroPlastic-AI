"""
=========================================================
MicroPlastic-AI Project Setup
Author : Tanmay
Purpose : Create the complete folder structure
=========================================================
"""

from pathlib import Path

# ------------------------------------------------------
# Folder Structure
# ------------------------------------------------------

folders = [

    # Dataset
    "dataset",
    "dataset/original",
    "dataset/original/train",
    "dataset/original/valid",

    "dataset/yolo",
    "dataset/yolo/train",
    "dataset/yolo/train/images",
    "dataset/yolo/train/labels",

    "dataset/yolo/valid",
    "dataset/yolo/valid/images",
    "dataset/yolo/valid/labels",

    # Source Code
    "microplastic_ai",
    "microplastic_ai/dataset",
    "microplastic_ai/ai",
    "microplastic_ai/vision",
    "microplastic_ai/iot",
    "microplastic_ai/dashboard",

    # Models
    "models",
    "models/checkpoints",
    "models/weights",

    # Outputs
    "outputs",
    "outputs/detections",
    "outputs/reports",
    "outputs/graphs",
    "outputs/logs",

    # Documentation
    "docs",

    # Notebooks
    "notebooks",

    # Tests
    "tests",
]

# ------------------------------------------------------
# Files
# ------------------------------------------------------

files = [

    # Root Files
    "README.md",
    ".gitignore",
    "requirements.txt",
    "main.py",

    # Package
    "microplastic_ai/__init__.py",
    "microplastic_ai/config.py",
    "microplastic_ai/utils.py",

    # Dataset
    "microplastic_ai/dataset/__init__.py",
    "microplastic_ai/dataset/convert_to_yolo.py",
    "microplastic_ai/dataset/dataset_analysis.py",

    # AI
    "microplastic_ai/ai/__init__.py",
    "microplastic_ai/ai/train_yolo.py",
    "microplastic_ai/ai/detect.py",

    # Vision
    "microplastic_ai/vision/__init__.py",
    "microplastic_ai/vision/particle_analysis.py",
    "microplastic_ai/vision/density_estimation.py",

    # IoT
    "microplastic_ai/iot/__init__.py",
    "microplastic_ai/iot/raspberry_pi.py",
    "microplastic_ai/iot/camera.py",
    "microplastic_ai/iot/sensors.py",

    # Dashboard
    "microplastic_ai/dashboard/__init__.py",
    "microplastic_ai/dashboard/app.py",

    # Dataset
    "dataset/yolo/data.yaml",
]

# ------------------------------------------------------
# Create Folders
# ------------------------------------------------------

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------
# Create Files
# ------------------------------------------------------

for file in files:
    path = Path(file)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

print("=" * 60)
print("✅ MicroPlastic-AI Project Structure Created Successfully")
print("=" * 60)

print(f"Folders Created : {len(folders)}")
print(f"Files Created   : {len(files)}")

print("\nNext Steps:")
print("1. Copy your Kaggle dataset to:")
print("   dataset/original/train/")
print("   dataset/original/valid/")
print("\n2. We'll implement:")
print("   ✔ config.py")
print("   ✔ utils.py")
print("   ✔ convert_to_yolo.py")
print("   ✔ dataset_analysis.py")
print("   ✔ train_yolo.py")