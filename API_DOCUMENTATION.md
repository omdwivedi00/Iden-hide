# Iden-Hide AI Anonymization Engine - API Documentation

## ⚠️ Security Notice

**This is a rapid development prototype built in 24 hours for a hackathon. Security has not been implemented as the primary focus was on core functionality and AI detection capabilities. The next critical step is implementing comprehensive security measures including:**

- Authentication and authorization
- Input validation and sanitization
- Rate limiting and DDoS protection
- Data encryption at rest and in transit
- Secure credential management
- API key validation
- Request logging and monitoring

**Do not use this in production without implementing proper security measures.**

## Overview

The Iden-Hide API provides comprehensive AI-powered anonymization services for detecting and blurring faces and license plates in images. The API supports single image processing, batch folder processing, and cloud-based S3 processing.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Content-Type**: `application/json`  
**Authentication**: None (Future: JWT Bearer Token)

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)
7. [SDK Examples](#sdk-examples)

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

```http
# Future Authentication Header
Authorization: Bearer <jwt_token>
```

## Endpoints

### Health Check

#### GET /health

Check API health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "face_detection": "operational",
    "license_plate_detection": "operational",
    "blur_engine": "operational"
  }
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is down

---

### Single Image Detection

#### POST /detect

Process a single image for face and license plate detection with optional privacy blur.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "detect_faces": true,
  "detect_license_plates": true,
  "enable_blur": false,
  "face_blur_strength": 25,
  "plate_blur_strength": 20,
  "return_original": true,
  "return_blurred": false
}
```

**Parameters:**
- `image` (string, required): Base64 encoded image data
- `detect_faces` (boolean, optional): Enable face detection (default: true)
- `detect_license_plates` (boolean, optional): Enable license plate detection (default: true)
- `enable_blur` (boolean, optional): Apply privacy blur (default: false)
- `face_blur_strength` (integer, optional): Blur strength for faces (1-100, default: 25)
- `plate_blur_strength` (integer, optional): Blur strength for plates (1-100, default: 20)
- `return_original` (boolean, optional): Include original image in response (default: true)
- `return_blurred` (boolean, optional): Include blurred image in response (default: false)

**Response:**
```json
{
  "success": true,
  "processing_time_ms": 2340,
  "detection_results": {
    "total_faces": 2,
    "total_license_plates": 1,
    "detections": [
      {
        "label": "face",
        "confidence": 0.95,
        "bbox": [100, 150, 200, 250],
        "blurred": true
      },
      {
        "label": "license_plate",
        "confidence": 0.87,
        "bbox": [300, 400, 450, 430],
        "blurred": true
      }
    ]
  },
  "images": {
    "original": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "blurred": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  },
  "metadata": {
    "image_size": [1920, 1080],
    "file_format": "JPEG",
    "file_size_bytes": 245760
  }
}
```

**Status Codes:**
- `200 OK`: Detection successful
- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Invalid image format
- `500 Internal Server Error`: Processing failed

---

### Batch Folder Processing

#### POST /process-folder

Process multiple images from a folder with parallel processing support.

**Request Body:**
```json
{
  "images": [
    {
      "filename": "image1.jpg",
      "data": "base64_encoded_image_string"
    },
    {
      "filename": "image2.png", 
      "data": "base64_encoded_image_string"
    }
  ],
  "detect_faces": true,
  "detect_license_plates": true,
  "enable_blur": true,
  "face_blur_strength": 25,
  "plate_blur_strength": 20,
  "use_parallel_processing": true,
  "max_workers": 4
}
```

**Parameters:**
- `images` (array, required): Array of image objects with filename and base64 data
- `detect_faces` (boolean, optional): Enable face detection (default: true)
- `detect_license_plates` (boolean, optional): Enable license plate detection (default: true)
- `enable_blur` (boolean, optional): Apply privacy blur (default: false)
- `face_blur_strength` (integer, optional): Blur strength for faces (1-100, default: 25)
- `plate_blur_strength` (integer, optional): Blur strength for plates (1-100, default: 20)
- `use_parallel_processing` (boolean, optional): Enable parallel processing (default: true)
- `max_workers` (integer, optional): Maximum number of worker processes (default: 4)

**Response:**
```json
{
  "success": true,
  "total_images": 2,
  "processed_images": 2,
  "failed_images": 0,
  "total_processing_time_ms": 4560,
  "results": [
    {
      "filename": "image1.jpg",
      "success": true,
      "processing_time_ms": 2100,
      "detection_results": {
        "total_faces": 1,
        "total_license_plates": 0,
        "detections": [
          {
            "label": "face",
            "confidence": 0.92,
            "bbox": [150, 200, 250, 300],
            "blurred": true
          }
        ]
      },
      "images": {
        "original": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
        "blurred": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      }
    },
    {
      "filename": "image2.png",
      "success": true,
      "processing_time_ms": 2460,
      "detection_results": {
        "total_faces": 0,
        "total_license_plates": 1,
        "detections": [
          {
            "label": "license_plate",
            "confidence": 0.89,
            "bbox": [400, 500, 550, 530],
            "blurred": true
          }
        ]
      },
      "images": {
        "original": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "blurred": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
      }
    }
  ],
  "summary": {
    "total_faces_detected": 1,
    "total_plates_detected": 1,
    "average_processing_time_ms": 2280
  }
}
```

**Status Codes:**
- `200 OK`: Batch processing completed
- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Invalid image format(s)
- `500 Internal Server Error`: Processing failed

---

### S3 Cloud Processing

#### POST /process-s3

Process images from AWS S3 with cloud storage integration.

**Request Body:**
```json
{
  "s3_config": {
    "bucket_name": "my-images-bucket",
    "prefix": "input-images/",
    "region": "us-west-2"
  },
  "credentials": {
    "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
    "aws_session_token": "YOUR_AWS_SESSION_TOKEN_IF_APPLICABLE"
  },
  "detect_faces": true,
  "detect_license_plates": true,
  "enable_blur": true,
  "face_blur_strength": 25,
  "plate_blur_strength": 20,
  "use_parallel_processing": true,
  "max_workers": 4,
  "output_prefix": "processed-images/"
}
```

**Parameters:**
- `s3_config` (object, required): S3 configuration
  - `bucket_name` (string): S3 bucket name
  - `prefix` (string): S3 object prefix/folder
  - `region` (string): AWS region
- `credentials` (object, required): AWS credentials
  - `aws_access_key_id` (string): AWS access key
  - `aws_secret_access_key` (string): AWS secret key
  - `aws_session_token` (string, optional): Session token for temporary credentials
- `detect_faces` (boolean, optional): Enable face detection (default: true)
- `detect_license_plates` (boolean, optional): Enable license plate detection (default: true)
- `enable_blur` (boolean, optional): Apply privacy blur (default: false)
- `face_blur_strength` (integer, optional): Blur strength for faces (1-100, default: 25)
- `plate_blur_strength` (integer, optional): Blur strength for plates (1-100, default: 20)
- `use_parallel_processing` (boolean, optional): Enable parallel processing (default: true)
- `max_workers` (integer, optional): Maximum number of worker processes (default: 4)
- `output_prefix` (string, optional): S3 prefix for processed images (default: "processed/")

**Response:**
```json
{
  "success": true,
  "total_images": 5,
  "processed_images": 5,
  "failed_images": 0,
  "total_processing_time_ms": 12340,
  "s3_results": {
    "processed_objects": [
      {
        "original_key": "input-images/photo1.jpg",
        "processed_key": "processed-images/photo1_processed.jpg",
        "detection_results": {
          "total_faces": 2,
          "total_license_plates": 1,
          "detections": [
            {
              "label": "face",
              "confidence": 0.94,
              "bbox": [100, 150, 200, 250],
              "blurred": true
            }
          ]
        },
        "s3_urls": {
          "original": "https://my-images-bucket.s3.us-west-2.amazonaws.com/input-images/photo1.jpg",
          "processed": "https://my-images-bucket.s3.us-west-2.amazonaws.com/processed-images/photo1_processed.jpg"
        }
      }
    ],
    "summary": {
      "total_faces_detected": 8,
      "total_plates_detected": 3,
      "average_processing_time_ms": 2468
    }
  }
}
```

**Status Codes:**
- `200 OK`: S3 processing completed
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid AWS credentials
- `403 Forbidden`: Insufficient S3 permissions
- `404 Not Found`: S3 bucket or objects not found
- `500 Internal Server Error`: Processing failed

---

### View S3 Image

#### POST /view-s3-image

Generate presigned URLs for viewing S3 images.

**Request Body:**
```json
{
  "s3_key": "processed-images/photo1_processed.jpg",
  "bucket_name": "my-images-bucket",
  "credentials": {
    "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
    "aws_session_token": "YOUR_AWS_SESSION_TOKEN_IF_APPLICABLE"
  },
  "expires_in": 3600
}
```

**Parameters:**
- `s3_key` (string, required): S3 object key
- `bucket_name` (string, required): S3 bucket name
- `credentials` (object, required): AWS credentials
- `expires_in` (integer, optional): URL expiration time in seconds (default: 3600)

**Response:**
```json
{
  "success": true,
  "presigned_url": "https://my-images-bucket.s3.us-west-2.amazonaws.com/processed-images/photo1_processed.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
  "expires_at": "2024-01-15T11:30:00Z",
  "metadata": {
    "content_type": "image/jpeg",
    "content_length": 245760,
    "last_modified": "2024-01-15T10:30:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Presigned URL generated
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid AWS credentials
- `404 Not Found`: S3 object not found
- `500 Internal Server Error`: URL generation failed

## Data Models

### Detection Object

```json
{
  "label": "face|license_plate",
  "confidence": 0.95,
  "bbox": [x1, y1, x2, y2],
  "blurred": true
}
```

**Fields:**
- `label` (string): Type of detection ("face" or "license_plate")
- `confidence` (float): Detection confidence score (0.0-1.0)
- `bbox` (array): Bounding box coordinates [x1, y1, x2, y2]
- `blurred` (boolean): Whether the detection was blurred

### Detection Results

```json
{
  "total_faces": 2,
  "total_license_plates": 1,
  "detections": [
    {
      "label": "face",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 250],
      "blurred": true
    }
  ]
}
```

### Image Object

```json
{
  "filename": "image.jpg",
  "data": "base64_encoded_image_string"
}
```

### S3 Configuration

```json
{
  "bucket_name": "my-images-bucket",
  "prefix": "input-images/",
  "region": "us-west-2"
}
```

### AWS Credentials

```json
{
  "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
  "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
  "aws_session_token": "YOUR_AWS_SESSION_TOKEN_IF_APPLICABLE"
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE_FORMAT",
    "message": "Unsupported image format. Supported formats: JPEG, PNG, GIF, WebP",
    "details": {
      "provided_format": "BMP",
      "supported_formats": ["JPEG", "PNG", "GIF", "WebP"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_IMAGE_FORMAT` | 422 | Unsupported image format |
| `INVALID_BASE64` | 400 | Invalid base64 encoding |
| `IMAGE_TOO_LARGE` | 413 | Image exceeds size limit |
| `PROCESSING_FAILED` | 500 | AI processing failed |
| `S3_ACCESS_DENIED` | 403 | Insufficient S3 permissions |
| `S3_BUCKET_NOT_FOUND` | 404 | S3 bucket does not exist |
| `INVALID_CREDENTIALS` | 401 | Invalid AWS credentials |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests (future) |

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will include:

- **Per IP**: 100 requests per minute
- **Per API Key**: 1000 requests per hour
- **Burst Allowance**: 20 requests per second

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Examples

### cURL Examples

#### Single Image Detection

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "detect_faces": true,
    "detect_license_plates": true,
    "enable_blur": true,
    "face_blur_strength": 25,
    "plate_blur_strength": 20
  }'
```

#### Batch Processing

```bash
curl -X POST "http://localhost:8000/process-folder" \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "filename": "photo1.jpg",
        "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      }
    ],
    "use_parallel_processing": true,
    "max_workers": 4
  }'
```

#### S3 Processing

```bash
curl -X POST "http://localhost:8000/process-s3" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_config": {
      "bucket_name": "my-images-bucket",
      "prefix": "input-images/",
      "region": "us-west-2"
    },
    "credentials": {
      "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
      "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY"
    },
    "enable_blur": true
  }'
```

## SDK Examples

### Python SDK

```python
import requests
import base64

class IdenHideClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def detect_image(self, image_path, **kwargs):
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        payload = {
            "image": f"data:image/jpeg;base64,{image_data}",
            "detect_faces": kwargs.get("detect_faces", True),
            "detect_license_plates": kwargs.get("detect_license_plates", True),
            "enable_blur": kwargs.get("enable_blur", False),
            "face_blur_strength": kwargs.get("face_blur_strength", 25),
            "plate_blur_strength": kwargs.get("plate_blur_strength", 20)
        }
        
        response = requests.post(f"{self.base_url}/detect", json=payload)
        return response.json()
    
    def process_folder(self, image_paths, **kwargs):
        images = []
        for path in image_paths:
            with open(path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            images.append({
                "filename": path.split('/')[-1],
                "data": f"data:image/jpeg;base64,{image_data}"
            })
        
        payload = {
            "images": images,
            "use_parallel_processing": kwargs.get("use_parallel_processing", True),
            "max_workers": kwargs.get("max_workers", 4)
        }
        
        response = requests.post(f"{self.base_url}/process-folder", json=payload)
        return response.json()

# Usage
client = IdenHideClient()

# Single image
result = client.detect_image("photo.jpg", enable_blur=True)
print(f"Detected {result['detection_results']['total_faces']} faces")

# Batch processing
results = client.process_folder(["photo1.jpg", "photo2.jpg"])
print(f"Processed {results['processed_images']} images")
```

### JavaScript SDK

```javascript
class IdenHideClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async detectImage(imageFile, options = {}) {
        const base64 = await this.fileToBase64(imageFile);
        
        const payload = {
            image: `data:${imageFile.type};base64,${base64}`,
            detect_faces: options.detectFaces ?? true,
            detect_license_plates: options.detectLicensePlates ?? true,
            enable_blur: options.enableBlur ?? false,
            face_blur_strength: options.faceBlurStrength ?? 25,
            plate_blur_strength: options.plateBlurStrength ?? 20
        };
        
        const response = await fetch(`${this.baseUrl}/detect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    async processFolder(imageFiles, options = {}) {
        const images = await Promise.all(
            imageFiles.map(async (file) => ({
                filename: file.name,
                data: `data:${file.type};base64,${await this.fileToBase64(file)}`
            }))
        );
        
        const payload = {
            images,
            use_parallel_processing: options.useParallelProcessing ?? true,
            max_workers: options.maxWorkers ?? 4
        };
        
        const response = await fetch(`${this.baseUrl}/process-folder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = error => reject(error);
        });
    }
}

// Usage
const client = new IdenHideClient();

// Single image
const fileInput = document.getElementById('imageInput');
const file = fileInput.files[0];
const result = await client.detectImage(file, { enableBlur: true });
console.log(`Detected ${result.detection_results.total_faces} faces`);

// Batch processing
const fileInputs = document.getElementById('imageInputs');
const files = Array.from(fileInputs.files);
const results = await client.processFolder(files);
console.log(`Processed ${results.processed_images} images`);
```

## Security Implementation Roadmap

### ⚠️ Current Security Status
**This is a rapid development prototype. Security has NOT been implemented as the primary focus was on core functionality and AI detection capabilities.**

### Critical Security Gaps
- **No Authentication**: All endpoints are publicly accessible
- **No Authorization**: No access control or user management
- **No Input Validation**: Limited request validation and sanitization
- **No Rate Limiting**: Vulnerable to DDoS attacks and abuse
- **No Encryption**: Data transmitted in plain text (HTTP only)
- **No Audit Logging**: No security event tracking
- **No API Keys**: No secure API key validation

### Next Priority: Security Implementation
1. **Authentication**: Implement JWT-based authentication
2. **Authorization**: Add role-based access control
3. **Input Validation**: Comprehensive request validation
4. **Rate Limiting**: API rate limiting and DDoS protection
5. **HTTPS**: SSL/TLS encryption for all communications
6. **Audit Logging**: Security event logging and monitoring

### Data Privacy
- Images are processed in memory and not permanently stored
- Temporary files are cleaned up after processing
- S3 credentials should be stored securely (environment variables recommended)

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Single image detection
- Batch folder processing
- S3 cloud processing
- Face and license plate detection
- Privacy blur functionality
- Parallel processing support

### Future Versions
- **v1.1.0**: Authentication and authorization
- **v1.2.0**: Rate limiting and monitoring
- **v1.3.0**: Real-time video processing
- **v2.0.0**: Advanced AI models and features

---

*This API documentation is maintained alongside the codebase and reflects the current state of the Iden-Hide AI Anonymization Engine API.*
