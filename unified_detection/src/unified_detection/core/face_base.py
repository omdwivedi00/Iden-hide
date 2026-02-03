"""Base interface for face detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List
import numpy as np


class BaseFaceDetector(ABC):
    """Abstract base class for face detectors."""

    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """Detect faces in a single image."""
        raise NotImplementedError

    @abstractmethod
    def detect_faces_batch(self, images: List[np.ndarray], batch: int = 8) -> List[List[Dict]]:
        """Detect faces in a batch of images."""
        raise NotImplementedError
