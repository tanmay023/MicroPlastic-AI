"""
=========================================================
Utility Functions
=========================================================
"""

from pathlib import Path
import shutil


def create_directory(directory: Path):
    """
    Create directory if it does not exist.
    """
    directory.mkdir(parents=True, exist_ok=True)


def copy_file(source: Path, destination: Path):
    """
    Copy a file preserving metadata.
    """
    shutil.copy2(source, destination)


def print_heading(title: str):
    """
    Print formatted heading.
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)