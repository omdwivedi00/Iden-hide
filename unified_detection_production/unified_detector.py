"""
Unified Detection System
"""

import cv2
import numpy as np
from detect_face_v2_wrapper import DetectFace
from detect_lp import DetectLP

class UnifiedDetector:
    def __init__(self):
        self.face_detector = None
        self.lp_detector = None
        self._initialize_detectors()

    def _initialize_detectors(self):
        """Initialize all detection modules"""
        try:
            print("🚀 Initializing Face Detection System")
            self.face_detector = DetectFace()
            print("✅ Face detection system ready")
            
            print("🚀 Initializing License Plate Detection System")
            self.lp_detector = DetectLP()
            print("✅ License plate detection system ready")
            
            print("✅ All detectors initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing detectors: {e}")
            raise

    def detect_objects(self, image, detect_face=True, detect_lp=True):
        """Detect faces and license plates in image"""
        results = {
            'faces': [],
            'license_plates': []
        }
        
        if detect_face and self.face_detector:
            try:
                faces = self.face_detector.detect_faces(image)
                results['faces'] = faces
            except Exception as e:
                print(f"❌ Face detection error: {e}")
        
        if detect_lp and self.lp_detector:
            try:
                plates = self.lp_detector.detect_license_plates(image)
                results['license_plates'] = plates
            except Exception as e:
                print(f"❌ License plate detection error: {e}")
        
        return results
