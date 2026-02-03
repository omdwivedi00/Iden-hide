"""Core detection logic (no API dependencies)."""

from .detector import UnifiedDetector
from .face_base import BaseFaceDetector
from .face_cascade import CascadeFaceDetector
from .face_yolo import YoloFaceDetector
from .face_scrfd import ScrfdFaceDetector
from .license_plate import DetectLP

__all__ = [
    "UnifiedDetector",
    "BaseFaceDetector",
    "CascadeFaceDetector",
    "YoloFaceDetector",
    "ScrfdFaceDetector",
    "DetectLP",
]
