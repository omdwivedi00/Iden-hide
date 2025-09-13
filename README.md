# Production Backup - Unified Detection System

This folder contains a complete backup of the unified detection system with both backend and frontend components.

## 📁 Contents

- `unified_detection_production/` - Backend API server with detection and S3 processing
- `detection-app/` - React.js frontend application

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the complete setup
./setup.sh
```

### Option 2: Manual Setup
```bash
# Step 1: Start backend server
./step1.sh

# Step 2: In a new terminal, start frontend
./step2.sh
```

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn
- Git

## 🔧 Backend Features

- **Face Detection**: Advanced face detection with YOLO + SCRFD
- **License Plate Detection**: Vehicle detection + license plate detection with max confidence selection
- **Blur Processing**: Oval blur for faces, rectangular blur for license plates
- **S3 Integration**: Process images from/to AWS S3
- **REST API**: Complete REST API with FastAPI
- **Image Viewing**: S3 image viewing with presigned URLs

## 🎨 Frontend Features

- **Single Image Processing**: Upload and process individual images
- **Folder Processing**: Batch process local folders
- **S3 Processing**: Process images from S3 buckets
- **Image Viewer**: View processed images with bounding boxes
- **S3 Image Viewer**: View S3 images with navigation
- **Download Support**: Download processed images
- **Progress Tracking**: Real-time processing progress

## 📊 API Endpoints

### Detection & Blur
- `POST /detect` - Detect faces and license plates
- `POST /blur` - Apply blur to detected objects
- `GET /download/{filename}` - Download processed images

### S3 Processing
- `POST /s3/process-single` - Process single S3 image
- `POST /s3/process-folder` - Process S3 folder
- `POST /s3/view-image` - Get presigned URL for S3 image
- `POST /s3/list-folder` - List S3 folder contents
- `GET /s3/test-credentials` - Test S3 credentials

## 🛠️ Configuration

### Backend Configuration
- Edit `unified_detection_production/main.py` for API settings
- Edit `unified_detection_production/detect_*.py` for detection parameters
- Set environment variables for AWS credentials

### Frontend Configuration
- Edit `detection-app/src/services/apiService.js` for API URL
- Edit `detection-app/src/services/s3Service.js` for S3 settings

## 📝 Usage Examples

### Backend API
```bash
# Test detection
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d '{"detect_face": true, "detect_license_plate": true}'

# Test S3 processing
curl -X POST "http://localhost:8000/s3/process-single" \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "aws_access_key_id": "your-key",
      "aws_secret_access_key": "your-secret"
    },
    "input_s3_path": "s3://bucket/input.jpg",
    "output_s3_path": "s3://bucket/output.jpg"
  }'
```

### Frontend
1. Open http://localhost:3000
2. Choose processing mode (Single Image, Folder, or S3)
3. Upload images or configure S3 settings
4. Process and view results

## 🔍 Troubleshooting

### Backend Issues
- Check Python version: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check model files exist in `models/` folder
- Verify port 8000 is available

### Frontend Issues
- Check Node.js version: `node --version`
- Install dependencies: `npm install`
- Check port 3000 is available
- Verify backend is running

### S3 Issues
- Verify AWS credentials are correct
- Check S3 bucket permissions
- Ensure S3 paths are valid
- Check network connectivity

## 📚 Documentation

- `unified_detection_production/README.md` - Backend documentation
- `unified_detection_production/SETUP_GUIDE.md` - Detailed setup guide
- `detection-app/README.md` - Frontend documentation
- `unified_detection_production/LICENSE_PLATE_IMPROVEMENTS.md` - License plate detection improvements

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in terminal
3. Check the API documentation at http://localhost:8000/docs
4. Verify all dependencies are installed

## 📄 License

This project is part of the hackathon submission for TELUS.
