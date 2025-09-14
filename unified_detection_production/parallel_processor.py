"""
Parallel Processing Service for Batch Image Processing
Uses the same detection and blur APIs as sequential processing
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import tempfile
import os
from detection_service import DetectionService

class ParallelProcessor:
    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel processor
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.detection_service = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize detection components"""
        try:
            print("🚀 Initializing Parallel Processing Components")
            self.detection_service = DetectionService()
            print("✅ Parallel processing components ready")
        except Exception as e:
            print(f"❌ Error initializing parallel components: {e}")
            raise
    
    def _process_single_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single image using the same APIs as sequential processing
        
        Args:
            image_data: Dictionary containing image file and processing options
            
        Returns:
            Dictionary with processing results
        """
        try:
            file_content = image_data['file_content']
            filename = image_data['filename']
            detect_face = image_data['detect_face']
            detect_license_plate = image_data['detect_license_plate']
            enable_blur = image_data.get('enable_blur', False)
            face_blur_strength = image_data.get('face_blur_strength', 25)
            plate_blur_strength = image_data.get('plate_blur_strength', 20)
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_input = tmp_file.name
                tmp_file.write(file_content)
            
            try:
                # Use detection service for detection (same as sequential)
                detection_result = self.detection_service.detect_objects_in_image(
                    image_path=temp_input,
                    detect_face=detect_face,
                    detect_license_plate=detect_license_plate
                )
                
                if not detection_result.success:
                    raise ValueError(f"Detection failed: {detection_result.message}")
                
                # Use detection service for blur (same as sequential)
                blur_result = None
                if enable_blur:
                    blur_result = self.detection_service.blur_objects_in_image(
                        image_path=temp_input,
                        detect_face=detect_face,
                        detect_license_plate=detect_license_plate,
                        face_blur_strength=face_blur_strength,
                        plate_blur_strength=plate_blur_strength
                    )
                    
                    if not blur_result.success:
                        print(f"Warning: Blur failed for {filename}: {blur_result.message}")
                        blur_result = None
                
                # Convert to the format expected by frontend
                detection_data = {
                    "success": detection_result.success,
                    "message": detection_result.message,
                    "detections": detection_result.detections,
                    "total_faces": detection_result.total_faces,
                    "total_license_plates": detection_result.total_license_plates,
                    "processing_time_ms": detection_result.processing_time_ms
                }
                
                blur_data = None
                if blur_result:
                    blur_data = {
                        "success": blur_result.success,
                        "message": blur_result.message,
                        "blurred_image_path": blur_result.blurred_image_path,
                        "detections_applied": blur_result.detections_applied,
                        "processing_time_ms": blur_result.processing_time_ms
                    }
                
                total_processing_time = detection_result.processing_time_ms
                if blur_result:
                    total_processing_time += blur_result.processing_time_ms
                
                return {
                    'success': True,
                    'filename': filename,
                    'detection': detection_data,
                    'blur': blur_data,
                    'processing_time': total_processing_time
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_input):
                    os.remove(temp_input)
                    
        except Exception as e:
            return {
                'success': False,
                'filename': filename,
                'error': str(e),
                'processing_time': 0
            }
    
    def process_images_parallel(self, 
                              files: List[Dict[str, Any]], 
                              detect_face: bool = True,
                              detect_license_plate: bool = True,
                              enable_blur: bool = False,
                              face_blur_strength: int = 25,
                              plate_blur_strength: int = 20) -> Dict[str, Any]:
        """
        Process multiple images in parallel using the same APIs as sequential processing
        
        Args:
            files: List of file data dictionaries
            detect_face: Whether to detect faces
            detect_license_plate: Whether to detect license plates
            enable_blur: Whether to apply blur
            face_blur_strength: Blur strength for faces
            plate_blur_strength: Blur strength for license plates
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        # Prepare image data for parallel processing
        image_data_list = []
        for file_data in files:
            image_data = {
                'file_content': file_data['content'],
                'filename': file_data['filename'],
                'detect_face': detect_face,
                'detect_license_plate': detect_license_plate,
                'enable_blur': enable_blur,
                'face_blur_strength': face_blur_strength,
                'plate_blur_strength': plate_blur_strength
            }
            image_data_list.append(image_data)
        
        # Process images in parallel using ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks and wait for completion
            future_to_data = {
                executor.submit(self._process_single_image, image_data): image_data 
                for image_data in image_data_list
            }
            
            for future in future_to_data:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per image
                    results.append(result)
                except Exception as e:
                    image_data = future_to_data[future]
                    results.append({
                        'success': False,
                        'filename': image_data['filename'],
                        'error': str(e),
                        'processing_time': 0
                    })
        
        # Process results
        successful_results = []
        failed_results = []
        total_processing_time = 0
        
        for result in results:
            if result['success']:
                successful_results.append(result)
                total_processing_time += result['processing_time']
            else:
                failed_results.append(result)
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'success': True,
            'message': f'Parallel processing completed: {len(successful_results)} successful, {len(failed_results)} failed',
            'total_images': len(files),
            'successful_count': len(successful_results),
            'failed_count': len(failed_results),
            'results': successful_results,
            'failed_results': failed_results,
            'total_processing_time_ms': total_time,
            'average_time_per_image_ms': total_time / len(files) if files else 0,
            'parallel_efficiency': (total_processing_time / total_time) * 100 if total_time > 0 else 0
        }

# Global instance
_parallel_processor = None

def get_parallel_processor(max_workers: int = 4) -> ParallelProcessor:
    """Get or create parallel processor instance"""
    global _parallel_processor
    if _parallel_processor is None:
        _parallel_processor = ParallelProcessor(max_workers)
    return _parallel_processor