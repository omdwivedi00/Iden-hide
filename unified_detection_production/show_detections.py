#!/usr/bin/env python3
"""
Show Detection Results with OpenCV
"""

import requests
import cv2
import os
import time

def show_image_detections(server_url, image_path):
    """Show detections for a single image"""
    print(f"\n📸 Processing: {os.path.basename(image_path)}")
    print("-" * 50)
    
    # Call detection API
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {'detect_face': True, 'detect_license_plate': True}
            
            response = requests.post(f"{server_url}/detect", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Response: {result['message']}")
                print(f"📊 Faces: {result['total_faces']}, License Plates: {result['total_license_plates']}")
                print(f"⏱️  Processing time: {result['processing_time_ms']}ms")
                
                # Load and display image
                image = cv2.imread(image_path)
                if image is None:
                    print("❌ Could not load image")
                    return
                
                # Draw bounding boxes
                for detection in result['detections']:
                    x1, y1, x2, y2 = detection['x1'], detection['y1'], detection['x2'], detection['y2']
                    confidence = detection['confidence']
                    label = detection['label']
                    
                    # Choose color
                    color = (0, 255, 0) if label == 'face' else (0, 0, 255)  # Green for faces, Red for plates
                    
                    # Draw box
                    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label_text = f"{label}: {confidence:.3f}"
                    cv2.putText(image, label_text, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    print(f"   📍 {label}: BBox({x1}, {y1}, {x2}, {y2}) - Conf: {confidence:.3f}")
                
                # Resize for display
                height, width = image.shape[:2]
                if width > 1200 or height > 800:
                    scale = min(1200/width, 800/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    image = cv2.resize(image, (new_width, new_height))
                
                # Show image
                cv2.imshow(f"Detections: {os.path.basename(image_path)}", image)
                print(f"\n⌨️  Press any key to continue to next image...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
            else:
                print(f"❌ API Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    server_url = "http://localhost:8000"
    
    print("🎯 Show Detection Results")
    print("=" * 40)
    
    # Check server
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server")
        return
    
    # Test images
    images = [
        "test_images/frame_000000.png",
        "test_images/frame_000020.png", 
        "test_images/frame_000030.png"
    ]
    
    print(f"\n📸 Showing detections for {len(images)} images...")
    
    for i, image_path in enumerate(images):
        if os.path.exists(image_path):
            print(f"\n{'='*60}")
            print(f"IMAGE {i+1}/{len(images)}")
            show_image_detections(server_url, image_path)
        else:
            print(f"⚠️  Image not found: {image_path}")
    
    print(f"\n🎉 All images processed!")

if __name__ == "__main__":
    main()
