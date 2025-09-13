#!/bin/bash

# Run Both Backend and Frontend
# This script starts both backend and frontend in separate terminals

set -e  # Exit on any error

echo "🚀 Starting Both Backend and Frontend"
echo "===================================="

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
if [ ! -d "unified_detection_production" ] || [ ! -d "detection-app" ]; then
    print_error "Please run this script from the production_backup directory"
    print_error "Expected directories: unified_detection_production, detection-app"
    exit 1
fi

# Check if setup has been run
if [ ! -d "unified_detection_production/venv" ] || [ ! -d "detection-app/node_modules" ]; then
    print_warning "Setup not completed. Running setup first..."
    ./setup.sh
fi

# Function to start backend in background
start_backend() {
    print_status "Starting backend server in background..."
    cd unified_detection_production
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    print_success "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend application..."
    cd detection-app
    export REACT_APP_API_URL=http://localhost:8000
    npm start
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_status "Stopping backend server (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
        fi
        rm -f backend.pid
    fi
    rm -f backend.log
    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Start backend
start_backend

# Wait a moment for backend to start
print_status "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is running successfully!"
else
    print_warning "Backend may not be ready yet. Check backend.log for details."
fi

# Start frontend
print_status "Starting frontend..."
print_status "Backend logs: tail -f backend.log"
print_status "Press Ctrl+C to stop both servers"
echo ""

start_frontend
