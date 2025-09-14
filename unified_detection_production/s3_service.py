"""
S3 Processing Service
Handles S3 image processing requests
"""

import time
from typing import Dict, Any, List
from s3_processor import S3ImageProcessor
from models import S3ImageResult, S3SingleImageResponse, S3FolderResponse
from parallel_processor import get_parallel_processor


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
    
    def process_folder_parallel(self, request_data: Dict[str, Any]) -> S3FolderResponse:
        """Process all images in an S3 folder using parallel processing"""
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
            max_workers = request_data.get('max_workers', 4)
            
            # Get processor
            processor = self._get_processor(credentials)
            
            # List all images in the S3 folder
            image_paths = processor.list_s3_images(input_s3_folder)
            
            if not image_paths:
                return S3FolderResponse(
                    success=True,
                    message="No images found in the specified S3 folder",
                    input_folder=input_s3_folder,
                    output_folder=output_s3_folder,
                    total_images=0,
                    successful_count=0,
                    failed_count=0,
                    results=[],
                    total_processing_time_seconds=0.0,
                    average_time_per_image=0.0
                )
            
            # Download images for parallel processing
            print(f"🔄 Downloading {len(image_paths)} images for parallel processing...")
            downloaded_files = []
            for i, s3_path in enumerate(image_paths):
                try:
                    # Download image to temporary file
                    temp_file = processor.download_s3_image(s3_path)
                    if temp_file:
                        downloaded_files.append({
                            'content': temp_file['content'],
                            'filename': temp_file['filename'],
                            's3_path': s3_path,
                            'output_s3_path': s3_path.replace(input_s3_folder, output_s3_folder)
                        })
                except Exception as e:
                    print(f"⚠️ Failed to download {s3_path}: {e}")
            
            if not downloaded_files:
                return S3FolderResponse(
                    success=False,
                    message="Failed to download any images from S3 folder",
                    input_folder=input_s3_folder,
                    output_folder=output_s3_folder,
                    total_images=len(image_paths),
                    successful_count=0,
                    failed_count=len(image_paths),
                    results=[],
                    total_processing_time_seconds=time.time() - start_time,
                    average_time_per_image=0.0
                )
            
            # Process images in parallel
            print(f"⚡ Processing {len(downloaded_files)} images in parallel with {max_workers} workers...")
            parallel_processor = get_parallel_processor(max_workers)
            
            parallel_result = parallel_processor.process_images_parallel(
                files=downloaded_files,
                detect_face=detect_face,
                detect_license_plate=detect_license_plate,
                enable_blur=True,
                face_blur_strength=face_blur_strength,
                plate_blur_strength=plate_blur_strength
            )
            
            if not parallel_result['success']:
                raise Exception(f"Parallel processing failed: {parallel_result.get('message', 'Unknown error')}")
            
            # Upload processed images back to S3
            print(f"📤 Uploading {len(parallel_result['results'])} processed images to S3...")
            s3_results = []
            successful_count = 0
            failed_count = 0
            
            for result in parallel_result['results']:
                try:
                    # Find the corresponding downloaded file
                    downloaded_file = next(
                        (f for f in downloaded_files if f['filename'] == result['filename']), 
                        None
                    )
                    
                    if not downloaded_file:
                        s3_results.append(S3ImageResult(
                            success=False,
                            input_s3_path=result['filename'],
                            output_s3_path="",
                            output_s3_url=None,
                            original_filename=result['filename'],
                            faces_detected=0,
                            license_plates_detected=0,
                            processing_time_seconds=0.0,
                            error="File not found in downloaded files"
                        ))
                        failed_count += 1
                        continue
                    
                    # Upload blurred image to S3
                    if result['blur'] and result['blur'].get('blurred_image_path'):
                        # Read the blurred image file
                        with open(result['blur']['blurred_image_path'], 'rb') as f:
                            blurred_content = f.read()
                        
                        # Upload to S3
                        output_s3_path = downloaded_file['output_s3_path']
                        upload_result = processor.upload_s3_image(
                            content=blurred_content,
                            s3_path=output_s3_path,
                            content_type='image/png'
                        )
                        
                        if upload_result['success']:
                            s3_results.append(S3ImageResult(
                                success=True,
                                input_s3_path=downloaded_file['s3_path'],
                                output_s3_path=output_s3_path,
                                output_s3_url=upload_result['url'],
                                original_filename=result['filename'],
                                faces_detected=result['detection'].get('total_faces', 0),
                                license_plates_detected=result['detection'].get('total_license_plates', 0),
                                processing_time_seconds=result['processing_time'] / 1000.0,
                                error=None
                            ))
                            successful_count += 1
                        else:
                            s3_results.append(S3ImageResult(
                                success=False,
                                input_s3_path=downloaded_file['s3_path'],
                                output_s3_path=output_s3_path,
                                output_s3_url=None,
                                original_filename=result['filename'],
                                faces_detected=result['detection'].get('total_faces', 0),
                                license_plates_detected=result['detection'].get('total_license_plates', 0),
                                processing_time_seconds=result['processing_time'] / 1000.0,
                                error=f"Upload failed: {upload_result.get('error', 'Unknown error')}"
                            ))
                            failed_count += 1
                    else:
                        # No blur result, upload original
                        s3_results.append(S3ImageResult(
                            success=False,
                            input_s3_path=downloaded_file['s3_path'],
                            output_s3_path=downloaded_file['output_s3_path'],
                            output_s3_url=None,
                            original_filename=result['filename'],
                            faces_detected=result['detection'].get('total_faces', 0),
                            license_plates_detected=result['detection'].get('total_license_plates', 0),
                            processing_time_seconds=result['processing_time'] / 1000.0,
                            error="No blur result available"
                        ))
                        failed_count += 1
                
                except Exception as e:
                    s3_results.append(S3ImageResult(
                        success=False,
                        input_s3_path=result['filename'],
                        output_s3_path="",
                        output_s3_url=None,
                        original_filename=result['filename'],
                        faces_detected=0,
                        license_plates_detected=0,
                        processing_time_seconds=0.0,
                        error=f"Upload error: {str(e)}"
                    ))
                    failed_count += 1
            
            # Add failed results from parallel processing
            for failed_result in parallel_result.get('failed_results', []):
                s3_results.append(S3ImageResult(
                    success=False,
                    input_s3_path=failed_result['filename'],
                    output_s3_path="",
                    output_s3_url=None,
                    original_filename=failed_result['filename'],
                    faces_detected=0,
                    license_plates_detected=0,
                    processing_time_seconds=0.0,
                    error=failed_result.get('error', 'Processing failed')
                ))
                failed_count += 1
            
            processing_time = time.time() - start_time
            
            return S3FolderResponse(
                success=True,
                message=f"Parallel processing completed: {successful_count}/{len(image_paths)} images processed in {processing_time:.2f}s",
                input_folder=input_s3_folder,
                output_folder=output_s3_folder,
                total_images=len(image_paths),
                successful_count=successful_count,
                failed_count=failed_count,
                results=s3_results,
                total_processing_time_seconds=round(processing_time, 2),
                average_time_per_image=processing_time / len(image_paths) if len(image_paths) > 0 else 0.0
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return S3FolderResponse(
                success=False,
                message=f"Failed to process S3 folder in parallel: {str(e)}",
                input_folder=request_data.get('input_s3_folder', ''),
                output_folder=request_data.get('output_s3_folder', ''),
                total_images=0,
                successful_count=0,
                failed_count=0,
                results=[],
                total_processing_time_seconds=round(processing_time, 2),
                average_time_per_image=0.0
            )
