"""
S3 Processing Service
Handles S3 image processing requests
"""

import time
from typing import Dict, Any
from s3_processor import S3ImageProcessor
from models import S3ImageResult, S3SingleImageResponse, S3FolderResponse


class S3ProcessingService:
    """Service for processing S3 images"""
    
    def __init__(self):
        """Initialize S3 processing service"""
        self.processors = {}  # Cache processors by credentials
    
    def _get_processor(self, credentials: Dict[str, str]) -> S3ImageProcessor:
        """Get or create S3 processor for credentials"""
        # Create a key for caching processors
        cred_key = f"{credentials['aws_access_key_id']}_{credentials['aws_secret_access_key']}"
        
        if cred_key not in self.processors:
            self.processors[cred_key] = S3ImageProcessor(
                aws_access_key_id=credentials['aws_access_key_id'],
                aws_secret_access_key=credentials['aws_secret_access_key'],
                aws_session_token=credentials.get('aws_session_token')
            )
        
        return self.processors[cred_key]
    
    def process_single_image(self, request_data: Dict[str, Any]) -> S3SingleImageResponse:
        """Process a single image from S3"""
        start_time = time.time()
        
        try:
            # Extract credentials and parameters
            credentials = request_data['credentials']
            input_s3_path = request_data['input_s3_path']
            output_s3_path = request_data['output_s3_path']
            detect_face = request_data.get('detect_face', True)
            detect_license_plate = request_data.get('detect_license_plate', True)
            face_blur_strength = request_data.get('face_blur_strength', 25)
            plate_blur_strength = request_data.get('plate_blur_strength', 20)
            
            # Get processor
            processor = self._get_processor(credentials)
            
            # Process image
            result = processor.process_single_image(
                input_s3_path=input_s3_path,
                output_s3_path=output_s3_path,
                detect_face=detect_face,
                detect_license_plate=detect_license_plate,
                face_blur_strength=face_blur_strength,
                plate_blur_strength=plate_blur_strength
            )
            
            processing_time = time.time() - start_time
            
            if result['success']:
                # Convert to S3ImageResult
                s3_result = S3ImageResult(
                    success=True,
                    input_s3_path=result['input_s3_path'],
                    output_s3_path=result['output_s3_path'],
                    output_s3_url=result['output_s3_url'],
                    original_filename=result['original_filename'],
                    faces_detected=result['faces_detected'],
                    license_plates_detected=result['license_plates_detected'],
                    processing_time_seconds=result['processing_time_seconds']
                )
                
                return S3SingleImageResponse(
                    success=True,
                    message=f"Successfully processed {result['original_filename']}",
                    result=s3_result,
                    processing_time_seconds=round(processing_time, 2)
                )
            else:
                # Handle error case
                s3_result = S3ImageResult(
                    success=False,
                    input_s3_path=result['input_s3_path'],
                    output_s3_path="",
                    error=result['error'],
                    processing_time_seconds=result['processing_time_seconds']
                )
                
                return S3SingleImageResponse(
                    success=False,
                    message=f"Failed to process image: {result['error']}",
                    result=s3_result,
                    processing_time_seconds=round(processing_time, 2)
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return S3SingleImageResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                result=None,
                processing_time_seconds=round(processing_time, 2)
            )
    
    def process_folder(self, request_data: Dict[str, Any]) -> S3FolderResponse:
        """Process all images in an S3 folder"""
        start_time = time.time()
        
        try:
            # Extract credentials and parameters
            credentials = request_data['credentials']
            input_s3_folder = request_data['input_s3_folder']
            output_s3_folder = request_data['output_s3_folder']
            detect_face = request_data.get('detect_face', True)
            detect_license_plate = request_data.get('detect_license_plate', True)
            face_blur_strength = request_data.get('face_blur_strength', 25)
            plate_blur_strength = request_data.get('plate_blur_strength', 20)
            
            # Get processor
            processor = self._get_processor(credentials)
            
            # Process folder
            result = processor.process_s3_folder(
                input_s3_folder=input_s3_folder,
                output_s3_folder=output_s3_folder,
                detect_face=detect_face,
                detect_license_plate=detect_license_plate,
                face_blur_strength=face_blur_strength,
                plate_blur_strength=plate_blur_strength
            )
            
            processing_time = time.time() - start_time
            
            if result['success']:
                # Convert results to S3ImageResult objects
                s3_results = []
                for img_result in result['results']:
                    s3_result = S3ImageResult(
                        success=img_result['success'],
                        input_s3_path=img_result['input_s3_path'],
                        output_s3_path=img_result.get('output_s3_path', ''),
                        output_s3_url=img_result.get('output_s3_url'),
                        original_filename=img_result.get('original_filename'),
                        faces_detected=img_result.get('faces_detected', 0),
                        license_plates_detected=img_result.get('license_plates_detected', 0),
                        processing_time_seconds=img_result.get('processing_time_seconds', 0.0),
                        error=img_result.get('error')
                    )
                    s3_results.append(s3_result)
                
                return S3FolderResponse(
                    success=True,
                    message=f"Successfully processed {result['successful_count']}/{result['total_images']} images",
                    input_folder=result['input_folder'],
                    output_folder=result['output_folder'],
                    total_images=result['total_images'],
                    successful_count=result['successful_count'],
                    failed_count=result['failed_count'],
                    results=s3_results,
                    total_processing_time_seconds=round(result['total_processing_time_seconds'], 2),
                    average_time_per_image=round(result['average_time_per_image'], 2)
                )
            else:
                return S3FolderResponse(
                    success=False,
                    message=f"Folder processing failed: {result['error']}",
                    input_folder=input_s3_folder,
                    output_folder=output_s3_folder,
                    total_images=0,
                    successful_count=0,
                    failed_count=0,
                    results=[],
                    total_processing_time_seconds=round(processing_time, 2),
                    average_time_per_image=0.0
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return S3FolderResponse(
                success=False,
                message=f"Folder processing failed: {str(e)}",
                input_folder=request_data.get('input_s3_folder', ''),
                output_folder=request_data.get('output_s3_folder', ''),
                total_images=0,
                successful_count=0,
                failed_count=0,
                results=[],
                total_processing_time_seconds=round(processing_time, 2),
                average_time_per_image=0.0
            )
