#!/usr/bin/env python3
"""
Test S3 API Endpoints
Test the S3 processing functionality
"""

import requests
import json
import os
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_s3_credentials():
    """Test S3 credentials endpoint"""
    print("🔐 Testing S3 credentials...")
    
    # You can set these as environment variables or replace with actual values
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-key')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN', None)
    
    params = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key
    }
    
    if aws_session_token:
        params['aws_session_token'] = aws_session_token
    
    try:
        response = requests.get(f"{BASE_URL}/s3/test-credentials", params=params)
        result = response.json()
        
        if result['success']:
            print("✅ S3 credentials are valid")
            return True
        else:
            print(f"❌ S3 credentials test failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False

def test_s3_single_image():
    """Test single image processing from S3"""
    print("\n🖼️ Testing S3 single image processing...")
    
    # Example S3 paths - replace with your actual S3 paths
    request_data = {
        "credentials": {
            "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key'),
            "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-key'),
            "aws_session_token": os.getenv('AWS_SESSION_TOKEN', None)
        },
        "input_s3_path": "s3://your-bucket/input/test-image.jpg",
        "output_s3_path": "s3://your-bucket/output/test-image-blurred.jpg",
        "detect_face": True,
        "detect_license_plate": True,
        "face_blur_strength": 25,
        "plate_blur_strength": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/s3/process-single",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Single image processing successful")
            print(f"   Input: {result['result']['input_s3_path']}")
            print(f"   Output: {result['result']['output_s3_path']}")
            print(f"   Faces detected: {result['result']['faces_detected']}")
            print(f"   License plates detected: {result['result']['license_plates_detected']}")
            print(f"   Processing time: {result['processing_time_seconds']}s")
            return True
        else:
            print(f"❌ Single image processing failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing single image: {e}")
        return False

def test_s3_folder():
    """Test folder processing from S3"""
    print("\n📁 Testing S3 folder processing...")
    
    # Example S3 folder paths - replace with your actual S3 paths
    request_data = {
        "credentials": {
            "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key'),
            "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-key'),
            "aws_session_token": os.getenv('AWS_SESSION_TOKEN', None)
        },
        "input_s3_folder": "s3://your-bucket/input/",
        "output_s3_folder": "s3://your-bucket/output/",
        "detect_face": True,
        "detect_license_plate": True,
        "face_blur_strength": 25,
        "plate_blur_strength": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/s3/process-folder",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Folder processing successful")
            print(f"   Input folder: {result['input_folder']}")
            print(f"   Output folder: {result['output_folder']}")
            print(f"   Total images: {result['total_images']}")
            print(f"   Successful: {result['successful_count']}")
            print(f"   Failed: {result['failed_count']}")
            print(f"   Total time: {result['total_processing_time_seconds']}s")
            print(f"   Average time per image: {result['average_time_per_image']}s")
            return True
        else:
            print(f"❌ Folder processing failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing folder: {e}")
        return False

def test_api_health():
    """Test if API is running"""
    print("🏥 Testing API health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API is not running: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting S3 API Tests")
    print("=" * 50)
    
    # Test API health first
    if not test_api_health():
        print("\n❌ API is not running. Please start the server first.")
        return
    
    # Test S3 credentials
    if not test_s3_credentials():
        print("\n⚠️ S3 credentials test failed. Please check your AWS credentials.")
        print("Set environment variables:")
        print("export AWS_ACCESS_KEY_ID=your-access-key")
        print("export AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("export AWS_SESSION_TOKEN=your-session-token  # Optional")
        return
    
    # Test single image processing
    test_s3_single_image()
    
    # Test folder processing
    test_s3_folder()
    
    print("\n" + "=" * 50)
    print("🎉 S3 API tests completed!")

if __name__ == "__main__":
    main()
