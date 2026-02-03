"""Full-frame SCRFD detector using InsightFace FaceAnalysis."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from insightface.app import FaceAnalysis

from ..config import Settings
from ..logging import get_logger
from .face_base import BaseFaceDetector

logger = get_logger(__name__)


class ScrfdFaceDetector(BaseFaceDetector):
    """Full-frame SCRFD face detector (no person prefilter)."""

    def __init__(self, device: Optional[str] = None, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.device = device or self.settings.device

        providers = ["CPUExecutionProvider"]
        if "cuda" in self.device.lower():
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=providers,
            allowed_modules=["detection"],
        )
        self.app.prepare(ctx_id=-1, det_size=(self.settings.face_det_size, self.settings.face_det_size))
        det = self.app.models.get("detection", None)
        if det is not None:
            det.det_thresh = float(self.settings.face_det_thr)
            det.nms_thresh = 0.40

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        faces = list(self.app.get(image))
        detections: List[Dict] = []
        for f in faces:
            x1, y1, x2, y2 = f.bbox.astype(float).tolist()
            conf = float(getattr(f, "det_score", 1.0))
            if conf < float(self.settings.face_det_thr):
                continue
            detections.append({"bbox": [int(x1), int(y1), int(x2), int(y2)], "confidence": conf})
        return detections

    def detect_faces_batch(self, images: List[np.ndarray], batch: int = 8) -> List[List[Dict]]:
        # InsightFace FaceAnalysis is not batch-optimized; run sequential
        return [self.detect_faces(img) for img in images]
