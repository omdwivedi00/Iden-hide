# 🚀 Unified Detection Production System - Complete Setup Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Starting the Server](#starting-the-server)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)

## 🎯 Overview

The Unified Detection Production System is a complete solution for face and license plate detection with privacy protection features. It provides:

- **Face Detection**: Using YOLO + InsightFace for accurate face detection
- **License Plate Detection**: Using YOLO with vehicle-first approach
- **Privacy Protection**: Oval blur for faces, rectangular blur for license plates
- **REST API**: FastAPI-based server with automatic documentation
- **Visual Display**: OpenCV-based visualization tools

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space for models and dependencies

### Hardware Requirements
- **CPU**: Multi-core processor (Intel/AMD)
- **GPU**: Optional but recommended for faster processing
- **Webcam**: Optional, for real-time detection

## 🔧 Installation

### Step 1: Download the System
```bash
# If you have the unified_detection_production folder
cd /path/to/unified_detection_production

# Verify the folder structure
ls -la
```

Expected structure:
```
unified_detection_production/
├── models/                    # AI model files
├── test_images/              # Sample test images
├── api_results/              # Test results
├── output/                   # Generated images
├── detect_face.py           # Face detection module
├── detect_lp.py             # License plate detection module
├── unified_detector.py      # Main detection orchestrator
├── visualizer.py            # Visualization and blur functions
├── api.py                   # Core API functions
├── models.py                # Pydantic models
├── detection_service.py     # FastAPI service layer
├── main.py                  # FastAPI server
├── test_api.py              # API test script
├── show_detections.py       # Visual detection display
├── requirements.txt         # Dependencies
└── README.md                # Basic documentation
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import cv2, ultralytics, insightface; print('✅ All dependencies installed successfully')"
```

### Step 4: Download AI Models
The system will automatically download required models on first run, but you can also download them manually:

```bash
# YOLO model (will be downloaded automatically)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O models/yolov8n.pt

# License plate detection model (if available)
# Place your trained license plate model at: models/license_plate_detector.pt
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (optional):
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Detection Parameters
FACE_CONFIDENCE=0.3
PLATE_CONFIDENCE=0.5
BLUR_STRENGTH=15

# File Paths
UPLOAD_DIR=uploads
OUTPUT_DIR=output
MODEL_DIR=models
```

### Model Configuration
Edit detection parameters in the respective files:

**Face Detection** (`detect_face.py`):
```python
# Adjust these parameters
person_conf=0.20          # Person detection confidence
face_det_thresh=0.20      # Face detection threshold
face_det_size=1280        # Face detection input size
```

**License Plate Detection** (`detect_lp.py`):
```python
# Adjust these parameters
vehicle_conf_threshold=0.3    # Vehicle detection confidence
plate_conf_threshold=0.5      # License plate detection confidence
```

## 🚀 Starting the Server

### Method 1: Direct Python Execution
```bash
# Navigate to the project directory
cd unified_detection_production

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

# Start the server
python main.py
```

### Method 2: Using Uvicorn Directly
```bash
# Start with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# For production (without reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Method 3: Background Process
```bash
# Start in background
nohup python main.py > server.log 2>&1 &

# Check if running
ps aux | grep python
```

### Server Status
Once started, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID] using StatReload
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Available Endpoints

#### 1. Health Check
- **URL**: `GET /health`
- **Description**: Check if the server is running
- **Response**: `{"status": "healthy", "message": "API is running"}`

#### 2. API Information
- **URL**: `GET /`
- **Description**: Get API information and available endpoints
- **Response**: JSON with API details

#### 3. Object Detection
- **URL**: `POST /detect`
- **Description**: Detect faces and license plates in an image
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Image file (required)
  - `detect_face`: Boolean (default: true)
  - `detect_license_plate`: Boolean (default: true)

#### 4. Privacy Blur
- **URL**: `POST /blur`
- **Description**: Blur detected faces and license plates
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Image file (required)
  - `detect_face`: Boolean (default: true)
  - `detect_license_plate`: Boolean (default: true)
  - `face_blur_strength`: Integer 1-100 (default: 15)
  - `plate_blur_strength`: Integer 1-100 (default: 15)

#### 5. List Output Files
- **URL**: `GET /outputs`
- **Description**: List all processed output files
- **Response**: JSON with file list and metadata

#### 6. Download File
- **URL**: `GET /download/{filename}`
- **Description**: Download a processed image file
- **Response**: Image file

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### 1. Basic API Test
```bash
# Run comprehensive API tests
python test_api.py

# Expected output:
# 🚀 Unified Detection API Test
# ========================================
# ✅ Health check passed
# 📸 Testing with 3 images...
# 🎉 Testing completed!
# 📊 Success rate: 6/6 (100.0%)
```

### 2. Visual Detection Test
```bash
# Show detections with OpenCV visualization
python show_detections.py

# This will:
# - Call the detection API for each test image
# - Display images with bounding boxes
# - Show detection details in console
```

### 3. Manual Testing with cURL

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Detection Test**:
```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@test_images/frame_000000.png" \
  -F "detect_face=true" \
  -F "detect_license_plate=true"
```

**Blur Test**:
```bash
curl -X POST "http://localhost:8000/blur" \
  -F "file=@test_images/frame_000000.png" \
  -F "face_blur_strength=25" \
  -F "plate_blur_strength=20"
```

### 4. Using the REST File
Use the provided `api_tests.rest` file with REST client extensions:
- VS Code REST Client
- IntelliJ HTTP Client
- Postman

## 🔧 Troubleshooting

### Common Issues

#### 1. Module Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'insightface'
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### 2. Model Loading Errors
```bash
# Error: Model file not found
# Solution: Ensure models are in the correct location
ls -la models/
# Should contain: yolov8n.pt and license_plate_detector.pt
```

#### 3. Port Already in Use
```bash
# Error: Address already in use
# Solution: Kill existing process or use different port
lsof -ti:8000 | xargs kill -9
# Or change port in main.py
```

#### 4. Permission Errors
```bash
# Error: Permission denied
# Solution: Check file permissions
chmod +x *.py
chmod 755 models/
chmod 755 output/
```

#### 5. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce image size or use smaller models
# Edit detect_face.py and detect_lp.py to reduce input sizes
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
# Set environment variable
export DEBUG=True

# Or modify main.py
uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
```

### Log Files
Check server logs for detailed error information:
```bash
# If running with nohup
tail -f server.log

# If running in foreground, logs appear in terminal
```

## 🚀 Production Deployment

### 1. Using Gunicorn (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Start with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t unified-detection .
docker run -p 8000:8000 unified-detection
```

### 3. Using Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Environment-Specific Configuration
Create different configuration files:
- `config/development.py`
- `config/production.py`
- `config/testing.py`

## 📊 Performance Optimization

### 1. Model Optimization
- Use smaller models for faster inference
- Enable GPU acceleration if available
- Implement model caching

### 2. API Optimization
- Implement request caching
- Use async processing for large files
- Add rate limiting

### 3. System Optimization
- Increase worker processes
- Use load balancing
- Implement horizontal scaling

## 🔒 Security Considerations

### 1. Input Validation
- Validate file types and sizes
- Implement file size limits
- Sanitize file names

### 2. Authentication
- Add API key authentication
- Implement rate limiting
- Use HTTPS in production

### 3. Data Privacy
- Implement automatic file cleanup
- Use secure file storage
- Add audit logging

## 📞 Support

### Getting Help
1. Check the troubleshooting section
2. Review server logs
3. Test with provided sample images
4. Verify all dependencies are installed

### Common Commands
```bash
# Check server status
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test the system
python test_api.py

# Show visual detections
python show_detections.py
```

---

## 🎉 Success!

If you see this message and the server is running, congratulations! Your Unified Detection Production System is ready to use.

**Next Steps:**
1. Test the API endpoints using the provided REST file
2. Integrate with your application
3. Customize detection parameters as needed
4. Deploy to production environment

**Happy Detecting!** 🚀
