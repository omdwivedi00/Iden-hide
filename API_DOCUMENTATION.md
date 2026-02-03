# Unified Detection API Documentation

## Security Notice
This API currently runs without authentication. Add authn/z, rate limiting, input validation, and secrets management before production use.

## Base URL
`http://localhost:8000`

## Environment Configuration
Runtime configuration is loaded from `.env` in the repo root (see `.env.example`). You can override any setting via environment variables at run time (e.g., `DETECT_DEVICE`, `FACE_MODE`).

## Content Types
- **Upload endpoints**: `multipart/form-data`
- **JSON endpoints**: `application/json`

## Endpoints

### GET /
API info.

### GET /health
Health check.

**Response**
```json
{"status":"healthy","message":"API is running"}
```

---

### POST /detect
Detect faces and/or license plates.

**Request (multipart/form-data)**
- `file` (image file, required)
- `detect_face` (bool, default: true)
- `detect_license_plate` (bool, default: true)

**Response**
```json
{
  "success": true,
  "message": "Successfully detected 3 objects",
  "detections": [
    {"x1": 10, "y1": 20, "x2": 120, "y2": 160, "confidence": 0.91, "label": "face"}
  ],
  "total_faces": 2,
  "total_license_plates": 1,
  "processing_time_ms": 84.2
}
```

---

### POST /blur
Detect + blur faces and/or plates.

**Request (multipart/form-data)**
- `file` (image file, required)
- `detect_face` (bool, default: true)
- `detect_license_plate` (bool, default: true)
- `face_blur_strength` (int 1–100, default: 15)
- `plate_blur_strength` (int 1–100, default: 15)

**Response**
```json
{
  "success": true,
  "message": "Successfully blurred 3 objects",
  "blurred_image_path": "output/example_blurred.jpg",
  "detections_applied": 3,
  "processing_time_ms": 121.5
}
```

---

### GET /outputs
List output files.

### GET /download/{filename}
Download a processed image.

---

### POST /process-parallel
Process multiple images in parallel (local batch).

**Request (multipart/form-data)**
- `files` (multiple image files)
- `detect_face` (bool, default: true)
- `detect_license_plate` (bool, default: true)
- `enable_blur` (bool, default: false)
- `face_blur_strength` (int, default: 25)
- `plate_blur_strength` (int, default: 20)
- `max_workers` (int, default: 4; capped at 8)

**Response**
```json
{
  "success": true,
  "message": "Parallel processing completed: 10 successful, 0 failed",
  "total_images": 10,
  "successful_count": 10,
  "failed_count": 0,
  "results": [
    {
      "success": true,
      "filename": "img1.jpg",
      "detection": {"total_faces": 1, "total_license_plates": 0, "detections": []},
      "blur": null,
      "processing_time": 0.0
    }
  ],
  "failed_results": [],
  "total_processing_time_ms": 1200.0,
  "average_time_per_image_ms": 120.0,
  "parallel_efficiency": 0.0
}
```

---

## S3 Endpoints

### POST /s3/process-single
**Body (JSON)**
```json
{
  "credentials": {"aws_access_key_id": "...", "aws_secret_access_key": "...", "aws_session_token": "..."},
  "input_s3_path": "s3://bucket/input.jpg",
  "output_s3_path": "s3://bucket/output.jpg",
  "detect_face": true,
  "detect_license_plate": true,
  "face_blur_strength": 25,
  "plate_blur_strength": 20
}
```

### POST /s3/process-folder
Same as above with `input_s3_folder` + `output_s3_folder`.

### POST /s3/process-folder-parallel
Same as `/s3/process-folder` plus `max_workers`.

### POST /s3/list-folder
```json
{"credentials": {...}, "s3_folder_path": "s3://bucket/folder/"}
```

### POST /s3/view-image
```json
{"credentials": {...}, "s3_uri": "s3://bucket/key.jpg", "expiration": 300}
```

### GET /s3/test-credentials
Query params:
- `aws_access_key_id`
- `aws_secret_access_key`
- `aws_session_token` (optional)

---

## Errors
- `400` for invalid inputs (wrong file type, invalid params)
- `500` for internal errors
