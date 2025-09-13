#!/usr/bin/env python3
"""
Test the Unified Detection API
"""

import requests
import json
import time
import os
from pathlib import Path

def test_detection_api(server_url, image_path):
    """Test detection API"""
    print(f"🔍 Testing detection API with {os.path.basename(image_path)}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'detect_face': True,
                'detect_license_plate': True
            }
            
            response = requests.post(f"{server_url}/detect", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result['message']}")
                print(f"   📊 Faces: {result['total_faces']}, License Plates: {result['total_license_plates']}")
                print(f"   ⏱️  Processing time: {result['processing_time_ms']}ms")
                
                for i, detection in enumerate(result['detections']):
                    print(f"      {i+1}. {detection['label']}: BBox({detection['x1']}, {detection['y1']}, {detection['x2']}, {detection['y2']}) - Conf: {detection['confidence']:.3f}")
                
                return True
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_blur_api(server_url, image_path):
    """Test blur API"""
    print(f"🔒 Testing blur API with {os.path.basename(image_path)}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'detect_face': True,
                'detect_license_plate': True,
                'face_blur_strength': 25,
                'plate_blur_strength': 20
            }
            
            response = requests.post(f"{server_url}/blur", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result['message']}")
                print(f"   🔒 Objects blurred: {result['detections_applied']}")
                print(f"   💾 Output: {result['blurred_image_path']}")
                print(f"   ⏱️  Processing time: {result['processing_time_ms']}ms")
                return True
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_health(server_url):
    """Test health endpoint"""
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main test function"""
    server_url = "http://localhost:8000"
    
    print("🚀 Unified Detection API Test")
    print("=" * 40)
    
    # Test health
    if not test_health(server_url):
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Test images
    test_images = [
        "test_images/frame_000000.png",
        "test_images/frame_000020.png",
        "test_images/frame_000030.png"
    ]
    
    print(f"\n📸 Testing with {len(test_images)} images...")
    
    success_count = 0
    total_tests = len(test_images) * 2  # detection + blur for each image
    
    for i, image_path in enumerate(test_images):
        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"📸 Image {i+1}: {os.path.basename(image_path)}")
        print('='*60)
        
        # Test detection
        if test_detection_api(server_url, image_path):
            success_count += 1
        
        # Test blur
        if test_blur_api(server_url, image_path):
            success_count += 1
    
    print(f"\n🎉 Testing completed!")
    print(f"📊 Success rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")

if __name__ == "__main__":
    main()
