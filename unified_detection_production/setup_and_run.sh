#!/bin/bash

# =============================================================================
# Unified Detection Production System - Setup and Run Script
# =============================================================================
# This script handles everything from Python version checking to running the server
# Author: TELUS Hackathon Team
# Version: 1.0.0
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MIN_PYTHON_VERSION="3.9"
REQUIRED_PYTHON_VERSION="3.9"
SERVER_HOST="0.0.0.0"
SERVER_PORT="8000"
VENV_NAME="venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}=============================================================================${NC}"
    echo -e "${PURPLE}   UNIFIED DETECTION PRODUCTION SYSTEM - SETUP AND RUN${NC}"
    echo -e "${PURPLE}=============================================================================${NC}"
    echo
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH"
        print_error "Please install Python 3.9 or higher"
        print_error "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_VERSION_FULL=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    
    # Check if version meets minimum requirement
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        print_success "Python $PYTHON_VERSION_FULL - OK (meets minimum requirement of $MIN_PYTHON_VERSION)"
    else
        print_error "Python $PYTHON_VERSION_FULL - FAILED"
        print_error "Minimum required version: $MIN_PYTHON_VERSION"
        print_error "Please upgrade Python to version 3.9 or higher"
        exit 1
    fi
}

# Function to check if we're in the right directory
check_directory() {
    print_status "Checking project directory..."
    
    if [[ ! -f "main.py" ]]; then
        print_error "main.py not found in current directory"
        print_error "Please run this script from the unified_detection_production directory"
        exit 1
    fi
    
    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt not found"
        print_error "Please ensure you're in the correct project directory"
        exit 1
    fi
    
    print_success "Project directory structure verified"
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Setting up virtual environment..."
    
    if [[ -d "$VENV_NAME" ]]; then
        print_warning "Virtual environment already exists"
        print_status "Activating existing virtual environment..."
        source "$VENV_NAME/bin/activate" 2>/dev/null || source "$VENV_NAME/Scripts/activate" 2>/dev/null
    else
        print_status "Creating new virtual environment..."
        python3 -m venv "$VENV_NAME"
        
        # Activate virtual environment
        if [[ -f "$VENV_NAME/bin/activate" ]]; then
            source "$VENV_NAME/bin/activate"
        elif [[ -f "$VENV_NAME/Scripts/activate" ]]; then
            source "$VENV_NAME/Scripts/activate"
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
        
        print_success "Virtual environment created and activated"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    print_status "Installing required packages..."
    if pip install -r requirements.txt; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        print_error "Please check requirements.txt and try again"
        exit 1
    fi
}

# Function to check if models exist
check_models() {
    print_status "Checking AI models..."
    
    MODELS_DIR="models"
    if [[ ! -d "$MODELS_DIR" ]]; then
        print_status "Creating models directory..."
        mkdir -p "$MODELS_DIR"
    fi
    
    # Check for required models
    if [[ -f "$MODELS_DIR/yolov8n.pt" ]]; then
        print_success "YOLO model found: yolov8n.pt"
    else
        print_warning "YOLO model not found - will be downloaded automatically on first run"
    fi
    
    if [[ -f "$MODELS_DIR/license_plate_detector.pt" ]]; then
        print_success "License plate model found: license_plate_detector.pt"
    else
        print_warning "License plate model not found - using default detection"
    fi
}

# Function to check test images
check_test_images() {
    print_status "Checking test images..."
    
    TEST_IMAGES_DIR="test_images"
    if [[ ! -d "$TEST_IMAGES_DIR" ]]; then
        print_warning "Test images directory not found"
        print_status "Creating test images directory..."
        mkdir -p "$TEST_IMAGES_DIR"
    else
        IMAGE_COUNT=$(find "$TEST_IMAGES_DIR" -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | wc -l)
        if [[ $IMAGE_COUNT -gt 0 ]]; then
            print_success "Found $IMAGE_COUNT test images"
        else
            print_warning "No test images found in test_images/ directory"
        fi
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p output
    mkdir -p api_results
    mkdir -p uploads
    
    print_success "Directories created successfully"
}

# Function to test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test core imports
    if python -c "
import cv2
import numpy as np
import ultralytics
import insightface
import fastapi
import uvicorn
print('All core dependencies imported successfully')
"; then
        print_success "Core dependencies test passed"
    else
        print_error "Core dependencies test failed"
        exit 1
    fi
    
    # Test detection functionality
    print_status "Testing detection functionality..."
    if python -c "
from api import detect_objects
import os
if os.path.exists('test_images'):
    test_images = [f for f in os.listdir('test_images') if f.endswith(('.png', '.jpg', '.jpeg'))]
    if test_images:
        print('Testing with:', test_images[0])
        results = detect_objects(f'test_images/{test_images[0]}', detect_face=True, detect_lp=True)
        print(f'Detection test passed - Found {len(results.get(\"faces\", []))} faces, {len(results.get(\"license_plates\", []))} license plates')
    else:
        print('No test images available for testing')
else:
    print('No test images directory available for testing')
"; then
        print_success "Detection functionality test passed"
    else
        print_warning "Detection functionality test failed - but continuing..."
    fi
}

# Function to start the server
start_server() {
    print_status "Starting FastAPI server..."
    print_status "Server will be available at: http://$SERVER_HOST:$SERVER_PORT"
    print_status "API Documentation: http://$SERVER_HOST:$SERVER_PORT/docs"
    print_status "Press Ctrl+C to stop the server"
    echo
    
    # Start the server
    python main.py
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -s, --setup-only    Only run setup, don't start server"
    echo "  -t, --test-only     Only run tests, don't start server"
    echo "  -f, --force         Force reinstall dependencies"
    echo "  --host HOST         Server host (default: $SERVER_HOST)"
    echo "  --port PORT         Server port (default: $SERVER_PORT)"
    echo
    echo "Examples:"
    echo "  $0                  # Full setup and start server"
    echo "  $0 --setup-only     # Only setup, don't start server"
    echo "  $0 --test-only      # Only run tests"
    echo "  $0 --force          # Force reinstall dependencies"
    echo "  $0 --host 127.0.0.1 --port 8080  # Custom host and port"
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill
    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Parse command line arguments
SETUP_ONLY=false
TEST_ONLY=false
FORCE_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--setup-only)
            SETUP_ONLY=true
            shift
            ;;
        -t|--test-only)
            TEST_ONLY=true
            shift
            ;;
        -f|--force)
            FORCE_INSTALL=true
            shift
            ;;
        --host)
            SERVER_HOST="$2"
            shift 2
            ;;
        --port)
            SERVER_PORT="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header
    
    # Step 1: Check Python version
    check_python_version
    
    # Step 2: Check directory
    check_directory
    
    # Step 3: Create virtual environment
    create_virtual_environment
    
    # Step 4: Install dependencies
    if [[ "$FORCE_INSTALL" == true ]]; then
        print_status "Force reinstall requested..."
        pip install --upgrade --force-reinstall -r requirements.txt
    else
        install_dependencies
    fi
    
    # Step 5: Check models
    check_models
    
    # Step 6: Check test images
    check_test_images
    
    # Step 7: Create directories
    create_directories
    
    # Step 8: Test installation
    test_installation
    
    if [[ "$TEST_ONLY" == true ]]; then
        print_success "Tests completed successfully!"
        exit 0
    fi
    
    if [[ "$SETUP_ONLY" == true ]]; then
        print_success "Setup completed successfully!"
        print_status "To start the server, run: $0"
        exit 0
    fi
    
    # Step 9: Start server
    start_server
}

# Run main function
main "$@"
