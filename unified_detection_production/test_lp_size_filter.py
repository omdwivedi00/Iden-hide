#!/usr/bin/env python3
"""
Test script for license plate detection with 30% vehicle area size filter
"""

import cv2
import numpy as np
from detect_lp import DetectLP

def test_license_plate_size_filter():
    """Test the updated license plate detection with size filtering"""
    print("🧪 Testing License Plate Detection with 30% Vehicle Area Size Filter")
    print("=" * 70)
    
    # Initialize detector
    try:
        detector = DetectLP()
        print("✅ License plate detector initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return
    
    # Test with a sample image
    test_image_path = "output/frame_000000_1757759038_blurred.jpg"
    
    try:
        # Load test image
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Could not load test image: {test_image_path}")
            print("Please ensure you have a test image available")
            return
        
        print(f"📸 Loaded test image: {test_image_path}")
        print(f"   Image shape: {image.shape}")
        
        # Test detection with size filtering (default behavior)
        print("\n🔍 Testing detection with 30% vehicle area size filter...")
        plates_filtered = detector.detect_license_plates(image, return_all_plates=False)
        
        print(f"📊 Results with size filtering:")
        print(f"   Total plates detected: {len(plates_filtered)}")
        
        for i, plate in enumerate(plates_filtered):
            bbox = plate['bbox']
            conf = plate['confidence']
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            print(f"   Plate {i+1}: bbox={bbox}, confidence={conf:.3f}, area={area}px²")
        
        # Test detection with all plates (for comparison)
        print("\n🔍 Testing detection with all plates (for comparison)...")
        plates_all = detector.detect_license_plates(image, return_all_plates=True)
        
        print(f"📊 Results with all plates:")
        print(f"   Total plates detected: {len(plates_all)}")
        
        for i, plate in enumerate(plates_all):
            bbox = plate['bbox']
            conf = plate['confidence']
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            print(f"   Plate {i+1}: bbox={bbox}, confidence={conf:.3f}, area={area}px²")
        
        print(f"\n📈 Filtering Summary:")
        print(f"   Plates with size filter: {len(plates_filtered)}")
        print(f"   Plates without size filter: {len(plates_all)}")
        print(f"   Plates filtered out: {len(plates_all) - len(plates_filtered)}")
        
        if len(plates_all) > len(plates_filtered):
            print("✅ Size filtering is working - some plates were filtered out")
        else:
            print("ℹ️ No plates were filtered out by size criteria")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_license_plate_size_filter()
