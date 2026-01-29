"""Core detection schemas."""

from __future__ import annotations

from typing import List, TypedDict


class DetectionItem(TypedDict):
    bbox: List[int]
    confidence: float


class DetectionResults(TypedDict):
    faces: List[DetectionItem]
    license_plates: List[DetectionItem]
