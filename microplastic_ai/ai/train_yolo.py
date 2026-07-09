"""
=========================================================
YOLO11 Training

Author : Tanmay
Project : MicroPlastic-AI
=========================================================
"""

from pathlib import Path
from ultralytics import YOLO


class YOLOTrainer:
    """
    Train YOLO11 model for Microplastic Detection.
    """

    def __init__(self):

        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.data_yaml = (
            self.project_root
            / "dataset"
            / "yolo"
            / "data.yaml"
        )

        self.model = YOLO("yolo11n.pt")

    def train(self):

        print("=" * 60)
        print("MICROPLASTIC YOLO11 TRAINING")
        print("=" * 60)

        print(f"Dataset : {self.data_yaml}")
        print("Model   : YOLO11n")
        print("Device  : CUDA GPU")
        print("Epochs  : 50")
        print()

        results = self.model.train(

            # Dataset
            data=str(self.data_yaml),

            # Training
            epochs=50,
            imgsz=640,
            batch=8,

            # Hardware
            device=0,
            workers=0,

            # Performance
            cache=False,
            amp=True,
            pretrained=True,

            # Optimization
            optimizer="auto",
            cos_lr=True,
            patience=15,

            # Saving
            project="models",
            name="microplastic_yolo11n",
            exist_ok=True,
            save=True,
            save_period=10,

            # Visualization
            plots=True,
            verbose=True,
        )

        print("\n")
        print("=" * 60)
        print("TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print("\nBest model saved at:")

        print(
            self.project_root
            / "models"
            / "microplastic_yolo11n"
            / "weights"
            / "best.pt"
        )

        return results

    def export(self):

        print("\nExporting model to ONNX...\n")

        self.model.export(format="onnx")

        print("Model exported successfully.")

    def run(self):

        self.train()

        # Export later if required
        # self.export()


if __name__ == "__main__":

    trainer = YOLOTrainer()

    trainer.run()