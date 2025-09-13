#!/usr/bin/env python3
"""
Test S3 API endpoints with debugging
"""

import requests
import json
import os

API_BASE_URL = "http://localhost:8000"

def test_s3_credentials():
    """Test S3 credentials endpoint"""
    print("🔐 Testing S3 Credentials...")
    
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'test-key')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'test-secret')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    
    params = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key
    }
    
    if aws_session_token:
        params['aws_session_token'] = aws_session_token
    
    try:
        response = requests.get(f"{API_BASE_URL}/s3/test-credentials", params=params)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Credentials test passed")
            return True
        else:
            print("❌ Credentials test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_s3_list_folder():
    """Test S3 folder listing endpoint"""
    print("\n📁 Testing S3 Folder Listing...")
    
    credentials = {
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', 'test-key'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', 'test-secret'),
        'aws_session_token': os.getenv('AWS_SESSION_TOKEN')
    }
    
    folder_path = input("Enter S3 folder path (e.g., s3://bucket/input/): ").strip()
    if not folder_path:
        print("❌ No folder path provided")
        return False
    
    request_data = {
        'credentials': credentials,
        's3_folder_path': folder_path
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/s3/list-folder",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"✅ Found {result.get('total_count', 0)} files")
            return True
        else:
            print("❌ Folder listing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_s3_single_image():
    """Test S3 single image processing"""
    print("\n🖼️ Testing S3 Single Image Processing...")
    
    credentials = {
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', 'test-key'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', 'test-secret'),
        'aws_session_token': os.getenv('AWS_SESSION_TOKEN')
    }
    
    input_path = input("Enter input S3 path (e.g., s3://bucket/input/image.jpg): ").strip()
    output_path = input("Enter output S3 path (e.g., s3://bucket/output/image.jpg): ").strip()
    
    if not input_path or not output_path:
        print("❌ Missing input or output path")
        return False
    
    request_data = {
        'credentials': credentials,
        'input_s3_path': input_path,
        'output_s3_path': output_path,
        'detect_face': True,
        'detect_license_plate': True,
        'face_blur_strength': 25,
        'plate_blur_strength': 20
    }
    
    try:
        print("🚀 Processing image...")
        response = requests.post(
            f"{API_BASE_URL}/s3/process-single",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=300  # 5 minutes timeout
        )
        
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Image processing successful")
            return True
        else:
            print("❌ Image processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 S3 API Debug Tool")
    print("=" * 50)
    
    # Test credentials
    if not test_s3_credentials():
        print("\n❌ Credentials test failed. Please check your AWS credentials.")
        return
    
    # Test folder listing
    test_s3_list_folder()
    
    # Test single image processing
    test_s3_single_image()
    
    print("\n🎉 Debug complete!")

if __name__ == "__main__":
    main()
