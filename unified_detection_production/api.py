"""
Main API Module
"""

import cv2
import time
import numpy as np
from pathlib import Path
from typing import Union, Dict, List
from unified_detector import UnifiedDetector
from visualizer import DetectionVisualizer

# Global instances
_detector = None
_visualizer = None

def _get_detector():
    """Get or create detector instance"""
    global _detector
    if _detector is None:
        _detector = UnifiedDetector()
    return _detector

def _get_visualizer():
    """Get or create visualizer instance"""
    global _visualizer
    if _visualizer is None:
        _visualizer = DetectionVisualizer()
    return _visualizer

def detect_objects(image: Union[str, Path, np.ndarray], 
                  detect_face: bool = True, 
                  detect_lp: bool = True) -> Dict[str, List[Dict]]:
    """
    Detect faces and license plates in an image.
    
    Args:
        image: Input image (file path, Path object, or numpy array)
        detect_face: Whether to detect faces
        detect_lp: Whether to detect license plates
        
    Returns:
        Dictionary with 'faces' and 'license_plates' lists containing detection results
    """
    detector = _get_detector()
    
    # Load image if path is provided
    if isinstance(image, (str, Path)):
        image = cv2.imread(str(image))
        if image is None:
            raise ValueError(f"Failed to load image: {image}")
    
    # Perform detection
    results = detector.detect_objects(image, detect_face=detect_face, detect_lp=detect_lp)
    
    return results

def visualize_detections(image: Union[str, Path, np.ndarray], 
                        results: Dict[str, List[Dict]], 
                        show_confidence: bool = True,
                        save_path: Union[str, Path, None] = None) -> np.ndarray:
    """
    Visualize detection results on an image.
    
    Args:
        image: Input image (file path, Path object, or numpy array)
        results: Detection results from detect_objects()
        show_confidence: Whether to show confidence scores
        save_path: Optional path to save the visualization
        
    Returns:
        Image with drawn bounding boxes as numpy array
    """
    visualizer = _get_visualizer()
    
    # Load image if path is provided
    if isinstance(image, (str, Path)):
        image = cv2.imread(str(image))
        if image is None:
            raise ValueError(f"Failed to load image: {image}")
    
    # Draw detections
    result_image = visualizer.draw_boxes(image, results, show_confidence)
    
    # Save image if path provided
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), result_image)
        print(f"💾 Visualization saved to: {save_path}")
    
    return result_image

def blur_detections(image: Union[str, Path, np.ndarray], 
                   results: Dict[str, List[Dict]], 
                   face_blur_strength: int = 15,
                   plate_blur_strength: int = 15,
                   save_path: Union[str, Path, None] = None) -> np.ndarray:
    """
    Blur detected faces and license plates in the image.
    
    Args:
        image: Input image (file path, Path object, or numpy array)
        results: Detection results from detect_objects()
        face_blur_strength: Blur strength for faces - oval blur (default: 15)
        plate_blur_strength: Blur strength for license plates - rectangular blur (default: 15)
        save_path: Optional path to save the blurred image
        
    Returns:
        Image with blurred detections as numpy array
    """
    visualizer = _get_visualizer()
    
    # Load image if path is provided
    if isinstance(image, (str, Path)):
        image = cv2.imread(str(image))
        if image is None:
            raise ValueError(f"Failed to load image: {image}")
    
    # Create blurred image
    blurred_image = visualizer.blur_detections(
        image, results, face_blur_strength, plate_blur_strength
    )
    
    # Save image if path provided
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), blurred_image)
        print(f"🔒 Blurred image saved to: {save_path}")
    
    return blurred_image
