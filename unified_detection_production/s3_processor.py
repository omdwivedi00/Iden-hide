"""
S3 Image Processor
Processes images from S3, applies detection and blur, uploads results back to S3
"""

import os
import boto3
from boto3.session import Config
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import cv2
import numpy as np
from datetime import datetime

from unified_detector import UnifiedDetector
from visualizer import DetectionVisualizer


class S3ImageProcessor:
    """Process images from S3 with detection and blur capabilities"""
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: Optional[str] = None):
        """
        Initialize S3 processor with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_session_token: Optional AWS session token for temporary credentials
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        
        # Initialize S3 client
        self.s3_client = self._create_s3_client()
        
        # Initialize detection system
        self.detector = UnifiedDetector()
        self.visualizer = DetectionVisualizer()
        
        print("✅ S3 Image Processor initialized")
    
    def _create_s3_client(self):
        """Create S3 client with credentials"""
        try:
            session_kwargs = {
                'aws_access_key_id': self.aws_access_key_id,
                'aws_secret_access_key': self.aws_secret_access_key,
                'region_name': 'us-east-1'  # Default region
            }
            
            if self.aws_session_token:
                session_kwargs['aws_session_token'] = self.aws_session_token
            
            session = boto3.Session(**session_kwargs)
            s3_client = session.client('s3', config=Config(s3={'addressing_style': 'virtual'}))
            
            # Test connection
            s3_client.list_buckets()
            print("✅ S3 connection established")
            return s3_client
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found or invalid")
        except ClientError as e:
            raise Exception(f"Failed to create S3 client: {str(e)}")
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """
        Parse S3 path to extract bucket and key
        
        Args:
            s3_path: S3 path in format 's3://bucket-name/path/to/file'
            
        Returns:
            tuple: (bucket_name, key)
        """
        if not s3_path.startswith('s3://'):
            raise ValueError("S3 path must start with 's3://'")
        
        # Remove 's3://' prefix
        path_without_prefix = s3_path[5:]
        
        # Split into bucket and key
        parts = path_without_prefix.split('/', 1)
        if len(parts) != 2:
            raise ValueError("Invalid S3 path format. Use: s3://bucket-name/path/to/file")
        
        bucket_name, key = parts
        return bucket_name, key
    
    def _download_image_from_s3(self, s3_path: str) -> tuple:
        """
        Download image from S3 to temporary file
        
        Args:
            s3_path: S3 path to image
            
        Returns:
            tuple: (local_file_path, original_filename)
        """
        try:
            bucket_name, key = self._parse_s3_path(s3_path)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Download from S3
            self.s3_client.download_file(bucket_name, key, temp_path)
            
            # Get original filename
            original_filename = Path(key).name
            
            print(f"📥 Downloaded: {s3_path} -> {temp_path}")
            return temp_path, original_filename
            
        except ClientError as e:
            raise Exception(f"Failed to download from S3: {str(e)}")
    
    def _upload_image_to_s3(self, local_path: str, s3_path: str) -> str:
        """
        Upload image to S3
        
        Args:
            local_path: Local file path
            s3_path: S3 destination path
            
        Returns:
            str: S3 URL of uploaded file
        """
        try:
            # Check if local file exists
            if not os.path.exists(local_path):
                raise Exception(f"Local file does not exist: {local_path}")
            
            # Check file size
            file_size = os.path.getsize(local_path)
            if file_size == 0:
                raise Exception(f"Local file is empty: {local_path}")
            
            bucket_name, key = self._parse_s3_path(s3_path)
            print(f"📤 Uploading: {local_path} ({file_size} bytes) -> s3://{bucket_name}/{key}")
            
            # Upload to S3 with extra parameters
            self.s3_client.upload_file(
                local_path, 
                bucket_name, 
                key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'ACL': 'private'  # Make sure file is accessible
                }
            )
            
            # Verify upload by checking if object exists
            try:
                self.s3_client.head_object(Bucket=bucket_name, Key=key)
                print(f"✅ Upload verified: s3://{bucket_name}/{key}")
            except ClientError as e:
                print(f"⚠️ Upload verification failed: {e}")
            
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
            print(f"📤 Uploaded: {local_path} -> {s3_url}")
            return s3_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"Failed to upload to S3: {error_code} - {error_message}")
        except Exception as e:
            raise Exception(f"Upload error: {str(e)}")
    
    def _list_images_in_s3_folder(self, s3_folder_path: str) -> List[str]:
        """
        List all image files in S3 folder
        
        Args:
            s3_folder_path: S3 folder path (e.g., 's3://bucket-name/folder/')
            
        Returns:
            List[str]: List of S3 paths to image files
        """
        try:
            bucket_name, prefix = self._parse_s3_path(s3_folder_path)
            print(f"📁 Listing S3 folder: s3://{bucket_name}/{prefix}")
            
            # Ensure prefix ends with '/'
            if not prefix.endswith('/'):
                prefix += '/'
            
            # List objects in folder
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            print(f"📊 S3 response: {response.get('KeyCount', 0)} objects found")
            
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            image_paths = []
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    file_ext = Path(key).suffix.lower()
                    file_size = obj.get('Size', 0)
                    
                    print(f"📄 Found file: {key} ({file_size} bytes, ext: {file_ext})")
                    
                    if file_ext in image_extensions:
                        s3_path = f"s3://{bucket_name}/{key}"
                        image_paths.append(s3_path)
                        print(f"✅ Added image: {s3_path}")
                    else:
                        print(f"⏭️ Skipped non-image: {key}")
            else:
                print(f"⚠️ No objects found in s3://{bucket_name}/{prefix}")
            
            print(f"📁 Found {len(image_paths)} images in {s3_folder_path}")
            return image_paths
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"Failed to list S3 folder: {error_code} - {error_message}")
        except Exception as e:
            raise Exception(f"Folder listing error: {str(e)}")
    
    def process_single_image(self, 
                           input_s3_path: str, 
                           output_s3_path: str,
                           detect_face: bool = True,
                           detect_license_plate: bool = True,
                           face_blur_strength: int = 25,
                           plate_blur_strength: int = 20) -> Dict:
        """
        Process a single image from S3
        
        Args:
            input_s3_path: S3 path to input image
            output_s3_path: S3 path for output image
            detect_face: Whether to detect faces
            detect_license_plate: Whether to detect license plates
            face_blur_strength: Blur strength for faces
            plate_blur_strength: Blur strength for license plates
            
        Returns:
            Dict: Processing results
        """
        start_time = datetime.now()
        
        try:
            # Download image from S3
            local_input_path, original_filename = self._download_image_from_s3(input_s3_path)
            
            # Load image
            image = cv2.imread(local_input_path)
            if image is None:
                raise Exception(f"Failed to load image: {local_input_path}")
            
            # Detect objects
            detection_results = self.detector.detect_objects(
                image, 
                detect_face=detect_face, 
                detect_lp=detect_license_plate
            )
            
            # Apply blur
            blurred_image = self.visualizer.blur_detections(
                image, 
                detection_results,
                face_blur_strength=face_blur_strength,
                plate_blur_strength=plate_blur_strength
            )
            
            # Save blurred image to temporary file
            temp_output = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_output_path = temp_output.name
            temp_output.close()
            
            cv2.imwrite(temp_output_path, blurred_image)
            
            # Upload to S3
            s3_url = self._upload_image_to_s3(temp_output_path, output_s3_path)
            
            # Clean up temporary files
            os.unlink(local_input_path)
            os.unlink(temp_output_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'input_s3_path': input_s3_path,
                'output_s3_path': output_s3_path,
                'output_s3_url': s3_url,
                'original_filename': original_filename,
                'detection_results': detection_results,
                'faces_detected': len(detection_results.get('faces', [])),
                'license_plates_detected': len(detection_results.get('license_plates', [])),
                'processing_time_seconds': round(processing_time, 2)
            }
            
        except Exception as e:
            # Clean up temporary files on error
            try:
                if 'local_input_path' in locals():
                    os.unlink(local_input_path)
                if 'temp_output_path' in locals():
                    os.unlink(temp_output_path)
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'input_s3_path': input_s3_path,
                'processing_time_seconds': round((datetime.now() - start_time).total_seconds(), 2)
            }
    
    def process_s3_folder(self, 
                         input_s3_folder: str,
                         output_s3_folder: str,
                         detect_face: bool = True,
                         detect_license_plate: bool = True,
                         face_blur_strength: int = 25,
                         plate_blur_strength: int = 20) -> Dict:
        """
        Process all images in an S3 folder
        
        Args:
            input_s3_folder: S3 folder path containing input images
            output_s3_folder: S3 folder path for output images
            detect_face: Whether to detect faces
            detect_license_plate: Whether to detect license plates
            face_blur_strength: Blur strength for faces
            plate_blur_strength: Blur strength for license plates
            
        Returns:
            Dict: Batch processing results
        """
        start_time = datetime.now()
        
        try:
            # List all images in input folder
            input_images = self._list_images_in_s3_folder(input_s3_folder)
            
            if not input_images:
                return {
                    'success': False,
                    'error': 'No images found in input folder',
                    'input_folder': input_s3_folder,
                    'processed_count': 0,
                    'total_count': 0
                }
            
            # Process each image
            results = []
            successful_count = 0
            
            for i, input_s3_path in enumerate(input_images):
                print(f"🔄 Processing {i+1}/{len(input_images)}: {input_s3_path}")
                
                # Generate output path - preserve original filename
                bucket_name, input_key = self._parse_s3_path(input_s3_path)
                filename = Path(input_key).name
                
                # Parse output folder to get the correct bucket and prefix
                output_bucket, output_prefix = self._parse_s3_path(output_s3_folder)
                
                # Keep original filename without adding _blurred suffix
                output_key = f"{output_prefix.rstrip('/')}/{filename}"
                output_s3_path = f"s3://{output_bucket}/{output_key}"
                
                # Process image
                result = self.process_single_image(
                    input_s3_path,
                    output_s3_path,
                    detect_face,
                    detect_license_plate,
                    face_blur_strength,
                    plate_blur_strength
                )
                
                results.append(result)
                
                if result['success']:
                    successful_count += 1
                    print(f"✅ Success: {result['original_filename']}")
                else:
                    print(f"❌ Failed: {result['error']}")
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'input_folder': input_s3_folder,
                'output_folder': output_s3_folder,
                'total_images': len(input_images),
                'successful_count': successful_count,
                'failed_count': len(input_images) - successful_count,
                'results': results,
                'total_processing_time_seconds': round(total_time, 2),
                'average_time_per_image': round(total_time / len(input_images), 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_folder': input_s3_folder,
                'processed_count': 0,
                'total_count': 0
            }


def test_s3_processor():
    """Test S3 processor functionality"""
    try:
        # Test with environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        
        if not aws_access_key_id or not aws_secret_access_key:
            print("❌ AWS credentials not found in environment variables")
            return False
        
        processor = S3ImageProcessor(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        
        print("✅ S3 Processor test successful")
        return True
        
    except Exception as e:
        print(f"❌ S3 Processor test failed: {e}")
        return False


if __name__ == "__main__":
    test_s3_processor()
