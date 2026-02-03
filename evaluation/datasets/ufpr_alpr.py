"""UFPR-ALPR dataset adapter (license plates).

Expected structure (common):
- {root}/UFPR-ALPR/images/*.jpg
- {root}/UFPR-ALPR/annotations/*.txt  (one file per image)

Annotation format per line (common):
class_id x y w h  (YOLO format, normalized)

If your dataset differs, adapt _load_annotation_file accordingly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import cv2
import numpy as np

from .base import DatasetAdapter


class UFPRALPRAdapter(DatasetAdapter):
    def __init__(self, root: str):
        self.root = Path(root)
        self.images_dir = self._resolve_images_dir()
        self.ann_dir = self._resolve_ann_dir()
        self.images = sorted([p for p in self.images_dir.glob("*.jpg")])
        if not self.images:
            self.images = sorted([p for p in self.images_dir.glob("*.png")])
        if not self.images:
            raise FileNotFoundError("No images found in UFPR-ALPR dataset_root")

    def _resolve_images_dir(self) -> Path:
        candidates = [
            self.root / "UFPR-ALPR" / "images",
            self.root / "images",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError("UFPR-ALPR images folder not found in dataset_root")

    def _resolve_ann_dir(self) -> Path:
        candidates = [
            self.root / "UFPR-ALPR" / "annotations",
            self.root / "annotations",
            self.root / "labels",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError("UFPR-ALPR annotations folder not found in dataset_root")

    def __len__(self) -> int:
        return len(self.images)

    def _load_annotation_file(self, image_path: Path) -> List[Dict]:
        ann_path = (self.ann_dir / image_path.with_suffix(".txt").name)
        if not ann_path.exists():
            return []
        lines = ann_path.read_text().strip().splitlines()
        boxes = []
        img = cv2.imread(str(image_path))
        if img is None:
            return []
        h, w = img.shape[:2]
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            _, cx, cy, bw, bh = map(float, parts[:5])
            x1 = (cx - bw / 2) * w
            y1 = (cy - bh / 2) * h
            x2 = (cx + bw / 2) * w
            y2 = (cy + bh / 2) * h
            boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "label": "license_plate"})
        return boxes

    def get_image(self, idx: int) -> np.ndarray:
        img_path = self.images[idx]
        img = cv2.imread(str(img_path))
        if img is None:
            raise FileNotFoundError(f"Image not found: {img_path}")
        return img

    def get_annotations(self, idx: int) -> List[Dict]:
        return self._load_annotation_file(self.images[idx])

    def image_id(self, idx: int) -> str:
        return self.images[idx].stem
