"""
API Request and Response Models
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class DetectionType(str, Enum):
    """Detection type options"""
    FACE = "face"
    LICENSE_PLATE = "license_plate"
    BOTH = "both"

class BoundingBox(BaseModel):
    """Bounding box coordinates and metadata"""
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str

class DetectionResponse(BaseModel):
    """Response model for detection endpoint"""
    success: bool
    message: str
    detections: List[BoundingBox]
    total_faces: int
    total_license_plates: int
    processing_time_ms: float

class BlurRequest(BaseModel):
    """Request model for blur endpoint"""
    detect_face: bool = True
    detect_license_plate: bool = True
    face_blur_strength: int = 15
    plate_blur_strength: int = 15

class BlurResponse(BaseModel):
    """Response model for blur endpoint"""
    success: bool
    message: str
    blurred_image_path: str
    detections_applied: int
    processing_time_ms: float

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: str

# S3 Processing Models
class S3Credentials(BaseModel):
    """AWS S3 credentials"""
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: Optional[str] = None

class S3SingleImageRequest(BaseModel):
    """Request model for single S3 image processing"""
    credentials: S3Credentials
    input_s3_path: str
    output_s3_path: str
    detect_face: bool = True
    detect_license_plate: bool = True
    face_blur_strength: int = 25
    plate_blur_strength: int = 20

class S3FolderRequest(BaseModel):
    """Request model for S3 folder processing"""
    credentials: S3Credentials
    input_s3_folder: str
    output_s3_folder: str
    detect_face: bool = True
    detect_license_plate: bool = True
    face_blur_strength: int = 25
    plate_blur_strength: int = 20

class S3ImageResult(BaseModel):
    """Result for a single processed image"""
    success: bool
    input_s3_path: str
    output_s3_path: str
    output_s3_url: Optional[str] = None
    original_filename: Optional[str] = None
    faces_detected: int = 0
    license_plates_detected: int = 0
    processing_time_seconds: float = 0.0
    error: Optional[str] = None

class S3SingleImageResponse(BaseModel):
    """Response model for single S3 image processing"""
    success: bool
    message: str
    result: Optional[S3ImageResult] = None
    processing_time_seconds: float

class S3FolderResponse(BaseModel):
    """Response model for S3 folder processing"""
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
    """Request to view S3 image"""
    credentials: S3Credentials
    s3_uri: str
    expiration: int = 300  # 5 minutes default

class S3ViewResponse(BaseModel):
    """Response for S3 image view"""
    success: bool
    presigned_url: Optional[str] = None
    error: Optional[str] = None
    s3_uri: str
    expiration: int
