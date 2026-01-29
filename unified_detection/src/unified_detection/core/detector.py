"""
Unified Detection Orchestrator (single-image + batch)

Key upgrades:
- Reuses detector instances (face + LP) once
- Adds detect_objects_batch() for dataset-scale processing (e.g., 1k images)
- CPU-first, GPU-switchable via device argument / env

Usage:
  det = UnifiedDetector(device="cpu", batch_size=8)
  results = det.detect_objects(image_np)
  batch_results = det.detect_objects_batch([img1, img2, ...])
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import cv2
import numpy as np

from ..config import Settings
from ..logging import get_logger
from .face import DetectFace
from .license_plate import DetectLP

logger = get_logger(__name__)


class UnifiedDetector:
    def __init__(
        self,
        device: Optional[str] = None,
        batch_size: Optional[int] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or Settings()
        self.device = device or self.settings.device
        self.batch_size = int(batch_size or self.settings.batch_size)

        self.face_detector: Optional[DetectFace] = None
        self.lp_detector: Optional[DetectLP] = None
        self._initialize_detectors()

    def _initialize_detectors(self):
        """Initialize all detection modules (once)."""
        try:
            logger.info("Initializing face detection system")
            self.face_detector = DetectFace(device=self.device, settings=self.settings)
            logger.info("Face detection system ready")

            logger.info("Initializing license plate detection system")
            self.lp_detector = DetectLP(device=self.device, settings=self.settings)
            logger.info("License plate detection system ready")

            logger.info("All detectors initialized successfully")
        except Exception as e:
            logger.exception("Error initializing detectors: %s", e)
            raise

    @staticmethod
    def _load_image(img: Union[str, np.ndarray]) -> np.ndarray:
        if isinstance(img, str):
            arr = cv2.imread(img)
            if arr is None:
                raise ValueError(f"Failed to load image: {img}")
            return arr
        return img

    def detect_objects(self, image: Union[str, np.ndarray], detect_face: bool = True, detect_lp: bool = True) -> Dict[str, Any]:
        """Detect faces and license plates in one image."""
        img = self._load_image(image)
        results: Dict[str, Any] = {"faces": [], "license_plates": []}

        if detect_face and self.face_detector is not None:
            results["faces"] = self.face_detector.detect_faces(img)

        if detect_lp and self.lp_detector is not None:
            results["license_plates"] = self.lp_detector.detect_license_plates(img)

        return results

    def detect_objects_batch(
        self,
        images: Sequence[Union[str, np.ndarray]],
        detect_face: bool = True,
        detect_lp: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Batch API for dataset-scale runs.

        - Loads images if paths are provided.
        - Runs batched YOLO person detection for faces (fast), then per-image SCRFD.
        - Runs LP detection per-image (can be batched later if desired).
        """
        # Load all in memory for this batch call; caller should chunk for large datasets
        imgs = [self._load_image(im) for im in images]

        face_results: List[List[Dict[str, Any]]] = [[] for _ in imgs]
        if detect_face and self.face_detector is not None:
            face_results = self.face_detector.detect_faces_batch(imgs, batch=self.batch_size)

        out: List[Dict[str, Any]] = []
        for i, img in enumerate(imgs):
            res: Dict[str, Any] = {"faces": [], "license_plates": []}
            if detect_face:
                res["faces"] = face_results[i]
            if detect_lp and self.lp_detector is not None:
                res["license_plates"] = self.lp_detector.detect_license_plates(img)
            out.append(res)
        return out
