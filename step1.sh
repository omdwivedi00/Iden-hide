#!/bin/bash

# Step 1: Start Backend Server
# This script starts the Python backend server

set -e  # Exit on any error

echo "🔧 Starting Backend Server"
echo "========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "unified_detection_production" ]; then
    print_error "Please run this script from the production_backup directory"
    print_error "Expected directory: unified_detection_production"
    exit 1
fi

# Change to backend directory
cd unified_detection_production

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run './setup.sh' first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
print_status "Checking Python dependencies..."
if ! python -c "import fastapi, uvicorn, ultralytics" 2>/dev/null; then
    print_warning "Some dependencies missing. Installing..."
    pip install -r requirements.txt
fi

# Check if models directory exists
if [ ! -d "models" ]; then
    print_warning "Models directory not found. Creating..."
    mkdir -p models
    print_warning "Please download the required model files to the models/ directory:"
    print_warning "- yolov8n.pt or yolo11n.pt (for vehicle detection)"
    print_warning "- license_plate_detector.pt (for license plate detection)"
    print_warning "- scrfd_500m.onnx (for face detection)"
fi

# Test imports
print_status "Testing backend imports..."
if python -c "from main import app; print('✅ Backend imports successfully')" 2>/dev/null; then
    print_success "Backend imports successful!"
else
    print_error "Backend import failed. Please check dependencies."
    exit 1
fi

# Start the server
print_status "Starting backend server on http://localhost:8000"
print_status "API documentation available at http://localhost:8000/docs"
print_status "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
