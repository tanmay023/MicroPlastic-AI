"""
=========================================================
Microplastic Detection Engine

Author : Tanmay
Project : MicroPlastic-AI
=========================================================
"""

from pathlib import Path
import time
import cv2
from ultralytics import YOLO
from microplastic_ai.analysis.particle_analysis import ParticleAnalyzer

from microplastic_ai.config import (
    BEST_MODEL,
    TEST_IMAGES_DIR,
    DETECTIONS_DIR,
    CONFIDENCE_THRESHOLD,
    BOX_COLOR,
    TEXT_COLOR,
    BOX_THICKNESS,
    FONT_SCALE,
    FONT_THICKNESS,
)


class MicroplasticDetector:
    """
    YOLO11 Microplastic Detection Engine.
    """

    def __init__(self):

        print("=" * 60)
        print("LOADING YOLO11 MODEL")
        print("=" * 60)

        if not BEST_MODEL.exists():
            raise FileNotFoundError(
                f"Model not found:\n{BEST_MODEL}"
            )

        self.model = YOLO(str(BEST_MODEL))

        print("✓ Model Loaded Successfully")
        print()

    def detect(self, image_path: Path):

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        image = cv2.imread(str(image_path))

        start = time.perf_counter()

        results = self.model.predict(
            source=image,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        inference_time = (
            time.perf_counter() - start
        ) * 1000

        result = results[0]

        boxes = result.boxes
        analyzer = ParticleAnalyzer()

        particle_count = len(boxes)

        confidences = []

        for box in boxes:

            confidences.append(
                float(box.conf[0])
            )

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            confidence = float(box.conf[0])

            analyzer.add_particle(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                confidence=confidence
            )

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                BOX_COLOR,
                BOX_THICKNESS
            )

            cv2.putText(
                image,
                f"{confidence:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                FONT_SCALE,
                TEXT_COLOR,
                FONT_THICKNESS
            )

        output_path = (
            DETECTIONS_DIR /
            f"{image_path.stem}_detected.jpg"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            str(output_path),
            image
        )

        if confidences:

            average_confidence = (
                sum(confidences) /
                len(confidences)
            )

            maximum_confidence = max(confidences)

            minimum_confidence = min(confidences)

        else:

            average_confidence = 0
            maximum_confidence = 0
            minimum_confidence = 0

        print("=" * 60)
        print("DETECTION SUMMARY")
        print("=" * 60)

        print(f"Image               : {image_path.name}")
        print(f"Particles Detected  : {particle_count}")
        print(f"Average Confidence  : {average_confidence:.3f}")
        print(f"Maximum Confidence  : {maximum_confidence:.3f}")
        print(f"Minimum Confidence  : {minimum_confidence:.3f}")
        print(f"Inference Time      : {inference_time:.2f} ms")
        print(f"Saved Output        : {output_path}")

        print("=" * 60)
        summary = analyzer.print_summary()

        return {
            "image": image_path.name,
            "particle_count": particle_count,
            "average_confidence": average_confidence,
            "maximum_confidence": maximum_confidence,
            "minimum_confidence": minimum_confidence,
            "inference_time_ms": inference_time,
            "output_image": output_path,
            "particle_analysis": summary
        }


def main():

    detector = MicroplasticDetector()

    images = sorted(TEST_IMAGES_DIR.glob("*"))

    if not images:
        print("No test images found.")
        return

    detector.detect(images[0])


if __name__ == "__main__":
    main()