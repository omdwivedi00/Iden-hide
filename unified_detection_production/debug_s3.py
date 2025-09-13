#!/usr/bin/env python3
"""
Debug S3 Upload Issues
Test S3 functionality with detailed logging
"""

import os
import sys
from s3_processor import S3ImageProcessor

def test_s3_connection():
    """Test basic S3 connection"""
    print("🔐 Testing S3 Connection...")
    
    # Get credentials from environment
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS credentials not found in environment variables")
        print("Please set:")
        print("export AWS_ACCESS_KEY_ID=your-access-key")
        print("export AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("export AWS_SESSION_TOKEN=your-session-token  # Optional")
        return False
    
    try:
        processor = S3ImageProcessor(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        print("✅ S3 connection established")
        return processor
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

def test_s3_folder_listing(processor, folder_path):
    """Test S3 folder listing"""
    print(f"\n📁 Testing S3 Folder Listing: {folder_path}")
    
    try:
        files = processor._list_images_in_s3_folder(folder_path)
        print(f"✅ Found {len(files)} files")
        for file in files:
            print(f"  📄 {file}")
        return files
    except Exception as e:
        print(f"❌ Folder listing failed: {e}")
        return []

def test_s3_upload(processor, local_file, s3_path):
    """Test S3 upload"""
    print(f"\n📤 Testing S3 Upload: {local_file} -> {s3_path}")
    
    if not os.path.exists(local_file):
        print(f"❌ Local file does not exist: {local_file}")
        return False
    
    try:
        s3_url = processor._upload_image_to_s3(local_file, s3_path)
        print(f"✅ Upload successful: {s3_url}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def test_s3_download(processor, s3_path, local_path):
    """Test S3 download"""
    print(f"\n📥 Testing S3 Download: {s3_path} -> {local_path}")
    
    try:
        local_file, filename = processor._download_image_from_s3(s3_path)
        print(f"✅ Download successful: {local_file}")
        print(f"📄 Original filename: {filename}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🐛 S3 Debug Tool")
    print("=" * 50)
    
    # Test connection
    processor = test_s3_connection()
    if not processor:
        return
    
    # Test folder listing
    input_folder = input("\nEnter S3 input folder path (e.g., s3://bucket/input/): ").strip()
    if input_folder:
        files = test_s3_folder_listing(processor, input_folder)
        
        if files:
            # Test download
            test_file = files[0]
            local_download = "test_download.jpg"
            test_s3_download(processor, test_file, local_download)
            
            # Test upload
            output_folder = input("\nEnter S3 output folder path (e.g., s3://bucket/output/): ").strip()
            if output_folder:
                # Generate output path
                bucket_name, input_key = processor._parse_s3_path(test_file)
                filename = os.path.basename(input_key)
                output_bucket, output_prefix = processor._parse_s3_path(output_folder)
                output_key = f"{output_prefix.rstrip('/')}/{filename}"
                output_s3_path = f"s3://{output_bucket}/{output_key}"
                
                print(f"\n📤 Generated output path: {output_s3_path}")
                test_s3_upload(processor, local_download, output_s3_path)
                
                # Clean up
                if os.path.exists(local_download):
                    os.remove(local_download)
                    print(f"🧹 Cleaned up: {local_download}")
    
    print("\n🎉 Debug complete!")

if __name__ == "__main__":
    main()
