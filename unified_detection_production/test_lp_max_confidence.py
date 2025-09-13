#!/usr/bin/env python3
"""
Test script for license plate detection with maximum confidence selection
"""

import cv2
import numpy as np
from detect_lp import DetectLP

def test_license_plate_detection():
    """Test the updated license plate detection"""
    print("🧪 Testing License Plate Detection with Max Confidence Selection")
    print("=" * 60)
    
    # Initialize detector
    try:
        detector = DetectLP()
        print("✅ License plate detector initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return
    
    # Test with a sample image (you can replace this with your test image)
    test_image_path = "output/frame_000000_1757759038_blurred.jpg"  # Use existing test image
    
    try:
        # Load test image
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Could not load test image: {test_image_path}")
            print("Please ensure you have a test image available")
            return
        
        print(f"📸 Loaded test image: {test_image_path}")
        print(f"   Image shape: {image.shape}")
        
        # Test detection with max confidence selection (default behavior)
        print("\n🔍 Testing detection with max confidence selection...")
        plates_max_conf = detector.detect_license_plates(image, return_all_plates=False)
        
        print(f"📊 Results with max confidence selection:")
        print(f"   Total plates detected: {len(plates_max_conf)}")
        
        for i, plate in enumerate(plates_max_conf):
            bbox = plate['bbox']
            conf = plate['confidence']
            print(f"   Plate {i+1}: bbox={bbox}, confidence={conf:.3f}")
        
        # Test detection with all plates (for comparison)
        print("\n🔍 Testing detection with all plates (for comparison)...")
        plates_all = detector.detect_license_plates(image, return_all_plates=True)
        
        print(f"📊 Results with all plates:")
        print(f"   Total plates detected: {len(plates_all)}")
        
        for i, plate in enumerate(plates_all):
            bbox = plate['bbox']
            conf = plate['confidence']
            print(f"   Plate {i+1}: bbox={bbox}, confidence={conf:.3f}")
        
        # Compare results
        print(f"\n📈 Comparison:")
        print(f"   Max confidence mode: {len(plates_max_conf)} plates")
        print(f"   All plates mode: {len(plates_all)} plates")
        print(f"   Difference: {len(plates_all) - len(plates_max_conf)} plates filtered out")
        
        # Test with different confidence thresholds
        print(f"\n🎯 Testing different confidence thresholds...")
        original_threshold = detector.plate_conf_threshold
        
        for threshold in [0.1, 0.2, 0.3, 0.5]:
            detector.plate_conf_threshold = threshold
            plates = detector.detect_license_plates(image)
            print(f"   Threshold {threshold}: {len(plates)} plates detected")
        
        # Restore original threshold
        detector.plate_conf_threshold = original_threshold
        
        print("\n✅ License plate detection test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def create_test_image():
    """Create a simple test image with multiple rectangles to simulate vehicles"""
    print("\n🎨 Creating test image...")
    
    # Create a white image
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Draw some rectangles to simulate vehicles
    vehicles = [
        (100, 100, 200, 150),  # Vehicle 1
        (300, 200, 450, 280),  # Vehicle 2
        (500, 100, 650, 180),  # Vehicle 3
    ]
    
    for i, (x1, y1, x2, y2) in enumerate(vehicles):
        # Draw vehicle rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"Vehicle {i+1}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw some rectangles inside to simulate license plates
        plate_x1 = x1 + 10
        plate_y1 = y1 + (y2-y1)//2
        plate_x2 = plate_x1 + 80
        plate_y2 = plate_y1 + 20
        
        cv2.rectangle(img, (plate_x1, plate_y1), (plate_x2, plate_y2), (0, 255, 0), 2)
        cv2.putText(img, f"LP{i+1}", (plate_x1, plate_y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Save test image
    test_path = "test_vehicles.jpg"
    cv2.imwrite(test_path, img)
    print(f"✅ Test image created: {test_path}")
    return test_path

if __name__ == "__main__":
    # Create test image if needed
    test_image = create_test_image()
    
    # Run the test
    test_license_plate_detection()
    
    print("\n🎉 All tests completed!")
