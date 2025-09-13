#!/usr/bin/env python3
"""
Simple Demo Script for Unified Detection Production System
Demonstrates different endpoints with a single image and visualization
"""

import requests
import cv2
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
IMAGE_PATH = "test_images/frame_000000.png"  # Change this to your image path
OUTPUT_DIR = "demo_output"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server")
        print("💡 Make sure to start the server first: python main.py")
        return False

def detect_objects(image_path, detect_face=True, detect_lp=True):
    """Call detection API"""
    print(f"\n🔍 Detecting objects in: {os.path.basename(image_path)}")
    print(f"   Face detection: {detect_face}")
    print(f"   License plate detection: {detect_lp}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'detect_face': detect_face,
                'detect_license_plate': detect_lp
            }
            
            response = requests.post(f"{BASE_URL}/detect", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Detection successful!")
                print(f"   📊 Faces: {result['total_faces']}, License Plates: {result['total_license_plates']}")
                print(f"   ⏱️  Processing time: {result['processing_time_ms']}ms")
                return result
            else:
                print(f"❌ Detection failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        return None

def blur_objects(image_path, detect_face=True, detect_lp=True, face_blur=25, plate_blur=20):
    """Call blur API"""
    print(f"\n🔒 Blurring objects in: {os.path.basename(image_path)}")
    print(f"   Face blur strength: {face_blur}")
    print(f"   License plate blur strength: {plate_blur}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'detect_face': detect_face,
                'detect_license_plate': detect_lp,
                'face_blur_strength': face_blur,
                'plate_blur_strength': plate_blur
            }
            
            response = requests.post(f"{BASE_URL}/blur", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Blur successful!")
                print(f"   🔒 Objects blurred: {result['detections_applied']}")
                print(f"   💾 Output saved: {result['blurred_image_path']}")
                print(f"   ⏱️  Processing time: {result['processing_time_ms']}ms")
                return result
            else:
                print(f"❌ Blur failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error during blur: {e}")
        return None

def visualize_detections(image_path, detections, save_path=None):
    """Visualize detections on image"""
    print(f"\n👀 Visualizing detections...")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return None
    
    # Draw bounding boxes
    for detection in detections['detections']:
        x1, y1, x2, y2 = detection['x1'], detection['y1'], detection['x2'], detection['y2']
        confidence = detection['confidence']
        label = detection['label']
        
        # Choose color based on label
        if label == 'face':
            color = (0, 255, 0)  # Green for faces
            thickness = 3
        else:  # license_plate
            color = (0, 0, 255)  # Red for license plates
            thickness = 3
        
        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label with confidence
        label_text = f"{label}: {confidence:.3f}"
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        
        # Draw background for text
        cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        
        # Draw text
        cv2.putText(image, label_text, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        print(f"   📍 {label}: BBox({x1}, {y1}, {x2}, {y2}) - Conf: {confidence:.3f}")
    
    # Save image if path provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, image)
        print(f"💾 Visualization saved: {save_path}")
    
    return image

def display_image(image, title="Detection Results"):
    """Display image with OpenCV"""
    # Resize image if too large
    height, width = image.shape[:2]
    if width > 1200 or height > 800:
        scale = min(1200/width, 800/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height))
    
    cv2.imshow(title, image)
    print(f"\n⌨️  Press any key to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    """Main demo function"""
    print_header("UNIFIED DETECTION SYSTEM - SIMPLE DEMO")
    
    # Check if image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found: {IMAGE_PATH}")
        print("💡 Please update IMAGE_PATH in the script to point to a valid image")
        return
    
    # Check server
    if not check_server():
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Demo 1: Detect both faces and license plates
    print_header("DEMO 1: DETECT FACES AND LICENSE PLATES")
    detections = detect_objects(IMAGE_PATH, detect_face=True, detect_lp=True)
    
    if detections and detections['detections']:
        # Visualize detections
        image = visualize_detections(IMAGE_PATH, detections, 
                                   f"{OUTPUT_DIR}/detections.jpg")
        if image is not None:
            display_image(image, "Detections - Faces & License Plates")
    
    # Demo 2: Detect only faces
    print_header("DEMO 2: DETECT FACES ONLY")
    face_detections = detect_objects(IMAGE_PATH, detect_face=True, detect_lp=False)
    
    if face_detections and face_detections['detections']:
        image = visualize_detections(IMAGE_PATH, face_detections, 
                                   f"{OUTPUT_DIR}/faces_only.jpg")
        if image is not None:
            display_image(image, "Detections - Faces Only")
    
    # Demo 3: Detect only license plates
    print_header("DEMO 3: DETECT LICENSE PLATES ONLY")
    plate_detections = detect_objects(IMAGE_PATH, detect_face=False, detect_lp=True)
    
    if plate_detections and plate_detections['detections']:
        image = visualize_detections(IMAGE_PATH, plate_detections, 
                                   f"{OUTPUT_DIR}/plates_only.jpg")
        if image is not None:
            display_image(image, "Detections - License Plates Only")
    
    # Demo 4: Blur objects
    print_header("DEMO 4: BLUR DETECTED OBJECTS")
    blur_result = blur_objects(IMAGE_PATH, detect_face=True, detect_lp=True, 
                              face_blur=30, plate_blur=25)
    
    if blur_result:
        # Load and display blurred image
        blurred_path = blur_result['blurred_image_path']
        if os.path.exists(blurred_path):
            blurred_image = cv2.imread(blurred_path)
            if blurred_image is not None:
                # Copy to output directory
                output_blur_path = f"{OUTPUT_DIR}/blurred_result.jpg"
                cv2.imwrite(output_blur_path, blurred_image)
                print(f"💾 Blurred image copied to: {output_blur_path}")
                display_image(blurred_image, "Blurred Image")
    
    # Demo 5: Show API information
    print_header("DEMO 5: API INFORMATION")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            api_info = response.json()
            print("📋 API Information:")
            print(f"   Name: {api_info.get('message', 'N/A')}")
            print(f"   Version: {api_info.get('version', 'N/A')}")
            print("   Available Endpoints:")
            for endpoint, description in api_info.get('endpoints', {}).items():
                print(f"     - {endpoint}: {description}")
    except Exception as e:
        print(f"❌ Error getting API info: {e}")
    
    print_header("DEMO COMPLETED!")
    print("📁 Check the 'demo_output' folder for saved images")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("🎉 Thanks for trying the Unified Detection System!")

if __name__ == "__main__":
    main()
