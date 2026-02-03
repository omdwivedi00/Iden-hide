"""Single-shot YOLO face detector."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from ultralytics import YOLO

from ..config import Settings
from ..logging import get_logger
from .face_base import BaseFaceDetector

logger = get_logger(__name__)


class YoloFaceDetector(BaseFaceDetector):
    """YOLO-based face detector (single-shot)."""

    def __init__(self, device: Optional[str] = None, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.device = device or self.settings.device
        self.model_path = self.settings.resolved_face_yolo_model
        self.model = YOLO(self.model_path)
        self.conf = float(self.settings.face_person_conf)

    def _predict(self, image: np.ndarray) -> List[Dict]:
        results = self.model.predict(
            image,
            conf=self.conf,
            device=self.device,
            verbose=False,
        )
        if not results:
            return []
        boxes = results[0].boxes
        if boxes is None:
            return []
        detections: List[Dict] = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            detections.append({"bbox": [int(x1), int(y1), int(x2), int(y2)], "confidence": conf})
        return detections

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        return self._predict(image)

    def detect_faces_batch(self, images: List[np.ndarray], batch: int = 8) -> List[List[Dict]]:
        # Use YOLO batch prediction if available; fallback to sequential
        try:
            results = self.model.predict(
                images,
                conf=self.conf,
                device=self.device,
                verbose=False,
                batch=batch,
            )
            out: List[List[Dict]] = []
            for res in results:
                boxes = res.boxes
                if boxes is None:
                    out.append([])
                    continue
                dets: List[Dict] = []
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                    conf = float(box.conf[0].cpu().numpy())
                    dets.append({"bbox": [int(x1), int(y1), int(x2), int(y2)], "confidence": conf})
                out.append(dets)
            return out
        except Exception as exc:
            logger.warning("Batch YOLO face prediction failed, falling back to sequential: %s", exc)
            return [self._predict(img) for img in images]
