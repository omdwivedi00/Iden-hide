#!/bin/bash

# Step 2: Start Frontend Application
# This script starts the React frontend application

set -e  # Exit on any error

echo "🎨 Starting Frontend Application"
echo "==============================="

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
if [ ! -d "detection-app" ]; then
    print_error "Please run this script from the production_backup directory"
    print_error "Expected directory: detection-app"
    exit 1
fi

# Change to frontend directory
cd detection-app

# Check if node_modules exists and if react-scripts is properly installed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/react-scripts" ] || ! npm list react-scripts > /dev/null 2>&1; then
    print_warning "Node modules not found or corrupted. Installing dependencies..."
    print_status "Cleaning up existing node_modules..."
    rm -rf node_modules package-lock.json
    print_status "Installing fresh dependencies..."
    npm install
fi

# Verify react-scripts installation
if ! npm list react-scripts > /dev/null 2>&1; then
    print_error "react-scripts installation failed. Trying to fix..."
    npm install react-scripts --save
fi

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please check the detection-app directory."
    exit 1
fi

# Check if backend is running
print_status "Checking if backend server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend server is running!"
else
    print_warning "Backend server is not running on http://localhost:8000"
    print_warning "Please start the backend first with './step1.sh'"
    print_warning "The frontend will still start but API calls may fail."
fi

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 3000 is already in use. The app may not start properly."
    print_warning "Please stop any process using port 3000 or use a different port."
fi

# Set environment variables
print_status "Setting up environment variables..."
export REACT_APP_API_URL=http://localhost:8000

# Start the React development server
print_status "Starting React development server on http://localhost:3000"
print_status "Press Ctrl+C to stop the server"
echo ""

# Start npm start
npm start
