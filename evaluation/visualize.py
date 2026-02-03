"""Visualization utilities for FP/FN analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import cv2


def draw_boxes(image, boxes: List[Dict], color, label: str):
    out = image.copy()
    for b in boxes:
        x1, y1, x2, y2 = map(int, [b["x1"], b["y1"], b["x2"], b["y2"]])
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        cv2.putText(out, label, (x1, max(0, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return out


def save_error_visual(
    image,
    gts: List[Dict],
    fps: List[Dict],
    fns: List[Dict],
    out_path: Path,
):
    out = image.copy()
    out = draw_boxes(out, gts, (0, 255, 0), "GT")
    out = draw_boxes(out, fns, (0, 0, 255), "FN")
    out = draw_boxes(out, fps, (0, 255, 255), "FP")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), out)
