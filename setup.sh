#!/bin/bash

# Production Backup Setup Script
# This script sets up both backend and frontend for the unified detection system

set -e  # Exit on any error

echo "🚀 Starting Production Backup Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -d "unified_detection_production" ] || [ ! -d "detection-app" ]; then
    print_error "Please run this script from the production_backup directory"
    print_error "Expected directories: unified_detection_production, detection-app"
    exit 1
fi

print_status "Found required directories: unified_detection_production, detection-app"

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python version: $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js version: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

NPM_VERSION=$(npm --version)
print_success "npm version: $NPM_VERSION"

print_success "All prerequisites met!"

# Setup backend
print_status "Setting up backend..."
cd unified_detection_production

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend setup completed!"

# Setup frontend
print_status "Setting up frontend..."
cd ../detection-app

# Clean and install Node.js dependencies
print_status "Installing Node.js dependencies..."
print_status "Cleaning up any existing node_modules..."
rm -rf node_modules package-lock.json
print_status "Installing fresh dependencies..."
npm install

# Verify react-scripts installation
if ! npm list react-scripts > /dev/null 2>&1; then
    print_warning "react-scripts not found. Installing..."
    npm install react-scripts --save
fi

print_success "Frontend setup completed!"

# Go back to production_backup directory
cd ..

print_success "Setup completed successfully!"
echo ""
print_status "Next steps:"
echo "1. Run './step1.sh' to start the backend server"
echo "2. In a new terminal, run './step2.sh' to start the frontend"
echo ""
print_status "Or run both automatically with:"
echo "  ./run_both.sh"
echo ""
print_success "Setup script completed! 🎉"
