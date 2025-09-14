#!/usr/bin/env python3
"""
Test script for parallel processing functionality
"""

import requests
import time
import os
from pathlib import Path

def test_parallel_processing():
    """Test the parallel processing endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/process-parallel"
    
    # Test images directory
    test_images_dir = Path("unified_detection_production/test_images")
    
    if not test_images_dir.exists():
        print("❌ Test images directory not found")
        return False
    
    # Get test images
    image_files = list(test_images_dir.glob("*.png"))
    if not image_files:
        print("❌ No test images found")
        return False
    
    print(f"🧪 Testing parallel processing with {len(image_files)} images")
    
    # Prepare form data
    files = []
    for img_path in image_files[:3]:  # Test with first 3 images
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/png')))
    
    data = {
        'detect_face': True,
        'detect_license_plate': True,
        'enable_blur': True,
        'face_blur_strength': 25,
        'plate_blur_strength': 20,
        'max_workers': 2
    }
    
    try:
        print("🚀 Sending parallel processing request...")
        start_time = time.time()
        
        response = requests.post(endpoint, files=files, data=data, timeout=300)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Request completed in {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Parallel processing successful!")
            print(f"📊 Results: {result.get('successful_count', 0)}/{result.get('total_images', 0)} images processed")
            print(f"⚡ Efficiency: {result.get('parallel_efficiency', 0):.1f}%")
            print(f"🕐 Total time: {result.get('total_processing_time_ms', 0)/1000:.2f}s")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Close file handles
        for _, file_tuple in files:
            file_tuple[1].close()

def test_sequential_processing():
    """Test sequential processing for comparison"""
    
    base_url = "http://localhost:8000"
    detect_endpoint = f"{base_url}/detect"
    blur_endpoint = f"{base_url}/blur"
    
    test_images_dir = Path("unified_detection_production/test_images")
    image_files = list(test_images_dir.glob("*.png"))[:2]  # Test with 2 images
    
    if not image_files:
        print("❌ No test images found for sequential test")
        return False
    
    print(f"🧪 Testing sequential processing with {len(image_files)} images")
    
    try:
        start_time = time.time()
        results = []
        
        for img_path in image_files:
            print(f"  Processing {img_path.name}...")
            
            # Detect objects
            with open(img_path, 'rb') as f:
                detect_response = requests.post(
                    detect_endpoint,
                    files={'file': (img_path.name, f, 'image/png')},
                    data={'detect_face': True, 'detect_license_plate': True},
                    timeout=60
                )
            
            if detect_response.status_code == 200:
                # Blur objects
                with open(img_path, 'rb') as f:
                    blur_response = requests.post(
                        blur_endpoint,
                        files={'file': (img_path.name, f, 'image/png')},
                        data={
                            'detect_face': True, 
                            'detect_license_plate': True,
                            'face_blur_strength': 25,
                            'plate_blur_strength': 20
                        },
                        timeout=60
                    )
                
                if blur_response.status_code == 200:
                    results.append(img_path.name)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Sequential processing completed!")
        print(f"📊 Results: {len(results)}/{len(image_files)} images processed")
        print(f"🕐 Total time: {processing_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Sequential processing error: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Testing Iden-Hide Parallel Processing")
    print("=" * 50)
    
    # Test parallel processing
    print("\n1. Testing Parallel Processing:")
    parallel_success = test_parallel_processing()
    
    print("\n2. Testing Sequential Processing:")
    sequential_success = test_sequential_processing()
    
    print("\n" + "=" * 50)
    if parallel_success and sequential_success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
