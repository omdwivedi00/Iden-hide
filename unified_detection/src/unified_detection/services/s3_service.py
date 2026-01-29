"""S3 processing service using shared detector/visualizer instances."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional

from ..config import Settings
from ..logging import get_logger
from ..core.detector import UnifiedDetector
from ..core.blur import DetectionVisualizer
from .s3_processor import S3ImageProcessor

logger = get_logger(__name__)


class S3ProcessingService:
    """Service for processing S3 images."""

    def __init__(
        self,
        detector: UnifiedDetector,
        visualizer: DetectionVisualizer,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or Settings()
        self.detector = detector
        self.visualizer = visualizer
        self.processors: Dict[str, S3ImageProcessor] = {}

    def _get_processor(self, credentials: Dict[str, str]) -> S3ImageProcessor:
        cred_key = f"{credentials['aws_access_key_id']}_{credentials['aws_secret_access_key']}"
        if cred_key not in self.processors:
            self.processors[cred_key] = S3ImageProcessor(
                aws_access_key_id=credentials['aws_access_key_id'],
                aws_secret_access_key=credentials['aws_secret_access_key'],
                aws_session_token=credentials.get('aws_session_token'),
                detector=self.detector,
                visualizer=self.visualizer,
                settings=self.settings,
            )
        return self.processors[cred_key]

    def process_single_image(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        try:
            credentials = request_data['credentials']
            processor = self._get_processor(credentials)
            result = processor.process_single_image(
                input_s3_path=request_data['input_s3_path'],
                output_s3_path=request_data['output_s3_path'],
                detect_face=request_data.get('detect_face', True),
                detect_license_plate=request_data.get('detect_license_plate', True),
                face_blur_strength=request_data.get('face_blur_strength', 25),
                plate_blur_strength=request_data.get('plate_blur_strength', 20),
            )
            processing_time = time.time() - start_time
            return {
                "success": result.get("success", False),
                "message": "OK" if result.get("success") else result.get("error", "Failed"),
                "result": result,
                "processing_time_seconds": round(processing_time, 2),
            }
        except Exception as exc:
            processing_time = time.time() - start_time
            logger.exception("S3 single image processing failed: %s", exc)
            return {
                "success": False,
                "message": f"Processing failed: {exc}",
                "result": None,
                "processing_time_seconds": round(processing_time, 2),
            }

    def process_folder(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        try:
            credentials = request_data['credentials']
            processor = self._get_processor(credentials)
            result = processor.process_s3_folder(
                input_s3_folder=request_data['input_s3_folder'],
                output_s3_folder=request_data['output_s3_folder'],
                detect_face=request_data.get('detect_face', True),
                detect_license_plate=request_data.get('detect_license_plate', True),
                face_blur_strength=request_data.get('face_blur_strength', 25),
                plate_blur_strength=request_data.get('plate_blur_strength', 20),
            )
            total_time = time.time() - start_time
            if result.get("success"):
                result["total_processing_time_seconds"] = round(total_time, 2)
                result["average_time_per_image"] = round(
                    (total_time / max(1, result.get("total_images", 1))), 2
                )
            return result
        except Exception as exc:
            processing_time = time.time() - start_time
            logger.exception("S3 folder processing failed: %s", exc)
            return {
                "success": False,
                "message": f"Folder processing failed: {exc}",
                "input_folder": request_data.get('input_s3_folder', ''),
                "output_folder": request_data.get('output_s3_folder', ''),
                "total_images": 0,
                "successful_count": 0,
                "failed_count": 0,
                "results": [],
                "total_processing_time_seconds": round(processing_time, 2),
                "average_time_per_image": 0.0,
            }

    def process_folder_parallel(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        credentials = request_data['credentials']
        processor = self._get_processor(credentials)

        input_s3_folder = request_data['input_s3_folder']
        output_s3_folder = request_data['output_s3_folder']
        detect_face = request_data.get('detect_face', True)
        detect_license_plate = request_data.get('detect_license_plate', True)
        face_blur_strength = request_data.get('face_blur_strength', 25)
        plate_blur_strength = request_data.get('plate_blur_strength', 20)
        max_workers = int(request_data.get('max_workers', self.settings.max_workers))
        max_workers = min(max_workers, 8)

        try:
            input_images = processor._list_images_in_s3_folder(input_s3_folder)
            if not input_images:
                return {
                    "success": True,
                    "message": "No images found in the specified S3 folder",
                    "input_folder": input_s3_folder,
                    "output_folder": output_s3_folder,
                    "total_images": 0,
                    "successful_count": 0,
                    "failed_count": 0,
                    "results": [],
                    "total_processing_time_seconds": 0.0,
                    "average_time_per_image": 0.0,
                }

            def _process_one(input_s3_path: str) -> Dict[str, Any]:
                bucket_name, input_key = processor._parse_s3_path(input_s3_path)
                filename = input_key.split('/')[-1]
                output_bucket, output_prefix = processor._parse_s3_path(output_s3_folder)
                output_key = f"{output_prefix.rstrip('/')}/{filename}"
                output_s3_path = f"s3://{output_bucket}/{output_key}"
                return processor.process_single_image(
                    input_s3_path=input_s3_path,
                    output_s3_path=output_s3_path,
                    detect_face=detect_face,
                    detect_license_plate=detect_license_plate,
                    face_blur_strength=face_blur_strength,
                    plate_blur_strength=plate_blur_strength,
                )

            results: List[Dict[str, Any]] = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for result in executor.map(_process_one, input_images):
                    results.append(result)

            successful_count = sum(1 for r in results if r.get("success"))
            total_time = time.time() - start_time

            return {
                "success": True,
                "message": f"Successfully processed {successful_count}/{len(input_images)} images",
                "input_folder": input_s3_folder,
                "output_folder": output_s3_folder,
                "total_images": len(input_images),
                "successful_count": successful_count,
                "failed_count": len(input_images) - successful_count,
                "results": results,
                "total_processing_time_seconds": round(total_time, 2),
                "average_time_per_image": round(total_time / max(1, len(input_images)), 2),
            }
        except Exception as exc:
            processing_time = time.time() - start_time
            logger.exception("S3 parallel folder processing failed: %s", exc)
            return {
                "success": False,
                "message": f"Folder processing failed: {exc}",
                "input_folder": input_s3_folder,
                "output_folder": output_s3_folder,
                "total_images": 0,
                "successful_count": 0,
                "failed_count": 0,
                "results": [],
                "total_processing_time_seconds": round(processing_time, 2),
                "average_time_per_image": 0.0,
            }
