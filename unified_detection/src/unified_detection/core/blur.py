"""
Visualization + Blurring Module (optimized)

Upgrades:
- Faster oval blur application (no per-channel Python loop)
- Defensive bbox clamping
"""

from __future__ import annotations

import cv2
import numpy as np
from typing import List, Dict, Union


class DetectionVisualizer:
    def __init__(self):
        self.colors = {
            "face": (0, 255, 0),
            "license_plate": (0, 0, 255),
        }
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_boxes(self, image: np.ndarray, results: Dict[str, List[Dict]], show_confidence: bool = True) -> np.ndarray:
        out = image.copy()

        for face in results.get("faces", []):
            bbox = face["bbox"]
            conf = float(face.get("confidence", 0.0))
            self._draw_single_box(out, bbox, "face", conf, show_confidence)

        for plate in results.get("license_plates", []):
            bbox = plate["bbox"]
            conf = float(plate.get("confidence", 0.0))
            self._draw_single_box(out, bbox, "license_plate", conf, show_confidence)

        return out

    def _draw_single_box(self, image: np.ndarray, bbox: List[int], label: str, confidence: float, show_confidence: bool):
        x1, y1, x2, y2 = [int(v) for v in bbox]
        color = self.colors.get(label, (255, 0, 0))

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        label_text = f"{label}: {confidence:.3f}" if show_confidence else label
        label_size = cv2.getTextSize(label_text, self.font, 0.6, 2)[0]

        y_text_top = max(0, y1 - label_size[1] - 10)
        cv2.rectangle(image, (x1, y_text_top), (x1 + label_size[0], y1), color, -1)
        cv2.putText(image, label_text, (x1, y1 - 5), self.font, 0.6, (255, 255, 255), 2)

    @staticmethod
    def _odd(k: int) -> int:
        k = int(k)
        if k < 1:
            k = 1
        return k + 1 if (k % 2 == 0) else k

    def blur_face_oval(self, image: np.ndarray, bbox: List[float], blur_strength: int = 15) -> np.ndarray:
        """Blur face region with an oval mask."""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1 = max(0, min(w - 1, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h - 1, y1))
        y2 = max(0, min(h, y2))

        if x2 <= x1 or y2 <= y1:
            return image

        k = self._odd(blur_strength)

        out = image.copy()
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return out

        blurred_region = cv2.GaussianBlur(region, (k, k), 0)

        # Build oval mask in ROI only (cheaper than full-frame mask)
        rh, rw = (y2 - y1), (x2 - x1)
        mask = np.zeros((rh, rw), dtype=np.uint8)
        cx, cy = rw // 2, rh // 2
        ax, ay = max(1, rw // 2), max(1, rh // 2)
        cv2.ellipse(mask, (cx, cy), (ax, ay), 0, 0, 360, 255, -1)

        m = mask.astype(bool)
        # broadcast mask to 3 channels
        out_roi = out[y1:y2, x1:x2]
        out_roi[m] = blurred_region[m]
        out[y1:y2, x1:x2] = out_roi
        return out

    def blur_rectangle_region(self, image: np.ndarray, bbox: List[float], blur_strength: int = 15) -> np.ndarray:
        """Blur a rectangular region (for license plates)."""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1 = max(0, min(w - 1, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h - 1, y1))
        y2 = max(0, min(h, y2))
        if x2 <= x1 or y2 <= y1:
            return image

        k = self._odd(blur_strength)
        out = image.copy()
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return out
        out[y1:y2, x1:x2] = cv2.GaussianBlur(region, (k, k), 0)
        return out

    def blur_detections(self, image: np.ndarray, results: Dict[str, List], face_blur_strength: int = 15, plate_blur_strength: int = 15) -> np.ndarray:
        """Blur all detected faces and license plates."""
        out = image.copy()

        for face in results.get("faces", []):
            if isinstance(face, dict) and "bbox" in face:
                bbox = face["bbox"]
            elif isinstance(face, list) and len(face) >= 4:
                bbox = face[:4]
            else:
                continue
            out = self.blur_face_oval(out, bbox, face_blur_strength)

        for plate in results.get("license_plates", []):
            if isinstance(plate, dict) and "bbox" in plate:
                bbox = plate["bbox"]
            elif isinstance(plate, list) and len(plate) >= 4:
                bbox = plate[:4]
            else:
                continue
            out = self.blur_rectangle_region(out, bbox, plate_blur_strength)

        return out


__all__ = ["DetectionVisualizer"]
