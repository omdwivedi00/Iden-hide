"""Batch dataset runner using UnifiedDetector.detect_objects_batch()."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, List

import cv2

from ..config import Settings
from ..logging import configure_logging, get_logger
from ..core.detector import UnifiedDetector
from ..core.blur import DetectionVisualizer

logger = get_logger(__name__)


def _load_images(image_dir: Path) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([p for p in image_dir.iterdir() if p.suffix.lower() in exts])


def _chunked(items: List[Path], batch_size: int) -> Iterable[List[Path]]:
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def main() -> None:
    parser = argparse.ArgumentParser("Unified Detection Dataset Runner")
    parser.add_argument("--input_dir", required=True, help="Directory with images")
    parser.add_argument("--out_dir", required=True, help="Output directory")
    parser.add_argument("--batch", type=int, default=4, help="Batch size")
    parser.add_argument("--blur", action="store_true", help="Apply blur on outputs")
    args = parser.parse_args()

    settings = Settings()
    configure_logging(settings.log_level)

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detector = UnifiedDetector(settings=settings, batch_size=args.batch)
    visualizer = DetectionVisualizer()

    image_paths = _load_images(input_dir)
    if not image_paths:
        raise RuntimeError("No images found in input directory")

    logger.info("Running dataset detection on device: %s", settings.device)
    logger.info("Batch size: %s", args.batch)
    logger.info("Found %s images", len(image_paths))

    timings: List[float] = []
    results_file = out_dir / "results.jsonl"

    with results_file.open("w", encoding="utf-8") as fout:
        for batch_paths in _chunked(image_paths, args.batch):
            images = []
            names = []
            for p in batch_paths:
                img = cv2.imread(str(p))
                if img is None:
                    logger.warning("Failed to load image: %s", p)
                    continue
                images.append(img)
                names.append(p.name)

            if not images:
                continue

            t0 = time.time()
            batch_results = detector.detect_objects_batch(images)
            t1 = time.time()

            batch_time = (t1 - t0) / len(batch_results)
            timings.extend([batch_time] * len(batch_results))

            for img, name, result in zip(images, names, batch_results):
                record = {
                    "image": name,
                    "faces": result.get("faces", []),
                    "license_plates": result.get("license_plates", []),
                }
                fout.write(json.dumps(record) + "\n")

                if args.blur:
                    blurred = visualizer.blur_detections(
                        img,
                        result,
                        face_blur_strength=settings.face_blur_strength,
                        plate_blur_strength=settings.plate_blur_strength,
                    )
                    cv2.imwrite(str(out_dir / f"{name}_blurred.jpg"), blurred)

    timings.sort()
    avg = sum(timings) / len(timings)
    p95 = timings[int(0.95 * len(timings))]

    logger.info("Dataset processing complete")
    logger.info("Images processed: %s", len(image_paths))
    logger.info("Avg time / image: %.3fs", avg)
    logger.info("P95 time / image: %.3fs", p95)
    logger.info("Results saved to: %s", results_file)
    logger.info("Outputs saved to: %s", out_dir)


if __name__ == "__main__":
    main()
