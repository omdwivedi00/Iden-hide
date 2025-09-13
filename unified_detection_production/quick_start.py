#!/usr/bin/env python3
"""
Quick Start Script for Unified Detection Production System
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("🚀" + "="*60 + "🚀")
    print("   UNIFIED DETECTION PRODUCTION SYSTEM - QUICK START")
    print("🚀" + "="*60 + "🚀")
    print()

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'cv2', 'numpy', 'ultralytics', 'insightface', 
        'fastapi', 'uvicorn', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_models():
    """Check if model files exist"""
    print("\n🤖 Checking AI models...")
    models_dir = Path("models")
    required_models = ["yolov8n.pt"]
    optional_models = ["license_plate_detector.pt"]
    
    all_good = True
    for model in required_models:
        model_path = models_dir / model
        if model_path.exists():
            print(f"✅ {model} - Found")
        else:
            print(f"❌ {model} - Missing (will be downloaded automatically)")
            all_good = False
    
    for model in optional_models:
        model_path = models_dir / model
        if model_path.exists():
            print(f"✅ {model} - Found")
        else:
            print(f"⚠️  {model} - Not found (using default detection)")
    
    return all_good

def check_test_images():
    """Check if test images exist"""
    print("\n📸 Checking test images...")
    test_dir = Path("test_images")
    if not test_dir.exists():
        print("❌ test_images/ directory not found")
        return False
    
    image_files = list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpg"))
    if not image_files:
        print("❌ No test images found in test_images/")
        return False
    
    print(f"✅ Found {len(image_files)} test images")
    for img in image_files[:3]:  # Show first 3
        print(f"   - {img.name}")
    if len(image_files) > 3:
        print(f"   ... and {len(image_files) - 3} more")
    
    return True

def test_core_functionality():
    """Test core detection functionality"""
    print("\n🧪 Testing core functionality...")
    try:
        from api import detect_objects
        from pathlib import Path
        
        # Find a test image
        test_images = list(Path("test_images").glob("*.png")) + list(Path("test_images").glob("*.jpg"))
        if not test_images:
            print("❌ No test images available for testing")
            return False
        
        test_image = test_images[0]
        print(f"   Testing with: {test_image.name}")
        
        # Test detection
        results = detect_objects(str(test_image), detect_face=True, detect_lp=True)
        
        faces = len(results.get('faces', []))
        plates = len(results.get('license_plates', []))
        
        print(f"✅ Detection test passed - Found {faces} faces, {plates} license plates")
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting FastAPI server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        print("   Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully on http://localhost:8000")
                return process
            else:
                print("❌ Server health check failed")
                return None
        except requests.exceptions.RequestException:
            print("❌ Server not responding")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_api_tests():
    """Run API tests"""
    print("\n🧪 Running API tests...")
    try:
        result = subprocess.run([sys.executable, "test_api.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ API tests passed")
            print("📊 Test results:")
            # Extract summary from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Success rate:' in line or 'Testing completed' in line:
                    print(f"   {line}")
            return True
        else:
            print("❌ API tests failed")
            print("Error output:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ API tests timed out")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎉 QUICK START COMPLETED!")
    print("="*50)
    print("\n📚 What you can do now:")
    print("\n1. 🌐 View API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    
    print("\n2. 🧪 Test the API:")
    print("   - Run: python test_api.py")
    print("   - Use: API_TESTS.rest file with REST client")
    
    print("\n3. 👀 Visual Testing:")
    print("   - Run: python show_detections.py")
    print("   - Shows images with bounding boxes")
    
    print("\n4. 📖 Documentation:")
    print("   - Read: SETUP_GUIDE.md for detailed instructions")
    print("   - API tests: API_TESTS.rest")
    
    print("\n5. 🔧 Customization:")
    print("   - Edit detection parameters in detect_face.py and detect_lp.py")
    print("   - Modify blur settings in visualizer.py")
    print("   - Configure server settings in main.py")
    
    print("\n6. 🚀 Production Deployment:")
    print("   - See SETUP_GUIDE.md for deployment options")
    print("   - Use Docker, Gunicorn, or Nginx for production")
    
    print("\n💡 Quick Commands:")
    print("   - Health check: curl http://localhost:8000/health")
    print("   - Stop server: Ctrl+C")
    print("   - Restart: python main.py")

def main():
    """Main quick start function"""
    print_banner()
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 To install dependencies, run:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_models():
        print("\n⚠️  Some models are missing but will be downloaded automatically")
    
    if not check_test_images():
        print("\n❌ Test images are required for testing")
        sys.exit(1)
    
    # Test core functionality
    if not test_core_functionality():
        print("\n❌ Core functionality test failed")
        sys.exit(1)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("\n❌ Failed to start server")
        sys.exit(1)
    
    # Run API tests
    if not run_api_tests():
        print("\n⚠️  API tests failed, but server is running")
    
    # Show next steps
    show_next_steps()
    
    print("\n🎯 Server is running! Press Ctrl+C to stop.")
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        server_process.terminate()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()
