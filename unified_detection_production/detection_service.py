"""
Detection Service Module
"""

import time
import os
from typing import List, Dict, Any
import cv2
import numpy as np
from pathlib import Path

from api import detect_objects, blur_detections
from models import BoundingBox, DetectionResponse, BlurResponse

class DetectionService:
    """Service class for handling detection operations"""
    
    def __init__(self):
        """Initialize the detection service"""
        self.upload_dir = Path("uploads")
        self.output_dir = Path("output")
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def detect_objects_in_image(self, 
                              image_path: str, 
                              detect_face: bool = True, 
                              detect_license_plate: bool = True) -> DetectionResponse:
        """Detect objects in an image and return bounding box information"""
        start_time = time.time()
        
        try:
            # Perform detection using the unified detection system
            results = detect_objects(
                image_path, 
                detect_face=detect_face, 
                detect_lp=detect_license_plate
            )
            
            # Convert results to BoundingBox objects
            detections = []
            
            # Process face detections
            if detect_face and 'faces' in results:
                for face in results['faces']:
                    # Handle both list format [x1, y1, x2, y2, confidence] and dict format
                    if isinstance(face, list) and len(face) >= 5:
                        # List format: [x1, y1, x2, y2, confidence]
                        detections.append(BoundingBox(
                            x1=int(face[0]),
                            y1=int(face[1]),
                            x2=int(face[2]),
                            y2=int(face[3]),
                            confidence=float(face[4]),
                            label="face"
                        ))
                    elif isinstance(face, dict) and 'bbox' in face:
                        # Dict format: {'bbox': [x1, y1, x2, y2], 'confidence': score}
                        bbox = face['bbox']
                        detections.append(BoundingBox(
                            x1=int(bbox[0]),
                            y1=int(bbox[1]),
                            x2=int(bbox[2]),
                            y2=int(bbox[3]),
                            confidence=float(face.get('confidence', 0.0)),
                            label="face"
                        ))
            
            # Process license plate detections
            if detect_license_plate and 'license_plates' in results:
                for plate in results['license_plates']:
                    bbox = plate['bbox']
                    detections.append(BoundingBox(
                        x1=int(bbox[0]),
                        y1=int(bbox[1]),
                        x2=int(bbox[2]),
                        y2=int(bbox[3]),
                        confidence=float(plate['confidence']),
                        label="license_plate"
                    ))
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return DetectionResponse(
                success=True,
                message=f"Successfully detected {len(detections)} objects",
                detections=detections,
                total_faces=len([d for d in detections if d.label == "face"]),
                total_license_plates=len([d for d in detections if d.label == "license_plate"]),
                processing_time_ms=round(processing_time, 2)
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return DetectionResponse(
                success=False,
                message=f"Detection failed: {str(e)}",
                detections=[],
                total_faces=0,
                total_license_plates=0,
                processing_time_ms=round(processing_time, 2)
            )
    
    def blur_objects_in_image(self, 
                            image_path: str, 
                            detect_face: bool = True, 
                            detect_license_plate: bool = True,
                            face_blur_strength: int = 15,
                            plate_blur_strength: int = 15) -> BlurResponse:
        """Blur detected objects in an image"""
        start_time = time.time()
        
        try:
            # First detect objects
            results = detect_objects(
                image_path, 
                detect_face=detect_face, 
                detect_lp=detect_license_plate
            )
            
            # Count total detections
            total_detections = 0
            if detect_face and 'faces' in results:
                total_detections += len(results['faces'])
            if detect_license_plate and 'license_plates' in results:
                total_detections += len(results['license_plates'])
            
            # Generate output filename
            input_filename = Path(image_path).stem
            output_filename = f"{input_filename}_blurred.jpg"
            output_path = self.output_dir / output_filename
            
            # Apply blur using the unified detection system
            blurred_image = blur_detections(
                image_path,
                results,
                face_blur_strength=face_blur_strength,
                plate_blur_strength=plate_blur_strength,
                save_path=str(output_path)
            )
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return BlurResponse(
                success=True,
                message=f"Successfully blurred {total_detections} objects",
                blurred_image_path=str(output_path),
                detections_applied=total_detections,
                processing_time_ms=round(processing_time, 2)
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return BlurResponse(
                success=False,
                message=f"Blur operation failed: {str(e)}",
                blurred_image_path="",
                detections_applied=0,
                processing_time_ms=round(processing_time, 2)
            )
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to uploads directory"""
        # Generate unique filename to avoid conflicts
        timestamp = int(time.time())
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def validate_image(self, image_path: str) -> bool:
        """Validate that the uploaded file is a valid image"""
        try:
            image = cv2.imread(image_path)
            return image is not None
        except Exception:
            return False
