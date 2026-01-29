"""
License Plate Detection Module (optimized)

Upgrades:
- Models loaded once per DetectLP instance
- Device-aware inference (cpu / cuda:0)
- Reduced log spam (optional)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
from ultralytics import YOLO

from ..config import Settings
from ..logging import get_logger

logger = get_logger(__name__)

class DetectLP:
    def __init__(
        self,
        vehicle_model_path: Optional[str] = None,
        plate_model_path: Optional[str] = None,
        device: Optional[str] = None,
        verbose: bool = False,
        settings: Optional[Settings] = None,
    ):
        settings = settings or Settings()
        self.vehicle_model_path = vehicle_model_path or settings.resolved_lp_vehicle_model
        self.plate_model_path = plate_model_path or settings.resolved_lp_plate_model
        self.device = device or settings.device
        self.verbose = bool(verbose)

        # Load models once
        self.vehicle_model = YOLO(self.vehicle_model_path)
        self.plate_model = YOLO(self.plate_model_path)

        # Detection parameters (tune as needed)
        self.vehicle_conf_threshold = float(settings.lp_vehicle_conf)
        self.plate_conf_threshold = float(settings.lp_plate_conf)
        self.vehicle_classes = list(settings.lp_vehicle_classes)

    def _log(self, msg: str):
        if self.verbose:
            logger.info(msg)

    def detect_vehicles(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect vehicles in the image."""
        results = self.vehicle_model.predict(
            image,
            conf=self.vehicle_conf_threshold,
            classes=self.vehicle_classes,
            device=self.device,
            verbose=False,
        )[0]

        vehicles: List[Dict[str, Any]] = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                vehicles.append({"bbox": [int(x1), int(y1), int(x2), int(y2)], "confidence": float(conf), "class": cls})
        return vehicles

    @staticmethod
    def crop_vehicle_roi(image: np.ndarray, vehicle_bbox: List[int]) -> Optional[np.ndarray]:
        """Crop vehicle region from image."""
        x1, y1, x2, y2 = vehicle_bbox
        h, w = image.shape[:2]
        x1 = max(0, int(x1)); y1 = max(0, int(y1))
        x2 = min(w, int(x2)); y2 = min(h, int(y2))
        if x2 <= x1 or y2 <= y1:
            return None
        return image[y1:y2, x1:x2]

    def detect_plates_in_roi(self, roi_image: Optional[np.ndarray]) -> List[Dict[str, Any]]:
        """Detect license plates in a vehicle ROI (ROI coordinates)."""
        if roi_image is None or roi_image.size == 0:
            return []
        results = self.plate_model.predict(
            roi_image,
            conf=self.plate_conf_threshold,
            device=self.device,
            verbose=False,
        )[0]

        plates: List[Dict[str, Any]] = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                plates.append({"bbox": [int(x1), int(y1), int(x2), int(y2)], "confidence": float(conf)})
        return plates

    @staticmethod
    def _filter_plates_by_size(plates: List[Dict[str, Any]], vehicle_bbox: List[int]) -> List[Dict[str, Any]]:
        """Filter plates by size: plate area shouldn't exceed 30% of vehicle area."""
        vx1, vy1, vx2, vy2 = vehicle_bbox
        vehicle_area = max(1, (vx2 - vx1) * (vy2 - vy1))
        max_plate_area = vehicle_area * 0.30
        filtered = []
        for plate in plates:
            px1, py1, px2, py2 = plate["bbox"]
            plate_area = max(1, (px2 - px1) * (py2 - py1))
            if plate_area <= max_plate_area:
                filtered.append(plate)
        return filtered

    def process_image_plates_only(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect the best license plate per vehicle (fast path)."""
        vehicles = self.detect_vehicles(image)
        all_plates: List[Dict[str, Any]] = []

        for vehicle in vehicles:
            vehicle_bbox = vehicle["bbox"]
            roi = self.crop_vehicle_roi(image, vehicle_bbox)
            plates = self.detect_plates_in_roi(roi)

            if not plates:
                continue

            valid_plates = [p for p in plates if p["confidence"] >= self.plate_conf_threshold]
            if not valid_plates:
                continue

            size_filtered = self._filter_plates_by_size(valid_plates, vehicle_bbox)
            if not size_filtered:
                continue

            best_plate = max(size_filtered, key=lambda x: x["confidence"])

            vx1, vy1, _, _ = vehicle_bbox
            px1, py1, px2, py2 = best_plate["bbox"]
            global_bbox = [vx1 + px1, vy1 + py1, vx1 + px2, vy1 + py2]
            all_plates.append({"bbox": global_bbox, "confidence": float(best_plate["confidence"])})

        return all_plates

    def process_image_all_plates(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Return all plates (debugging)."""
        vehicles = self.detect_vehicles(image)
        all_plates: List[Dict[str, Any]] = []

        for vehicle in vehicles:
            vehicle_bbox = vehicle["bbox"]
            roi = self.crop_vehicle_roi(image, vehicle_bbox)
            plates = self.detect_plates_in_roi(roi)
            valid_plates = [p for p in plates if p["confidence"] >= self.plate_conf_threshold]
            size_filtered = self._filter_plates_by_size(valid_plates, vehicle_bbox)

            vx1, vy1, _, _ = vehicle_bbox
            for plate in size_filtered:
                px1, py1, px2, py2 = plate["bbox"]
                global_bbox = [vx1 + px1, vy1 + py1, vx1 + px2, vy1 + py2]
                all_plates.append({"bbox": global_bbox, "confidence": float(plate["confidence"])})

        return all_plates

    def detect_license_plates(self, image: np.ndarray, return_all_plates: bool = False) -> List[Dict[str, Any]]:
        return self.process_image_all_plates(image) if return_all_plates else self.process_image_plates_only(image)
