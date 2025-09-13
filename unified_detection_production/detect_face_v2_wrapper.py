#!/usr/bin/env python3
"""
Wrapper for detect_face_v2.py to match the expected interface
"""

import os
import tempfile
import json
from detect_face_v2 import run as detect_faces_v2

class DetectFace:
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        """Initialize the face detector"""
        if not self.initialized:
            # The v2 detector initializes models on first use
            self.initialized = True
    
    def detect_faces(self, image, **kwargs):
        """
        Detect faces in an image using detect_face_v2.py
        
        Args:
            image: Input image as numpy array
            **kwargs: Additional parameters for face detection
            
        Returns:
            list: List of face detections in format [x1, y1, x2, y2, confidence]
        """
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_input = tmp_file.name
                import cv2
                cv2.imwrite(temp_input, image)
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_output = tmp_file.name
            
            # Set default parameters for v2 detector
            params = {
                'source': temp_input,
                'out_path': temp_output,
                'yolo_w': kwargs.get('yolo_w', 'yolov8x.pt'),
                'pconf': kwargs.get('person_conf', 0.25),
                'imgsz': kwargs.get('imgsz', 832),
                'person_nms_iou': kwargs.get('person_nms_iou', 0.60),
                'face_size': kwargs.get('face_det_size', 1600),
                'fthr': kwargs.get('face_det_thresh', 0.20),
                'flip_tta': kwargs.get('flip_tta', False),
                'roi_scale': kwargs.get('roi_scale', 1.10),
                'roi_square': kwargs.get('roi_square', False),
                'grid': kwargs.get('grid', '2x2'),
                'overlap': kwargs.get('overlap', 0.30),
                'head_frac': kwargs.get('head_frac', 0.45),
                'size_min_rel': kwargs.get('size_min_rel', 0.10),
                'size_max_rel': kwargs.get('size_max_rel', 0.55)
            }
            
            # Run the v2 detector
            detect_faces_v2(**params)
            
            # Read the JSON output
            json_path = os.path.splitext(temp_output)[0] + '.json'
            faces = []
            
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    face_data = data.get('faces', [])
                    # Convert to the expected format: [x1, y1, x2, y2, confidence]
                    for face in face_data:
                        if isinstance(face, dict) and 'bbox' in face:
                            bbox = face['bbox']
                            score = face.get('score', 0.0)
                            faces.append([bbox[0], bbox[1], bbox[2], bbox[3], score])
                        elif isinstance(face, list) and len(face) >= 5:
                            # Already in the correct format
                            faces.append(face)
            
            # Clean up temporary files
            try:
                os.unlink(temp_input)
                os.unlink(temp_output)
                if os.path.exists(json_path):
                    os.unlink(json_path)
            except:
                pass
            
            return faces
            
        except Exception as e:
            print(f"Error in face detection: {e}")
            return []
    
    def detect(self, image, **kwargs):
        """
        Detect faces in an image (numpy array)
        
        Args:
            image: Input image as numpy array
            **kwargs: Additional parameters
            
        Returns:
            list: List of face detections
        """
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_input = tmp_file.name
            import cv2
            cv2.imwrite(temp_input, image)
        
        try:
            faces = self.detect_faces(temp_input, **kwargs)
            return faces
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_input)
            except:
                pass
