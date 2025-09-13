#!/usr/bin/env python3
"""
Simple Test Script - One Image, All Endpoints
"""

import requests
import cv2
import os

# Configuration
BASE_URL = "http://localhost:8000"
IMAGE_PATH = "test_images/frame_000000.png"  # Change this to your image

def test_detection():
    """Test detection endpoint"""
    print("🔍 Testing Detection API...")
    
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': (os.path.basename(IMAGE_PATH), f, 'image/png')}
        data = {'detect_face': True, 'detect_license_plate': True}
        
        response = requests.post(f"{BASE_URL}/detect", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['total_faces']} faces, {result['total_license_plates']} license plates")
            
            # Draw bounding boxes
            image = cv2.imread(IMAGE_PATH)
            for detection in result['detections']:
                x1, y1, x2, y2 = detection['x1'], detection['y1'], detection['x2'], detection['y2']
                color = (0, 255, 0) if detection['label'] == 'face' else (0, 0, 255)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{detection['label']}: {detection['confidence']:.3f}", 
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Save and show
            cv2.imwrite("demo_output.jpg", image)
            print("💾 Saved: demo_output.jpg")
            
            # Display
            cv2.imshow("Detection Results", image)
            print("⌨️  Press any key to continue...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        else:
            print(f"❌ Error: {response.status_code}")

def test_blur():
    """Test blur endpoint"""
    print("\n🔒 Testing Blur API...")
    
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': (os.path.basename(IMAGE_PATH), f, 'image/png')}
        data = {'detect_face': True, 'detect_license_plate': True, 
                'face_blur_strength': 25, 'plate_blur_strength': 20}
        
        response = requests.post(f"{BASE_URL}/blur", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Blurred {result['detections_applied']} objects")
            print(f"💾 Saved: {result['blurred_image_path']}")
            
            # Load and show blurred image
            blurred_image = cv2.imread(result['blurred_image_path'])
            if blurred_image is not None:
                cv2.imshow("Blurred Image", blurred_image)
                print("⌨️  Press any key to continue...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            print(f"❌ Error: {response.status_code}")

def main():
    print("🚀 Simple Detection Test")
    print("=" * 40)
    
    # Check if image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found: {IMAGE_PATH}")
        return
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running")
            return
    except:
        print("❌ Cannot connect to server")
        print("💡 Start server: python main.py")
        return
    
    print("✅ Server is running")
    
    # Test detection
    test_detection()
    
    # Test blur
    test_blur()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
