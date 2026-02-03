"""API routes for unified detection."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from ..config import Settings
from ..core.blur import DetectionVisualizer
from ..core.detector import UnifiedDetector
from ..services.s3_service import S3ProcessingService

router = APIRouter()


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str


class DetectionResponse(BaseModel):
    success: bool
    message: str
    detections: List[BoundingBox]
    total_faces: int
    total_license_plates: int
    processing_time_ms: float


class BlurResponse(BaseModel):
    success: bool
    message: str
    blurred_image_path: str
    detections_applied: int
    processing_time_ms: float


class S3Credentials(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: Optional[str] = None


class S3SingleImageRequest(BaseModel):
    credentials: S3Credentials
    input_s3_path: str
    output_s3_path: str
    detect_face: bool = True
    detect_license_plate: bool = True
    face_blur_strength: int = 25
    plate_blur_strength: int = 20


class S3FolderRequest(BaseModel):
    credentials: S3Credentials
    input_s3_folder: str
    output_s3_folder: str
    detect_face: bool = True
    detect_license_plate: bool = True
    face_blur_strength: int = 25
    plate_blur_strength: int = 20
    max_workers: Optional[int] = 4


class S3ImageResult(BaseModel):
    success: bool
    input_s3_path: str
    output_s3_path: Optional[str] = None
    output_s3_url: Optional[str] = None
    original_filename: Optional[str] = None
    faces_detected: int = 0
    license_plates_detected: int = 0
    processing_time_seconds: float = 0.0
    error: Optional[str] = None


class S3SingleImageResponse(BaseModel):
    success: bool
    message: str
    result: Optional[S3ImageResult] = None
    processing_time_seconds: float


class S3FolderResponse(BaseModel):
    success: bool
    message: str
    input_folder: str
    output_folder: str
    total_images: int
    successful_count: int
    failed_count: int
    results: List[S3ImageResult]
    total_processing_time_seconds: float
    average_time_per_image: float


class S3ViewRequest(BaseModel):
    credentials: S3Credentials
    s3_uri: str
    expiration: int = 300


class S3ViewResponse(BaseModel):
    success: bool
    presigned_url: Optional[str] = None
    error: Optional[str] = None
    s3_uri: str
    expiration: int


def _get_state(request: Request):
    detector: UnifiedDetector = request.app.state.detector
    visualizer: DetectionVisualizer = request.app.state.visualizer
    s3_service: S3ProcessingService = request.app.state.s3_service
    settings: Settings = request.app.state.settings
    return detector, visualizer, s3_service, settings


def _ensure_dirs(settings: Settings) -> None:
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)


def _save_upload(settings: Settings, file_content: bytes, filename: str) -> Path:
    _ensure_dirs(settings)
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"
    file_path = Path(settings.uploads_dir) / unique_filename
    file_path.write_bytes(file_content)
    return file_path


def _validate_image(image_path: Path) -> bool:
    try:
        image = cv2.imread(str(image_path))
        return image is not None
    except Exception:
        return False


def _to_bounding_boxes(results: Dict[str, Any]) -> List[BoundingBox]:
    detections: List[BoundingBox] = []
    for face in results.get("faces", []):
        bbox = face["bbox"] if isinstance(face, dict) else face[:4]
        if isinstance(face, dict):
            confidence = face.get("confidence", 0.0)
        else:
            confidence = float(face[4]) if len(face) > 4 else 0.0
        detections.append(
            BoundingBox(
                x1=int(bbox[0]),
                y1=int(bbox[1]),
                x2=int(bbox[2]),
                y2=int(bbox[3]),
                confidence=float(confidence),
                label="face",
            )
        )
    for plate in results.get("license_plates", []):
        bbox = plate["bbox"] if isinstance(plate, dict) else plate[:4]
        if isinstance(plate, dict):
            confidence = plate.get("confidence", 0.0)
        else:
            confidence = float(plate[4]) if len(plate) > 4 else 0.0
        detections.append(
            BoundingBox(
                x1=int(bbox[0]),
                y1=int(bbox[1]),
                x2=int(bbox[2]),
                y2=int(bbox[3]),
                confidence=float(confidence),
                label="license_plate",
            )
        )
    return detections


@router.get("/")
async def root():
    return {
        "message": "Unified Detection API",
        "version": "1.0.0",
        "endpoints": {
            "detect": "/detect - POST - Detect objects in image",
            "blur": "/blur - POST - Blur detected objects in image",
            "health": "/health - GET - Health check",
        },
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


@router.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    request: Request,
    file: UploadFile = File(..., description="Image file to process"),
    detect_face: bool = Form(True, description="Whether to detect faces"),
    detect_license_plate: bool = Form(True, description="Whether to detect license plates"),
):
    detector, _, _, settings = _get_state(request)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    start_time = time.time()
    file_content = await file.read()
    image_path = _save_upload(settings, file_content, file.filename)

    try:
        if not _validate_image(image_path):
            image_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = detector.detect_objects(
            image=str(image_path),
            detect_face=detect_face,
            detect_lp=detect_license_plate,
        )
        detections = _to_bounding_boxes(results)
        processing_time = (time.time() - start_time) * 1000
        return DetectionResponse(
            success=True,
            message=f"Successfully detected {len(detections)} objects",
            detections=detections,
            total_faces=len([d for d in detections if d.label == "face"]),
            total_license_plates=len([d for d in detections if d.label == "license_plate"]),
            processing_time_ms=round(processing_time, 2),
        )
    finally:
        image_path.unlink(missing_ok=True)


@router.post("/blur", response_model=BlurResponse)
async def blur_objects(
    request: Request,
    file: UploadFile = File(..., description="Image file to process"),
    detect_face: bool = Form(True, description="Whether to detect and blur faces"),
    detect_license_plate: bool = Form(True, description="Whether to detect and blur license plates"),
    face_blur_strength: int = Form(15, description="Blur strength for faces (oval blur)"),
    plate_blur_strength: int = Form(15, description="Blur strength for license plates (rectangular blur)"),
):
    detector, visualizer, _, settings = _get_state(request)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    if face_blur_strength < 1 or face_blur_strength > 100:
        raise HTTPException(status_code=400, detail="Face blur strength must be between 1 and 100")
    if plate_blur_strength < 1 or plate_blur_strength > 100:
        raise HTTPException(status_code=400, detail="Plate blur strength must be between 1 and 100")

    start_time = time.time()
    file_content = await file.read()
    image_path = _save_upload(settings, file_content, file.filename)

    try:
        if not _validate_image(image_path):
            image_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = detector.detect_objects(
            image=str(image_path),
            detect_face=detect_face,
            detect_lp=detect_license_plate,
        )
        image = cv2.imread(str(image_path))
        blurred = visualizer.blur_detections(
            image,
            results,
            face_blur_strength=face_blur_strength,
            plate_blur_strength=plate_blur_strength,
        )

        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"{Path(image_path).stem}_blurred.jpg"
        output_path = output_dir / output_filename
        cv2.imwrite(str(output_path), blurred)

        total_detections = len(results.get("faces", [])) + len(results.get("license_plates", []))
        processing_time = (time.time() - start_time) * 1000

        return BlurResponse(
            success=True,
            message=f"Successfully blurred {total_detections} objects",
            blurred_image_path=str(output_path),
            detections_applied=total_detections,
            processing_time_ms=round(processing_time, 2),
        )
    finally:
        image_path.unlink(missing_ok=True)


@router.get("/download/")
async def download_root(request: Request):
    _, _, _, settings = _get_state(request)
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    available_files = []
    for file_path in output_dir.glob("*.jpg"):
        available_files.append(
            {
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "created_at": file_path.stat().st_ctime,
            }
        )
    return {
        "message": "Download endpoint requires a filename. Use /download/{filename}",
        "available_files": available_files,
        "total_count": len(available_files),
        "example": f"/download/{available_files[0]['filename']}" if available_files else "No files available",
    }


@router.get("/download/{filename}")
async def download_file(request: Request, filename: str):
    _, _, _, settings = _get_state(request)
    output_dir = Path(settings.output_dir)
    file_path = output_dir / filename
    if not file_path.exists():
        available_files = [f.name for f in output_dir.glob("*.jpg")]
        raise HTTPException(
            status_code=404,
            detail=(
                f"File '{filename}' not found. Available files: {available_files[:5]}"
                f"{'...' if len(available_files) > 5 else ''}"
            ),
        )
    return FileResponse(path=str(file_path), filename=filename, media_type="image/jpeg")


@router.get("/outputs")
async def list_output_files(request: Request):
    _, _, _, settings = _get_state(request)
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []
    for file_path in output_dir.glob("*.jpg"):
        output_files.append(
            {
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "created_at": file_path.stat().st_ctime,
            }
        )
    return {"files": output_files, "total_count": len(output_files)}


@router.post("/process-parallel")
async def process_images_parallel(
    request: Request,
    files: List[UploadFile] = File(..., description="Image files to process"),
    detect_face: bool = Form(True, description="Whether to detect faces"),
    detect_license_plate: bool = Form(True, description="Whether to detect license plates"),
    enable_blur: bool = Form(False, description="Whether to apply blur"),
    face_blur_strength: int = Form(25, description="Blur strength for faces"),
    plate_blur_strength: int = Form(20, description="Blur strength for license plates"),
    max_workers: int = Form(4, description="Maximum number of parallel workers"),
):
    detector, visualizer, _, settings = _get_state(request)
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    max_workers = min(int(max_workers), 8)

    async def _read_file(file: UploadFile) -> Dict[str, Any]:
        content = await file.read()
        return {"content": content, "filename": file.filename}

    file_data_list: List[Dict[str, Any]] = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            continue
        file_data_list.append(await _read_file(file))

    if not file_data_list:
        raise HTTPException(status_code=400, detail="No valid image files provided")

    start_time = time.time()

    def _process_one(file_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            img_array = np.frombuffer(file_data["content"], dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Failed to decode image")

            detection_results = detector.detect_objects(
                image=image,
                detect_face=detect_face,
                detect_lp=detect_license_plate,
            )
            detection_data = {
                "success": True,
                "message": f"Successfully detected {len(detection_results.get('faces', [])) + len(detection_results.get('license_plates', []))} objects",
                "detections": _to_bounding_boxes(detection_results),
                "total_faces": len(detection_results.get("faces", [])),
                "total_license_plates": len(detection_results.get("license_plates", [])),
                "processing_time_ms": 0.0,
            }

            blur_data = None
            if enable_blur:
                blurred = visualizer.blur_detections(
                    image,
                    detection_results,
                    face_blur_strength=face_blur_strength,
                    plate_blur_strength=plate_blur_strength,
                )
                output_dir = Path(settings.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_filename = f"{Path(file_data['filename']).stem}_{int(time.time())}_blurred.jpg"
                output_path = output_dir / output_filename
                cv2.imwrite(str(output_path), blurred)
                blur_data = {
                    "success": True,
                    "message": "Blurred successfully",
                    "blurred_image_path": str(output_path),
                    "detections_applied": len(detection_results.get("faces", [])) + len(detection_results.get("license_plates", [])),
                    "processing_time_ms": 0.0,
                }

            return {
                "success": True,
                "filename": file_data["filename"],
                "detection": detection_data,
                "blur": blur_data,
                "processing_time": 0.0,
            }
        except Exception as exc:
            return {
                "success": False,
                "filename": file_data.get("filename", ""),
                "error": str(exc),
                "processing_time": 0.0,
            }

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(_process_one, file_data_list):
            results.append(result)

    successful_results = [r for r in results if r.get("success")]
    failed_results = [r for r in results if not r.get("success")]
    total_time = (time.time() - start_time) * 1000

    return {
        "success": True,
        "message": f"Parallel processing completed: {len(successful_results)} successful, {len(failed_results)} failed",
        "total_images": len(file_data_list),
        "successful_count": len(successful_results),
        "failed_count": len(failed_results),
        "results": successful_results,
        "failed_results": failed_results,
        "total_processing_time_ms": total_time,
        "average_time_per_image_ms": total_time / len(file_data_list) if file_data_list else 0,
        "parallel_efficiency": 0.0,
    }


@router.post("/s3/process-single", response_model=S3SingleImageResponse)
async def process_s3_single_image(request: Request, payload: S3SingleImageRequest):
    _, _, s3_service, _ = _get_state(request)
    result = s3_service.process_single_image(payload.dict())
    if result["success"] and result.get("result"):
        res = result["result"]
        s3_result = S3ImageResult(
            success=res.get("success", False),
            input_s3_path=res.get("input_s3_path", ""),
            output_s3_path=res.get("output_s3_path"),
            output_s3_url=res.get("output_s3_url"),
            original_filename=res.get("original_filename"),
            faces_detected=res.get("faces_detected", 0),
            license_plates_detected=res.get("license_plates_detected", 0),
            processing_time_seconds=res.get("processing_time_seconds", 0.0),
            error=res.get("error"),
        )
        return S3SingleImageResponse(
            success=True,
            message=result["message"],
            result=s3_result,
            processing_time_seconds=result["processing_time_seconds"],
        )

    return S3SingleImageResponse(
        success=False,
        message=result.get("message", "Failed"),
        result=None,
        processing_time_seconds=result.get("processing_time_seconds", 0.0),
    )


@router.post("/s3/process-folder", response_model=S3FolderResponse)
async def process_s3_folder(request: Request, payload: S3FolderRequest):
    _, _, s3_service, _ = _get_state(request)
    result = s3_service.process_folder(payload.dict())
    results: List[S3ImageResult] = [
        S3ImageResult(
            success=img.get("success", False),
            input_s3_path=img.get("input_s3_path", ""),
            output_s3_path=img.get("output_s3_path"),
            output_s3_url=img.get("output_s3_url"),
            original_filename=img.get("original_filename"),
            faces_detected=img.get("faces_detected", 0),
            license_plates_detected=img.get("license_plates_detected", 0),
            processing_time_seconds=img.get("processing_time_seconds", 0.0),
            error=img.get("error"),
        )
        for img in result.get("results", [])
    ]
    return S3FolderResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        input_folder=result.get("input_folder", payload.input_s3_folder),
        output_folder=result.get("output_folder", payload.output_s3_folder),
        total_images=result.get("total_images", 0),
        successful_count=result.get("successful_count", 0),
        failed_count=result.get("failed_count", 0),
        results=results,
        total_processing_time_seconds=result.get("total_processing_time_seconds", 0.0),
        average_time_per_image=result.get("average_time_per_image", 0.0),
    )


@router.post("/s3/process-folder-parallel", response_model=S3FolderResponse)
async def process_s3_folder_parallel(request: Request, payload: S3FolderRequest):
    _, _, s3_service, _ = _get_state(request)
    result = s3_service.process_folder_parallel(payload.dict())
    results: List[S3ImageResult] = [
        S3ImageResult(
            success=img.get("success", False),
            input_s3_path=img.get("input_s3_path", ""),
            output_s3_path=img.get("output_s3_path"),
            output_s3_url=img.get("output_s3_url"),
            original_filename=img.get("original_filename"),
            faces_detected=img.get("faces_detected", 0),
            license_plates_detected=img.get("license_plates_detected", 0),
            processing_time_seconds=img.get("processing_time_seconds", 0.0),
            error=img.get("error"),
        )
        for img in result.get("results", [])
    ]
    return S3FolderResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        input_folder=result.get("input_folder", payload.input_s3_folder),
        output_folder=result.get("output_folder", payload.output_s3_folder),
        total_images=result.get("total_images", 0),
        successful_count=result.get("successful_count", 0),
        failed_count=result.get("failed_count", 0),
        results=results,
        total_processing_time_seconds=result.get("total_processing_time_seconds", 0.0),
        average_time_per_image=result.get("average_time_per_image", 0.0),
    )


@router.post("/s3/list-folder")
async def list_s3_folder(request: Request, payload: Dict[str, Any]):
    _, _, s3_service, _ = _get_state(request)
    credentials = payload["credentials"]
    s3_folder_path = payload["s3_folder_path"]

    processor = s3_service._get_processor(credentials)
    image_paths = processor._list_images_in_s3_folder(s3_folder_path)

    files = []
    for s3_path in image_paths:
        bucket_name, key = processor._parse_s3_path(s3_path)
        filename = key.split('/')[-1]
        files.append({"filename": filename, "s3_path": s3_path, "key": key})

    return {
        "success": True,
        "folder_path": s3_folder_path,
        "files": files,
        "total_count": len(files),
    }


@router.post("/s3/view-image", response_model=S3ViewResponse)
async def view_s3_image(request: Request, payload: S3ViewRequest):
    _, _, _, settings = _get_state(request)

    import boto3
    from botocore.exceptions import ClientError
    from boto3.session import Config

    try:
        parsed_uri = urlparse(payload.s3_uri)
        bucket_name = parsed_uri.netloc
        object_key = parsed_uri.path.lstrip('/')

        if not bucket_name or not object_key:
            return S3ViewResponse(
                success=False,
                error="Invalid S3 URI format. Use: s3://bucket-name/key",
                s3_uri=payload.s3_uri,
                expiration=payload.expiration,
            )

        s3_client = boto3.client(
            's3',
            aws_access_key_id=payload.credentials.aws_access_key_id,
            aws_secret_access_key=payload.credentials.aws_secret_access_key,
            aws_session_token=payload.credentials.aws_session_token,
            region_name=settings.s3_region,
            config=Config(s3={'addressing_style': 'virtual'}),
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ResponseContentType': 'image/jpeg',
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=payload.expiration,
        )

        return S3ViewResponse(
            success=True,
            presigned_url=presigned_url,
            s3_uri=payload.s3_uri,
            expiration=payload.expiration,
        )

    except ClientError as exc:
        error_code = exc.response['Error']['Code']
        error_message = exc.response['Error']['Message']
        return S3ViewResponse(
            success=False,
            error=f"AWS Error: {error_code} - {error_message}",
            s3_uri=payload.s3_uri,
            expiration=payload.expiration,
        )
    except Exception as exc:
        return S3ViewResponse(
            success=False,
            error=f"Error generating presigned URL: {exc}",
            s3_uri=payload.s3_uri,
            expiration=payload.expiration,
        )


@router.get("/s3/test-credentials")
async def test_s3_credentials(
    request: Request,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: Optional[str] = None,
):
    _, _, s3_service, _ = _get_state(request)
    try:
        processor = s3_service._get_processor(
            {
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "aws_session_token": aws_session_token,
            }
        )
        # simple call to verify
        processor.s3_client.list_buckets()
        return {"success": True, "message": "S3 credentials are valid and connection established"}
    except Exception as exc:
        return {"success": False, "message": f"S3 credentials test failed: {exc}"}
