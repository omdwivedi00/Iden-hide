"""WIDER FACE dataset adapter.

Expected structure (common WIDER layout):
- {root}/WIDER_train/images/... or {root}/images/...
- Annotation file: {root}/wider_face_train_bbx_gt.txt or {root}/wider_face_val_bbx_gt.txt

This adapter reads the official WIDER Face text format.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import cv2
import numpy as np

from .base import DatasetAdapter


class WiderFaceAdapter(DatasetAdapter):
    def __init__(self, root: str, split: str = "val"):
        self.root = Path(root)
        self.split = split
        self.images_dir = self._resolve_images_dir()
        self.ann_file = self._resolve_ann_file()
        self.index = self._load_index()

    def _resolve_images_dir(self) -> Path:
        candidates = [
            self.root / "WIDER_val" / "images",
            self.root / "WIDER_train" / "images",
            self.root / "images",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError("WIDERFace images folder not found in dataset_root")

    def _resolve_ann_file(self) -> Path:
        candidates = [
            self.root / "wider_face_val_bbx_gt.txt",
            self.root / "wider_face_train_bbx_gt.txt",
            self.root / "wider_face_bbx_gt.txt",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError("WIDERFace annotation txt not found in dataset_root")

    def _load_index(self):
        # WIDER Face format:
        # <image_path>
        # <num_faces>
        # x y w h blur expression illumination invalid occlusion pose
        lines = self.ann_file.read_text().strip().splitlines()
        i = 0
        entries = []
        while i < len(lines):
            img_rel = lines[i].strip()
            i += 1
            if not img_rel:
                continue
            num = int(lines[i].strip())
            i += 1
            boxes = []
            for _ in range(num):
                parts = lines[i].strip().split()
                i += 1
                if len(parts) < 4:
                    continue
                x, y, w, h = map(float, parts[:4])
                x1, y1, x2, y2 = x, y, x + w, y + h
                boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "label": "face"})
            entries.append((img_rel, boxes))
        return entries

    def __len__(self) -> int:
        return len(self.index)

    def get_image(self, idx: int) -> np.ndarray:
        img_rel, _ = self.index[idx]
        img_path = self.images_dir / img_rel
        img = cv2.imread(str(img_path))
        if img is None:
            raise FileNotFoundError(f"Image not found: {img_path}")
        return img

    def get_annotations(self, idx: int) -> List[Dict]:
        return self.index[idx][1]

    def image_id(self, idx: int) -> str:
        img_rel, _ = self.index[idx]
        return img_rel.replace("/", "_")
