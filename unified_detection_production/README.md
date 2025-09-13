# 🚀 Unified Detection Production System

A clean, production-ready system for face and license plate detection with blur functionality.

## 📁 Project Structure

```
unified_detection_production/
├── models/                          # AI model files
│   ├── yolov8n.pt                  # YOLO model for detection
│   └── license_plate_detector.pt   # License plate detection model
├── test_images/                     # Sample test images
│   ├── frame_000000.png
│   ├── frame_000020.png
│   └── frame_000030.png
├── api_results/                     # Test results
├── output/                          # Generated images
├── detect_face.py                   # Face detection module
├── detect_lp.py                     # License plate detection module
├── unified_detector.py              # Main detection orchestrator
├── visualizer.py                    # Visualization and blur functions
├── api.py                          # Core API functions
├── models.py                       # Pydantic models
├── detection_service.py            # FastAPI service layer
├── main.py                         # FastAPI server
├── test_api.py                     # API test script
├── show_detections.py              # Visual detection display
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python main.py
```

### 3. Test the API
```bash
python test_api.py
```

### 4. Show Visual Detections
```bash
python show_detections.py
```

## 🔧 API Endpoints

### Detection API
**POST** `/detect`
- Detects faces and license plates
- Returns bounding box coordinates and confidence scores

### Blur API
**POST** `/blur`
- Blurs detected objects (oval for faces, rectangular for license plates)
- Returns path to blurred image

### Utility Endpoints
- **GET** `/health` - Health check
- **GET** `/` - API information
- **GET** `/outputs` - List output files
- **GET** `/download/{filename}` - Download processed images

## 📊 Features

- ✅ **Face Detection**: Using YOLO + InsightFace
- ✅ **License Plate Detection**: Using YOLO with vehicle-first approach
- ✅ **Blur Functionality**: Oval blur for faces, rectangular for license plates
- ✅ **REST API**: FastAPI with automatic documentation
- ✅ **Visual Display**: OpenCV-based visualization
- ✅ **Modular Design**: Clean, reusable components

## 🎯 Usage Examples

### Python API
```python
from api import detect_objects, visualize_detections, blur_detections

# Detect objects
results = detect_objects('test_images/frame_000000.png')

# Visualize detections
visualize_detections('test_images/frame_000000.png', results, 
                    save_path='output/detection.jpg')

# Blur detections
blur_detections('test_images/frame_000000.png', results, 
               save_path='output/blurred.jpg')
```

### REST API
```bash
# Detection
curl -X POST "http://localhost:8000/detect" \
  -F "file=@test_images/frame_000000.png" \
  -F "detect_face=true" \
  -F "detect_license_plate=true"

# Blur
curl -X POST "http://localhost:8000/blur" \
  -F "file=@test_images/frame_000000.png" \
  -F "face_blur_strength=25" \
  -F "plate_blur_strength=20"
```

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

The system includes comprehensive testing:
- **API Tests**: `python test_api.py`
- **Visual Tests**: `python show_detections.py`
- **Health Check**: `curl http://localhost:8000/health`

## 🎉 Production Ready

This system is designed for production use with:
- Clean, modular architecture
- Comprehensive error handling
- Automatic file management
- RESTful API design
- Complete documentation
