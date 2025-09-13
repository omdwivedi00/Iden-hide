#!/bin/bash

# =============================================================================
# Quick Setup Script for Unified Detection Production System
# =============================================================================
# Simple one-command setup and run
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Unified Detection Production System - Quick Setup${NC}"
echo "=================================================================="
echo

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Python 3.9+ required. Please install Python 3.9 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p output api_results uploads models

# Test installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
python -c "
from api import detect_objects
import os
print('✅ Core functionality test passed')
"

echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo
echo -e "${BLUE}🚀 Starting server...${NC}"
echo -e "${BLUE}📖 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🛑 Press Ctrl+C to stop${NC}"
echo

# Start server
python main.py
