from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import cv2
import numpy as np

from ..config import Settings
from ..logging import get_logger

# Face detectors
from .face_cascade import CascadeFaceDetector  # CASCADE (YOLO → SCRFD)
from .face_yolo import YoloFaceDetector   # single-shot YOLO face
from .face_scrfd import ScrfdFaceDetector # single-shot SCRFD

# License plate
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

        self.face_detector = None
        self.lp_detector = None

        self._initialize_detectors()

    def _initialize_detectors(self):
        """Initialize detectors once based on FACE_MODE."""
        try:
            face_mode = self.settings.face_mode.lower()
            logger.info("Initializing face detector: mode=%s", face_mode)

            if face_mode == "cascade":
                # Your current ADAS-grade pipeline
                self.face_detector = CascadeFaceDetector(
                    device=self.device,
                    settings=self.settings,
                )

            elif face_mode == "yolo_face":
                self.face_detector = YoloFaceDetector(
                    device=self.device,
                    settings=self.settings,
                )

            elif face_mode == "scrfd":
                self.face_detector = ScrfdFaceDetector(
                    device=self.device,
                    settings=self.settings,
                )

            else:
                raise ValueError(f"Unknown FACE_MODE='{face_mode}'")

            logger.info("Face detector ready: %s", face_mode)

            logger.info("Initializing license plate detector")
            self.lp_detector = DetectLP(
                device=self.device,
                settings=self.settings,
            )
            logger.info("License plate detector ready")

        except Exception as e:
            logger.exception("Failed to initialize detectors")
            raise

    @staticmethod
    def _load_image(img: Union[str, np.ndarray]) -> np.ndarray:
        if isinstance(img, str):
            arr = cv2.imread(img)
            if arr is None:
                raise ValueError(f"Failed to load image: {img}")
            return arr
        return img

    def detect_objects(
        self,
        image: Union[str, np.ndarray],
        detect_face: bool = True,
        detect_lp: bool = True,
    ) -> Dict[str, Any]:
        """Single image detection."""
        img = self._load_image(image)
        results: Dict[str, Any] = {
            "faces": [],
            "license_plates": [],
        }

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
        """Batch detection API."""
        imgs = [self._load_image(im) for im in images]

        face_results: List[List[Dict[str, Any]]] = [[] for _ in imgs]

        if detect_face and self.face_detector is not None:
            face_results = self.face_detector.detect_faces_batch(
                imgs, batch=self.batch_size
            )

        out: List[Dict[str, Any]] = []
        for i, img in enumerate(imgs):
            res = {"faces": [], "license_plates": []}

            if detect_face:
                res["faces"] = face_results[i]

            if detect_lp and self.lp_detector is not None:
                res["license_plates"] = self.lp_detector.detect_license_plates(img)

            out.append(res)

        return out
