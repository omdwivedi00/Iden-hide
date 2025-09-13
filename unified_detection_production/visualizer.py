"""
Visualization Module
"""

import cv2
import numpy as np
from typing import List, Dict, Union
from pathlib import Path

class DetectionVisualizer:
    def __init__(self):
        self.colors = {
            'face': (0, 255, 0),        # Green
            'license_plate': (0, 0, 255)  # Red
        }
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_boxes(self, image: np.ndarray, results: Dict[str, List[Dict]], 
                   show_confidence: bool = True) -> np.ndarray:
        """Draw bounding boxes on image"""
        result_image = image.copy()
        
        # Draw face detections
        for face in results.get('faces', []):
            bbox = face['bbox']
            confidence = face['confidence']
            self._draw_single_box(result_image, bbox, 'face', confidence, show_confidence)
        
        # Draw license plate detections
        for plate in results.get('license_plates', []):
            bbox = plate['bbox']
            confidence = plate['confidence']
            self._draw_single_box(result_image, bbox, 'license_plate', confidence, show_confidence)
        
        return result_image

    def _draw_single_box(self, image: np.ndarray, bbox: List[int], 
                        label: str, confidence: float, show_confidence: bool):
        """Draw a single bounding box"""
        x1, y1, x2, y2 = bbox
        color = self.colors.get(label, (255, 0, 0))
        
        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        if show_confidence:
            label_text = f"{label}: {confidence:.3f}"
        else:
            label_text = label
        
        label_size = cv2.getTextSize(label_text, self.font, 0.6, 2)[0]
        
        # Draw background for text
        cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        
        # Draw text
        cv2.putText(image, label_text, (x1, y1 - 5), 
                   self.font, 0.6, (255, 255, 255), 2)

    def blur_face_oval(self, image: np.ndarray, bbox: List[float], blur_strength: int = 15) -> np.ndarray:
        """Blur a face region with oval shape"""
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        
        # Convert to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        if blur_strength % 2 == 0:
            blur_strength += 1
        
        blurred_image = image.copy()
        
        # Calculate oval parameters
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        axes_x = (x2 - x1) // 2
        axes_y = (y2 - y1) // 2
        
        # Create mask for oval region
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(mask, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, 255, -1)
        
        # Extract the region
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return blurred_image
        
        # Blur the region
        blurred_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
        
        # Apply oval mask to the blurred region
        mask_region = mask[y1:y2, x1:x2]
        if mask_region.shape[:2] == blurred_region.shape[:2]:
            for c in range(3):
                blurred_image[y1:y2, x1:x2, c] = np.where(
                    mask_region > 0,
                    blurred_region[:, :, c],
                    image[y1:y2, x1:x2, c]
                )
        
        return blurred_image

    def blur_rectangle_region(self, image: np.ndarray, bbox: List[float], blur_strength: int = 15) -> np.ndarray:
        """Blur a rectangular region (for license plates)"""
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        
        # Convert to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        if blur_strength % 2 == 0:
            blur_strength += 1
        
        blurred_image = image.copy()
        
        # Ensure coordinates are within image bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        # Extract the region
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return blurred_image
        
        # Blur the region
        blurred_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
        
        # Replace the region in the image
        blurred_image[y1:y2, x1:x2] = blurred_region
        
        return blurred_image

    def blur_detections(self, image: np.ndarray, results: Dict[str, List], 
                       face_blur_strength: int = 15, plate_blur_strength: int = 15) -> np.ndarray:
        """Blur all detected faces and license plates"""
        blurred_image = image.copy()
        
        # Blur faces with oval shape
        for face in results.get('faces', []):
            # Handle both formats: [x1, y1, x2, y2, confidence] and {'bbox': [x1, y1, x2, y2], 'confidence': score}
            if isinstance(face, list) and len(face) >= 4:
                # Format: [x1, y1, x2, y2, confidence]
                bbox = face[:4]  # Take first 4 elements as bbox
            elif isinstance(face, dict) and 'bbox' in face:
                # Format: {'bbox': [x1, y1, x2, y2], 'confidence': score}
                bbox = face['bbox']
            else:
                print(f"Warning: Invalid face format: {face}")
                continue
                
            blurred_image = self.blur_face_oval(blurred_image, bbox, face_blur_strength)
        
        # Blur license plates with rectangular shape
        for plate in results.get('license_plates', []):
            # Handle both formats: [x1, y1, x2, y2, confidence] and {'bbox': [x1, y1, x2, y2], 'confidence': score}
            if isinstance(plate, list) and len(plate) >= 4:
                # Format: [x1, y1, x2, y2, confidence]
                bbox = plate[:4]  # Take first 4 elements as bbox
            elif isinstance(plate, dict) and 'bbox' in plate:
                # Format: {'bbox': [x1, y1, x2, y2], 'confidence': score}
                bbox = plate['bbox']
            else:
                print(f"Warning: Invalid plate format: {plate}")
                continue
                
            blurred_image = self.blur_rectangle_region(blurred_image, bbox, plate_blur_strength)
        
        return blurred_image
