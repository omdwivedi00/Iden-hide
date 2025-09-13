"""
FastAPI Server for Unified Detection System
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional, Dict, Any
import os
from pathlib import Path

from models import (
    DetectionResponse, BlurRequest, BlurResponse, ErrorResponse,
    S3SingleImageRequest, S3SingleImageResponse,
    S3FolderRequest, S3FolderResponse, S3ViewRequest, S3ViewResponse
)
from detection_service import DetectionService
from s3_service import S3ProcessingService
from urllib.parse import urlparse

# Initialize FastAPI app
app = FastAPI(
    title="Unified Detection API",
    description="API for face and license plate detection with blur functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
detection_service = DetectionService()
s3_service = S3ProcessingService()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified Detection API",
        "version": "1.0.0",
        "endpoints": {
            "detect": "/detect - POST - Detect objects in image",
            "blur": "/blur - POST - Blur detected objects in image",
            "health": "/health - GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    file: UploadFile = File(..., description="Image file to process"),
    detect_face: bool = Form(True, description="Whether to detect faces"),
    detect_license_plate: bool = Form(True, description="Whether to detect license plates")
):
    """Detect faces and/or license plates in an uploaded image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file
        image_path = detection_service.save_uploaded_file(file_content, file.filename)
        
        # Validate image
        if not detection_service.validate_image(image_path):
            os.remove(image_path)  # Clean up invalid file
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Perform detection
        result = detection_service.detect_objects_in_image(
            image_path=image_path,
            detect_face=detect_face,
            detect_license_plate=detect_license_plate
        )
        
        # Clean up uploaded file
        os.remove(image_path)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/blur", response_model=BlurResponse)
async def blur_objects(
    file: UploadFile = File(..., description="Image file to process"),
    detect_face: bool = Form(True, description="Whether to detect and blur faces"),
    detect_license_plate: bool = Form(True, description="Whether to detect and blur license plates"),
    face_blur_strength: int = Form(15, description="Blur strength for faces (oval blur)"),
    plate_blur_strength: int = Form(15, description="Blur strength for license plates (rectangular blur)")
):
    """Blur detected faces and/or license plates in an uploaded image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate blur strength parameters
        if face_blur_strength < 1 or face_blur_strength > 100:
            raise HTTPException(status_code=400, detail="Face blur strength must be between 1 and 100")
        if plate_blur_strength < 1 or plate_blur_strength > 100:
            raise HTTPException(status_code=400, detail="Plate blur strength must be between 1 and 100")
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file
        image_path = detection_service.save_uploaded_file(file_content, file.filename)
        
        # Validate image
        if not detection_service.validate_image(image_path):
            os.remove(image_path)  # Clean up invalid file
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Perform blur operation
        result = detection_service.blur_objects_in_image(
            image_path=image_path,
            detect_face=detect_face,
            detect_license_plate=detect_license_plate,
            face_blur_strength=face_blur_strength,
            plate_blur_strength=plate_blur_strength
        )
        
        # Clean up uploaded file
        os.remove(image_path)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/download/")
async def download_root():
    """List available files for download"""
    available_files = []
    for file_path in detection_service.output_dir.glob("*.jpg"):
        available_files.append({
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "created_at": file_path.stat().st_ctime
        })
    
    return {
        "message": "Download endpoint requires a filename. Use /download/{filename}",
        "available_files": available_files,
        "total_count": len(available_files),
        "example": f"/download/{available_files[0]['filename']}" if available_files else "No files available"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a processed image file"""
    file_path = detection_service.output_dir / filename
    
    if not file_path.exists():
        # List available files for debugging
        available_files = [f.name for f in detection_service.output_dir.glob("*.jpg")]
        raise HTTPException(
            status_code=404, 
            detail=f"File '{filename}' not found. Available files: {available_files[:5]}{'...' if len(available_files) > 5 else ''}"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='image/jpeg'
    )

@app.get("/outputs")
async def list_output_files():
    """List all available output files"""
    output_files = []
    for file_path in detection_service.output_dir.glob("*.jpg"):
        output_files.append({
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "created_at": file_path.stat().st_ctime
        })
    
    return {
        "files": output_files,
        "total_count": len(output_files)
    }

# S3 Processing Endpoints
@app.post("/s3/process-single", response_model=S3SingleImageResponse)
async def process_s3_single_image(request: S3SingleImageRequest):
    """
    Process a single image from S3
    
    - **credentials**: AWS S3 credentials
    - **input_s3_path**: S3 path to input image (e.g., s3://bucket/path/image.jpg)
    - **output_s3_path**: S3 path for output image (e.g., s3://bucket/path/blurred_image.jpg)
    - **detect_face**: Whether to detect faces (default: True)
    - **detect_license_plate**: Whether to detect license plates (default: True)
    - **face_blur_strength**: Blur strength for faces (default: 25)
    - **plate_blur_strength**: Blur strength for license plates (default: 20)
    """
    try:
        result = s3_service.process_single_image(request.dict())
        return result
    except Exception as e:
        return S3SingleImageResponse(
            success=False,
            message=f"API error: {str(e)}",
            result=None,
            processing_time_seconds=0.0
        )

@app.post("/s3/process-folder", response_model=S3FolderResponse)
async def process_s3_folder(request: S3FolderRequest):
    """
    Process all images in an S3 folder
    
    - **credentials**: AWS S3 credentials
    - **input_s3_folder**: S3 folder path containing input images (e.g., s3://bucket/input/)
    - **output_s3_folder**: S3 folder path for output images (e.g., s3://bucket/output/)
    - **detect_face**: Whether to detect faces (default: True)
    - **detect_license_plate**: Whether to detect license plates (default: True)
    - **face_blur_strength**: Blur strength for faces (default: 25)
    - **plate_blur_strength**: Blur strength for license plates (default: 20)
    """
    try:
        result = s3_service.process_folder(request.dict())
        return result
    except Exception as e:
        return S3FolderResponse(
            success=False,
            message=f"API error: {str(e)}",
            input_folder=request.input_s3_folder,
            output_folder=request.output_s3_folder,
            total_images=0,
            successful_count=0,
            failed_count=0,
            results=[],
            total_processing_time_seconds=0.0,
            average_time_per_image=0.0
        )

@app.post("/s3/list-folder")
async def list_s3_folder(request: Dict[str, Any]):
    """
    List files in an S3 folder
    
    - **credentials**: AWS S3 credentials
    - **s3_folder_path**: S3 folder path (e.g., s3://bucket/folder/)
    """
    try:
        credentials = request['credentials']
        s3_folder_path = request['s3_folder_path']
        
        from s3_processor import S3ImageProcessor
        
        processor = S3ImageProcessor(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            aws_session_token=credentials.get('aws_session_token')
        )
        
        # List images in folder
        image_paths = processor._list_images_in_s3_folder(s3_folder_path)
        
        # Extract file information
        files = []
        for s3_path in image_paths:
            bucket_name, key = processor._parse_s3_path(s3_path)
            filename = key.split('/')[-1]
            files.append({
                'filename': filename,
                's3_path': s3_path,
                'key': key
            })
        
        return {
            "success": True,
            "folder_path": s3_folder_path,
            "files": files,
            "total_count": len(files)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_path": request.get('s3_folder_path', ''),
            "files": [],
            "total_count": 0
        }

@app.post("/s3/view-image", response_model=S3ViewResponse)
async def view_s3_image(request: S3ViewRequest):
    """
    Generate presigned URL for viewing S3 image
    
    - **credentials**: AWS S3 credentials
    - **s3_uri**: S3 URI of the image (e.g., s3://bucket/path/image.jpg)
    - **expiration**: URL expiration time in seconds (default: 300)
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Parse S3 URI to extract bucket and key
        parsed_uri = urlparse(request.s3_uri)
        bucket_name = parsed_uri.netloc
        object_key = parsed_uri.path.lstrip('/')
        
        if not bucket_name or not object_key:
            return S3ViewResponse(
                success=False,
                error="Invalid S3 URI format. Use: s3://bucket-name/key",
                s3_uri=request.s3_uri,
                expiration=request.expiration
            )
        
        # Create S3 client with provided credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=request.credentials.aws_access_key_id,
            aws_secret_access_key=request.credentials.aws_secret_access_key,
            aws_session_token=request.credentials.aws_session_token,
            region_name='ap-south-1'  # Default region
        )
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name, 
                'Key': object_key,
                'ResponseContentType': 'image/jpeg',  # Force image content type
                'ResponseContentDisposition': 'inline'  # Display inline in browser
            },
            ExpiresIn=request.expiration
        )
        
        return S3ViewResponse(
            success=True,
            presigned_url=presigned_url,
            s3_uri=request.s3_uri,
            expiration=request.expiration
        )
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return S3ViewResponse(
            success=False,
            error=f"AWS Error: {error_code} - {error_message}",
            s3_uri=request.s3_uri,
            expiration=request.expiration
        )
    except Exception as e:
        return S3ViewResponse(
            success=False,
            error=f"Error generating presigned URL: {str(e)}",
            s3_uri=request.s3_uri,
            expiration=request.expiration
        )

@app.get("/s3/test-credentials")
async def test_s3_credentials(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: Optional[str] = None
):
    """
    Test S3 credentials without processing any images
    
    - **aws_access_key_id**: AWS access key ID
    - **aws_secret_access_key**: AWS secret access key
    - **aws_session_token**: Optional AWS session token
    """
    try:
        from s3_processor import S3ImageProcessor
        
        processor = S3ImageProcessor(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        
        return {
            "success": True,
            "message": "S3 credentials are valid and connection established"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"S3 credentials test failed: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
