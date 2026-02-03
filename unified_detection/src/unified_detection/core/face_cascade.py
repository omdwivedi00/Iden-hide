"""
ADAS-optimized Face Detection (module + CLI)

Pipeline (default):
YOLO(person) -> per-person ROI -> tiled SCRFD (InsightFace) -> gating -> best face per person -> cross-person NMS

NEW (added, optional):
- YOLO(face) ONLY mode  -> direct face boxes from YOLO
- SCRFD ONLY mode       -> direct face boxes from InsightFace detector

Key goals:
- Fast on CPU by default
- Switchable to GPU for YOLO (and optional GPU for SCRFD if available via onnxruntime/cuda provider)
- Stable runtime on crowded scenes (caps + adaptive tiling)
- API-friendly: DetectFace.detect_faces(np.ndarray) -> [{'bbox':[x1,y1,x2,y2], 'confidence':score}, ...]

Notes:
- InsightFace FaceAnalysis is kept as a SINGLE instance and reused (huge speed win vs per-call init).
- YOLO is also reused and can do batched person detection.

Configuration is provided by unified_detection.config.Settings.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import cv2
import numpy as np
from ultralytics import YOLO
from insightface.app import FaceAnalysis

from ..config import Settings
from ..logging import get_logger
from .face_base import BaseFaceDetector

logger = get_logger(__name__)

# ---------------- utils ----------------
def _expand_xyxy(box, scale, W, H, square=False):
    x1, y1, x2, y2 = map(float, box)
    cx, cy = (x1 + x2) * 0.5, (y1 + y2) * 0.5
    w, h = (x2 - x1), (y2 - y1)
    if square:
        s = scale * max(w, h)
        w = h = s
    else:
        w, h = scale * w, scale * h
    nx1, ny1 = max(0.0, cx - w * 0.5), max(0.0, cy - h * 0.5)
    nx2 = min(W - 1.0, cx + w * 0.5)
    ny2 = min(H - 1.0, cy + h * 0.5)
    return [nx1, ny1, nx2, ny2]

def _head_distance_score(face_xyxy, person_xyxy, ideal=0.35):
    fx1, fy1, fx2, fy2 = face_xyxy
    px1, py1, px2, py2 = person_xyxy
    fc_y = 0.5 * (fy1 + fy2)
    ph = max(1.0, py2 - py1)
    rel = (fc_y - py1) / ph
    return abs(rel - ideal)

def _nms_xyxy(boxes, scores, iou_thr=0.5):
    if not boxes:
        return []
    B = np.asarray(boxes, np.float32)
    S = np.asarray(scores, np.float32)
    order = S.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        rest = order[1:]
        if rest.size == 0:
            break
        xx1 = np.maximum(B[i, 0], B[rest, 0])
        yy1 = np.maximum(B[i, 1], B[rest, 1])
        xx2 = np.minimum(B[i, 2], B[rest, 2])
        yy2 = np.minimum(B[i, 3], B[rest, 3])
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h
        area_i = (B[i, 2] - B[i, 0]) * (B[i, 3] - B[i, 1])
        area_r = (B[rest, 2] - B[rest, 0]) * (B[rest, 3] - B[rest, 1])
        iou = inter / (area_i + area_r - inter + 1e-6)
        order = rest[iou <= iou_thr]
    return keep

def _letterbox(img: np.ndarray, new_size: int, color=(114, 114, 114)):
    h, w = img.shape[:2]
    r = min(new_size / w, new_size / h)
    nw, nh = int(round(w * r)), int(round(h * r))
    imr = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_CUBIC)
    dw, dh = (new_size - nw) * 0.5, (new_size - nh) * 0.5
    top, bottom = int(dh), new_size - nh - int(dh)
    left, right = int(dw), new_size - nw - int(dw)
    out = cv2.copyMakeBorder(imr, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return out, r, (left, top), (nw, nh)

def _tiles_inside_roi(roi, W, H, grid=(2, 2), overlap=0.25):
    rx1, ry1, rx2, ry2 = map(int, roi)
    rx1 = max(0, rx1); ry1 = max(0, ry1); rx2 = min(W, rx2); ry2 = min(H, ry2)
    if rx2 <= rx1 or ry2 <= ry1:
        return []
    gw, gh = grid
    rw, rh = (rx2 - rx1), (ry2 - ry1)
    stepx, stepy = max(1, rw // gw), max(1, rh // gh)
    ox, oy = int(overlap * stepx), int(overlap * stepy)
    out = []
    for gy in range(gh):
        for gx in range(gw):
            tx1 = max(0, rx1 + gx * stepx - ox)
            ty1 = max(0, ry1 + gy * stepy - oy)
            tx2 = min(W, rx1 + (gx + 1) * stepx + ox)
            ty2 = min(H, ry1 + (gy + 1) * stepy + oy)
            if tx2 > tx1 and ty2 > ty1:
                out.append([tx1, ty1, tx2, ty2])
    return out

def _head_band_from_person(pb, frac=0.45):
    x1, y1, x2, y2 = map(float, pb)
    h = max(1.0, y2 - y1)
    return [x1, y1, x2, y1 + h * frac]

def _face_size_ok(face_xyxy, person_xyxy, min_rel=0.10, max_rel=0.55):
    x1, y1, x2, y2 = map(float, face_xyxy)
    px1, py1, px2, py2 = map(float, person_xyxy)
    fh = max(1.0, y2 - y1); ph = max(1.0, py2 - py1)
    r = fh / ph
    return (min_rel <= r <= max_rel)

# ---------------- config ----------------
@dataclass
class FaceDetectConfig:
    """
    mode:
      - "cascade"   : existing YOLO(person) -> ROI -> tiled SCRFD -> gating -> NMS
      - "yolo_face" : YOLO(face) only
      - "scrfd"     : SCRFD only (full-frame)
    """
    mode: str = "cascade"

    # YOLO model path/name (person model for cascade, face model for yolo_face)
    yolo_model: str = ""

    # YOLO person
    person_conf: float = 0.25
    imgsz: int = 832
    person_nms_iou: float = 0.60
    max_persons: int = 25  # cap for crowded scenes (keeps runtime stable)

    # SCRFD / InsightFace detection
    face_size: int = 640
    face_thr: float = 0.50
    flip_tta: bool = False  # accuracy↑ speed↓; keep False by default for CPU

    # ROI + tiling (cascade only)
    roi_scale: float = 1.10
    roi_square: bool = False
    grid = (1, 2)          # vertical bias (faces live vertically)
    overlap = 0.15
    roi_single_tile_px = 800 * 800

    # Gating (cascade only)
    head_frac: float = 0.45
    size_min_rel: float = 0.05
    size_max_rel: float = 0.80

    # Final NMS
    face_nms_iou: float = 0.55


# ---------------- main detector ----------------
class DetectFace:
    """
    Drop-in detector for unified system.
    """
    def __init__(
        self,
        config: Optional[FaceDetectConfig] = None,
        device: Optional[str] = None,
        providers: Optional[List[str]] = None,
        settings: Optional[Settings] = None,
    ):
        settings = settings or Settings()

        if config is None:
            # Default stays cascade to preserve existing behavior
            config = FaceDetectConfig(
                mode=getattr(settings, "face_mode", "cascade"),
                yolo_model=settings.resolved_face_yolo_model,
                person_conf=settings.face_person_conf,
                imgsz=settings.face_img_size,
                face_size=settings.face_det_size,
                face_thr=settings.face_det_thr,
                flip_tta=bool(settings.face_flip_tta),
                max_persons=settings.face_max_persons,
            )

        self.cfg = config
        self.mode = (self.cfg.mode or "cascade").lower()
        self.device = device or settings.device

        # YOLO model is used in cascade (person) and yolo_face (face)
        self.yolo = YOLO(self.cfg.yolo_model)

        # InsightFace SCRFD (used in cascade and scrfd-only)
        if providers is None:
            providers = ["CPUExecutionProvider"]

        self.app = FaceAnalysis(
            name="buffalo_l",  # keep as-is; you can change to "scrfd_10g" etc if present in your local model dir
            providers=providers,
            allowed_modules=["detection"],
        )

        # ctx_id: -1 for CPU; 0 for GPU in some setups (kept -1 safe)
        self.app.prepare(ctx_id=-1, det_size=(self.cfg.face_size, self.cfg.face_size))
        det = self.app.models.get("detection", None)
        if det is not None:
            det.det_thresh = float(self.cfg.face_thr)
            det.nms_thresh = 0.40

        # InsightFace is not guaranteed thread-safe → guard
        self._app_lock = threading.Lock()

    # ---------------- NEW: single-model modes ----------------
    def _detect_faces_yolo_only(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        YOLO(face) only mode.
        Expects yolo_model to be a face detector.
        """
        pred = self.yolo.predict(
            image,
            conf=self.cfg.face_thr,
            imgsz=self.cfg.imgsz,
            device=self.device,
            verbose=False,
        )[0]

        results: List[Dict[str, Any]] = []
        if pred.boxes is None:
            return results

        # Optional: If your face model uses a specific class id, filter here.
        # For generic face-only models, leaving it as-is returns all detections.
        for b in pred.boxes:
            x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
            score = float(b.conf[0]) if getattr(b, "conf", None) is not None else 0.0
            if score < self.cfg.face_thr:
                continue
            results.append({"bbox": [x1, y1, x2, y2], "confidence": score})

        # Cross-face NMS (optional but keeps output clean)
        if results:
            boxes = [r["bbox"] for r in results]
            scores = [r["confidence"] for r in results]
            keep = _nms_xyxy(boxes, scores, iou_thr=self.cfg.face_nms_iou)
            results = [results[i] for i in keep]

        return results

    def _detect_faces_scrfd_only(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        SCRFD only mode, full-frame.
        """
        with self._app_lock:
            faces = list(self.app.get(image))

        results: List[Dict[str, Any]] = []
        for f in faces:
            sc = float(getattr(f, "det_score", 1.0))
            if sc < self.cfg.face_thr:
                continue
            x1, y1, x2, y2 = map(int, f.bbox.astype(float).tolist())
            results.append({"bbox": [x1, y1, x2, y2], "confidence": sc})

        if results:
            boxes = [r["bbox"] for r in results]
            scores = [r["confidence"] for r in results]
            keep = _nms_xyxy(boxes, scores, iou_thr=self.cfg.face_nms_iou)
            results = [results[i] for i in keep]

        return results

    # ---------------- existing helpers ----------------
    def _detect_faces_in_tile(self, img: np.ndarray, xyxy: List[int]) -> List[List[float]]:
        x1, y1, x2, y2 = map(int, xyxy)
        tile = img[y1:y2, x1:x2]
        if tile.size == 0:
            return []
        rs, r, (dx, dy), (nw, nh) = _letterbox(tile, self.cfg.face_size)
        with self._app_lock:
            faces = list(self.app.get(rs))

        # optional flip TTA
        if self.cfg.flip_tta:
            rsf = cv2.flip(rs, 1)
            with self._app_lock:
                ff = list(self.app.get(rsf))
            for f in ff:
                b = f.bbox.astype(float)
                b[[0, 2]] = self.cfg.face_size - b[[2, 0]]
                faces.append(type("obj", (object,), {"bbox": b, "det_score": getattr(f, "det_score", 1.0)}))

        outs: List[List[float]] = []
        for f in faces:
            bx1, by1, bx2, by2 = f.bbox.astype(float)
            sc = float(getattr(f, "det_score", 1.0))
            if sc < self.cfg.face_thr:
                continue
            tx1 = (bx1 - dx) / r; ty1 = (by1 - dy) / r
            tx2 = (bx2 - dx) / r; ty2 = (by2 - dy) / r
            tx1 = float(np.clip(tx1, 0, nw - 1)); tx2 = float(np.clip(tx2, 0, nw - 1))
            ty1 = float(np.clip(ty1, 0, nh - 1)); ty2 = float(np.clip(ty2, 0, nh - 1))
            outs.append([x1 + tx1, y1 + ty1, x1 + tx2, y1 + ty2, sc])
        return outs

    def _persons_for_image(self, image: np.ndarray) -> List[List[float]]:
        pred = self.yolo.predict(
            image,
            conf=self.cfg.person_conf,
            classes=[0],  # person class for COCO
            imgsz=self.cfg.imgsz,
            device=self.device,
            verbose=False,
        )[0]
        p_boxes = [b.xyxy[0].tolist() for b in pred.boxes] if pred.boxes is not None else []
        p_scores = [float(b.conf[0]) if getattr(b, "conf", None) is not None else 0.0 for b in (pred.boxes or [])]
        keep_p = _nms_xyxy(p_boxes, p_scores, iou_thr=self.cfg.person_nms_iou)
        persons = [(p_boxes[i], p_scores[i]) for i in keep_p]

        # cap persons (top-k by score) for crowd stability
        persons.sort(key=lambda x: x[1], reverse=True)
        persons = persons[: self.cfg.max_persons]
        return [p for p, _ in persons]

    # ---------------- main API ----------------
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Single image API.
        Returns: [{'bbox':[x1,y1,x2,y2], 'confidence':score}, ...]
        """
        # NEW: single-model mode switch (keeps cascade logic intact)
        if self.mode == "yolo_face":
            return self._detect_faces_yolo_only(image)
        if self.mode == "scrfd":
            return self._detect_faces_scrfd_only(image)

        # ---------------- cascade (existing logic) ----------------
        H, W = image.shape[:2]
        persons = self._persons_for_image(image)

        faces_all: List[List[float]] = []
        scores_all: List[float] = []

        # If no persons found, do a single full-frame pass (fast fallback)
        if not persons:
            full_tile = [0, 0, W, H]
            outs = self._detect_faces_in_tile(image, full_tile)
            for x1, y1, x2, y2, sc in outs:
                faces_all.append([x1, y1, x2, y2]); scores_all.append(sc)
        else:
            for pb in persons:
                roi = _expand_xyxy(pb, self.cfg.roi_scale, W, H, square=self.cfg.roi_square)

                # Adaptive tiling: if ROI small enough, one tile is enough
                rx1, ry1, rx2, ry2 = map(int, roi)
                roi_area = max(1, (rx2 - rx1) * (ry2 - ry1))
                if roi_area <= self.cfg.roi_single_tile_px:
                    tiles = [[rx1, ry1, rx2, ry2]]
                else:
                    tiles = _tiles_inside_roi(roi, W, H, grid=self.cfg.grid, overlap=self.cfg.overlap)

                cand_boxes: List[List[float]] = []
                cand_scores: List[float] = []
                for t in tiles:
                    outs = self._detect_faces_in_tile(image, t)
                    for x1, y1, x2, y2, sc in outs:
                        if _face_size_ok([x1, y1, x2, y2], pb, self.cfg.size_min_rel, self.cfg.size_max_rel):
                            dist = _head_distance_score([x1, y1, x2, y2], pb)
                            adjusted_score = sc * np.exp(-2.0 * dist)
                            cand_boxes.append([x1, y1, x2, y2])
                            cand_scores.append(adjusted_score)

                # keep ALL valid faces for this person
                K = 2  # max faces per person
                if cand_boxes:
                    idxs = np.argsort(cand_scores)[-K:]
                    for j in idxs:
                        faces_all.append(cand_boxes[j])
                        scores_all.append(float(cand_scores[j]))

        # cross-person NMS
        keep_f = _nms_xyxy(faces_all, scores_all, iou_thr=self.cfg.face_nms_iou)

        results: List[Dict[str, Any]] = []
        for i in keep_f:
            b = faces_all[i]
            results.append(
                {
                    "bbox": [int(b[0]), int(b[1]), int(b[2]), int(b[3])],
                    "confidence": float(scores_all[i]),
                }
            )
        return results

    def detect_faces_batch(self, images: Sequence[np.ndarray], batch: int = 8) -> List[List[Dict[str, Any]]]:
        """
        Batched API.
        - For non-cascade modes, we just loop over images (simple + correct).
        - For cascade, we keep your batched YOLO person detection.
        """
        # NEW: single-model modes
        if self.mode in ("yolo_face", "scrfd"):
            return [self.detect_faces(img) for img in images]

        # ---------------- cascade (existing logic) ----------------
        preds = self.yolo.predict(
            list(images),
            conf=self.cfg.person_conf,
            classes=[0],
            imgsz=self.cfg.imgsz,
            device=self.device,
            batch=batch,
            verbose=False,
        )

        out: List[List[Dict[str, Any]]] = []
        for img, pred in zip(images, preds):
            H, W = img.shape[:2]
            p_boxes = [b.xyxy[0].tolist() for b in pred.boxes] if pred.boxes is not None else []
            p_scores = [float(b.conf[0]) if getattr(b, "conf", None) is not None else 0.0 for b in (pred.boxes or [])]
            keep_p = _nms_xyxy(p_boxes, p_scores, iou_thr=self.cfg.person_nms_iou)
            persons = [(p_boxes[i], p_scores[i]) for i in keep_p]
            persons.sort(key=lambda x: x[1], reverse=True)
            persons = persons[: self.cfg.max_persons]
            persons_boxes = [p for p, _ in persons]

            faces_all: List[List[float]] = []
            scores_all: List[float] = []

            if not persons_boxes:
                outs = self._detect_faces_in_tile(img, [0, 0, W, H])
                for x1, y1, x2, y2, sc in outs:
                    faces_all.append([x1, y1, x2, y2]); scores_all.append(sc)
            else:
                for pb in persons_boxes:
                    roi = _expand_xyxy(pb, self.cfg.roi_scale, W, H, square=self.cfg.roi_square)
                    rx1, ry1, rx2, ry2 = map(int, roi)
                    roi_area = max(1, (rx2 - rx1) * (ry2 - ry1))
                    if roi_area <= self.cfg.roi_single_tile_px:
                        tiles = [[rx1, ry1, rx2, ry2]]
                    else:
                        tiles = _tiles_inside_roi(roi, W, H, grid=self.cfg.grid, overlap=self.cfg.overlap)

                    cand_boxes: List[List[float]] = []
                    cand_scores: List[float] = []
                    for t in tiles:
                        outs = self._detect_faces_in_tile(img, t)
                        for x1, y1, x2, y2, sc in outs:
                            if _face_size_ok([x1, y1, x2, y2], pb, self.cfg.size_min_rel, self.cfg.size_max_rel):
                                dist = _head_distance_score([x1, y1, x2, y2], pb)
                                adjusted_score = sc * np.exp(-2.0 * dist)
                                cand_boxes.append([x1, y1, x2, y2])
                                cand_scores.append(adjusted_score)

                    K = 2
                    if cand_boxes:
                        idxs = np.argsort(cand_scores)[-K:]
                        for j in idxs:
                            faces_all.append(cand_boxes[j])
                            scores_all.append(float(cand_scores[j]))

            keep_f = _nms_xyxy(faces_all, scores_all, iou_thr=self.cfg.face_nms_iou)
            results: List[Dict[str, Any]] = []
            for i in keep_f:
                b = faces_all[i]
                results.append(
                    {"bbox": [int(b[0]), int(b[1]), int(b[2]), int(b[3])], "confidence": float(scores_all[i])}
                )
            out.append(results)

        return out


class CascadeFaceDetector(BaseFaceDetector):
    """Adapter for the existing cascade face detector."""

    def __init__(self, device: Optional[str] = None, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.detector = DetectFace(device=device, settings=self.settings)

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        return self.detector.detect_faces(image)

    def detect_faces_batch(self, images: List[np.ndarray], batch: int = 8) -> List[List[Dict]]:
        return self.detector.detect_faces_batch(images, batch=batch)


__all__ = ["FaceDetectConfig", "DetectFace", "CascadeFaceDetector"]
