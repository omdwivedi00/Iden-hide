"""
License Plate Detection Module
"""

import cv2
import numpy as np
from ultralytics import YOLO

class DetectLP:
    def __init__(self, vehicle_model_path='models/yolo11n.pt', plate_model_path='models/license_plate_detector.pt'):
        self.vehicle_model_path = vehicle_model_path
        self.plate_model_path = plate_model_path
        
        # Load models
        self.vehicle_model = YOLO(vehicle_model_path)
        self.plate_model = YOLO(plate_model_path)
        
        # Detection parameters
        self.vehicle_conf_threshold = 0.5
        self.plate_conf_threshold = 0.2
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

    def detect_vehicles(self, image):
        """Detect vehicles in the image"""
        results = self.vehicle_model.predict(
            image, 
            conf=self.vehicle_conf_threshold,
            classes=self.vehicle_classes,
            verbose=False
        )[0]
        
        vehicles = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                vehicles.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(conf),
                    'class': cls
                })
        
        return vehicles

    def crop_vehicle_roi(self, image, vehicle_bbox):
        """Crop vehicle region from image"""
        x1, y1, x2, y2 = vehicle_bbox
        h, w = image.shape[:2]
        
        # Ensure coordinates are within image bounds
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))
        
        if x2 <= x1 or y2 <= y1:
            return None
            
        return image[y1:y2, x1:x2]

    def detect_plates_in_roi(self, roi_image):
        """Detect license plates in vehicle ROI"""
        if roi_image is None or roi_image.size == 0:
            return []
        
        results = self.plate_model.predict(
            roi_image,
            conf=self.plate_conf_threshold,
            verbose=False
        )[0]
        
        plates = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                
                plates.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(conf)
                })
        
        return plates

    def _filter_plates_by_size(self, plates, vehicle_bbox):
        """
        Filter license plates by size - plates shouldn't exceed 30% of vehicle area
        
        Args:
            plates: List of detected plates in ROI coordinates
            vehicle_bbox: Vehicle bounding box [x1, y1, x2, y2]
            
        Returns:
            List of plates that meet the size criteria
        """
        vx1, vy1, vx2, vy2 = vehicle_bbox
        vehicle_area = (vx2 - vx1) * (vy2 - vy1)
        max_plate_area = vehicle_area * 0.30  # 30% of vehicle area
        
        filtered_plates = []
        
        for plate in plates:
            px1, py1, px2, py2 = plate['bbox']
            plate_area = (px2 - px1) * (py2 - py1)
            
            if plate_area <= max_plate_area:
                filtered_plates.append(plate)
            else:
                plate_percentage = (plate_area / vehicle_area) * 100
                print(f"  Plate filtered: area={plate_area:.0f}px² ({plate_percentage:.1f}% of vehicle), max allowed=30%")
        
        return filtered_plates

    def process_image_plates_only(self, image):
        """Process image to detect license plates only"""
        # Step 1: Detect vehicles
        vehicles = self.detect_vehicles(image)
        
        all_plates = []
        
        # Step 2: Look for license plates in each vehicle
        for i, vehicle in enumerate(vehicles):
            vehicle_bbox = vehicle['bbox']
            roi = self.crop_vehicle_roi(image, vehicle_bbox)
            
            if roi is not None:
                plates = self.detect_plates_in_roi(roi)
                
                # If multiple plates detected in this vehicle, select the one with highest confidence
                if plates:
                    # Filter out plates with very low confidence
                    valid_plates = [p for p in plates if p['confidence'] >= self.plate_conf_threshold]
                    
                    if valid_plates:
                        # Filter plates by size - license plate shouldn't be >30% of vehicle area
                        size_filtered_plates = self._filter_plates_by_size(valid_plates, vehicle_bbox)
                        
                        if size_filtered_plates:
                            # Sort plates by confidence in descending order
                            plates_sorted = sorted(size_filtered_plates, key=lambda x: x['confidence'], reverse=True)
                            best_plate = plates_sorted[0]  # Take the plate with highest confidence
                        else:
                            # No plates meet the size criteria
                            print(f"Vehicle {i+1}: All {len(valid_plates)} plates filtered out due to size (exceed 30% of vehicle area)")
                            continue
                        
                        # Convert ROI coordinates back to image coordinates
                        vx1, vy1, vx2, vy2 = vehicle_bbox
                        px1, py1, px2, py2 = best_plate['bbox']
                        
                        # Map back to original image coordinates
                        global_bbox = [
                            vx1 + px1,
                            vy1 + py1,
                            vx1 + px2,
                            vy1 + py2
                        ]
                        
                        all_plates.append({
                            'bbox': global_bbox,
                            'confidence': best_plate['confidence']
                        })
                        
                        # Log if multiple plates were found but only best one selected
                        if len(valid_plates) > 1:
                            print(f"Vehicle {i+1}: Found {len(valid_plates)} valid plates, selected best with confidence {best_plate['confidence']:.3f}")
                        elif len(plates) > len(valid_plates):
                            print(f"Vehicle {i+1}: Found {len(plates)} plates, {len(plates) - len(valid_plates)} filtered out due to low confidence")
        
        return all_plates

    def detect_license_plates(self, image, return_all_plates=False):
        """
        Main method to detect license plates
        
        Args:
            image: Input image
            return_all_plates: If True, return all detected plates per vehicle instead of just the best one
        
        Returns:
            List of detected license plates with bbox and confidence
        """
        if return_all_plates:
            return self.process_image_all_plates(image)
        else:
            return self.process_image_plates_only(image)
    
    def process_image_all_plates(self, image):
        """Process image to detect all license plates (for debugging)"""
        # Step 1: Detect vehicles
        vehicles = self.detect_vehicles(image)
        
        all_plates = []
        
        # Step 2: Look for license plates in each vehicle
        for i, vehicle in enumerate(vehicles):
            vehicle_bbox = vehicle['bbox']
            roi = self.crop_vehicle_roi(image, vehicle_bbox)
            
            if roi is not None:
                plates = self.detect_plates_in_roi(roi)
                
                # Filter out plates with very low confidence
                valid_plates = [p for p in plates if p['confidence'] >= self.plate_conf_threshold]
                
                if valid_plates:
                    # Filter plates by size - license plate shouldn't be >30% of vehicle area
                    size_filtered_plates = self._filter_plates_by_size(valid_plates, vehicle_bbox)
                    
                    # Convert ROI coordinates back to image coordinates
                    vx1, vy1, vx2, vy2 = vehicle_bbox
                    for plate in size_filtered_plates:
                        px1, py1, px2, py2 = plate['bbox']
                        # Map back to original image coordinates
                        global_bbox = [
                            vx1 + px1,
                            vy1 + py1,
                            vx1 + px2,
                            vy1 + py2
                        ]
                        all_plates.append({
                            'bbox': global_bbox,
                            'confidence': plate['confidence']
                        })
                    
                    # Log filtering results
                    if len(plates) > len(valid_plates):
                        print(f"Vehicle {i+1}: {len(plates) - len(valid_plates)} plates filtered out due to low confidence")
                    if len(valid_plates) > len(size_filtered_plates):
                        print(f"Vehicle {i+1}: {len(valid_plates) - len(size_filtered_plates)} plates filtered out due to size (exceed 30% of vehicle area)")
                
                if len(plates) > 1:
                    print(f"Vehicle {i+1}: Found {len(plates)} plates (all returned)")
        
        return all_plates
