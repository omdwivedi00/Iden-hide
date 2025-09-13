/**
 * Image Viewer Component
 * Displays images with bounding boxes and detection overlays
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';

const ViewerContainer = styled.div`
  position: relative;
  display: inline-block;
  max-width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
`;

const ImageWrapper = styled.div`
  position: relative;
  display: inline-block;
`;

const Canvas = styled.canvas`
  max-width: 100%;
  height: auto;
  display: block;
`;

const ControlsOverlay = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  z-index: 10;
`;

const ControlButton = styled.button`
  background: rgba(0,0,0,0.7);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    background: rgba(0,0,0,0.9);
  }

  &.active {
    background: #007bff;
  }
`;

const DetectionInfo = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  padding: 20px 15px 15px;
  font-size: 14px;
`;

const DetectionStats = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const DetectionItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
  font-size: 12px;
`;

const DetectionLabel = styled.span`
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
  background: ${props => props.type === 'face' ? '#28a745' : '#dc3545'};
  color: white;
`;

const Confidence = styled.span`
  color: #ccc;
`;

const ImageViewer = ({ 
  image, 
  detections = [], 
  isDownloading = false,
  showBoundingBoxes = true, 
  showLabels = true,
  showBlurred = false,
  onToggleBoundingBoxes,
  onToggleLabels,
  onToggleBlurred
}) => {
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Draw bounding boxes on canvas
  const drawBoundingBoxes = useCallback(() => {
    if (!imageLoaded || !canvasRef.current || !imageRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = imageRef.current;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the image
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    if (!showBoundingBoxes || !detections || detections.length === 0) return;

    // Draw bounding boxes
    detections.forEach((detection, index) => {
      const { x1, y1, x2, y2, label, confidence } = detection;
      
      // Choose color based on label
      const color = label === 'face' ? '#00FF00' : '#FF0000';
      
      // Draw rectangle
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      
      // Draw label with confidence if enabled
      if (showLabels) {
        const labelText = `${label}: ${(confidence * 100).toFixed(1)}%`;
        const textMetrics = ctx.measureText(labelText);
        const textWidth = textMetrics.width;
        const textHeight = 16;
        
        // Draw background rectangle for text
        ctx.fillStyle = color;
        ctx.fillRect(x1, y1 - textHeight - 5, textWidth + 10, textHeight + 5);
        
        // Draw text
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(labelText, x1 + 5, y1 - 5);
      }
    });
  }, [imageLoaded, detections, showBoundingBoxes, showLabels]);

  // Handle image load
  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  // Get the appropriate image source
  const getImageSource = () => {
    if (showBlurred && image.blurred && image.blurred.blurred_image_path) {
      // Return blurred image URL - extract filename from path
      const filename = image.blurred.blurred_image_path.split('/').pop();
      return `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/download/${filename}`;
    }
    return image.preview || image.url;
  };

  // Update canvas when image or settings change
  useEffect(() => {
    if (imageLoaded) {
      drawBoundingBoxes();
    }
  }, [imageLoaded, detections, showBoundingBoxes, showLabels, showBlurred, drawBoundingBoxes]);

  // Set canvas size when image loads
  useEffect(() => {
    if (imageLoaded && imageRef.current && canvasRef.current) {
      const img = imageRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas size to match image
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      
      // Redraw
      drawBoundingBoxes();
    }
  }, [imageLoaded, drawBoundingBoxes]);

  if (!image) return null;

  return (
    <ViewerContainer>
      <ImageWrapper>
        <img
          ref={imageRef}
          src={getImageSource()}
          alt={image.filename}
          style={{ display: 'none' }}
          onLoad={handleImageLoad}
        />
        
        <Canvas
          ref={canvasRef}
          style={{ 
            maxWidth: '100%', 
            height: 'auto',
            display: imageLoaded ? 'block' : 'none'
          }}
        />
        
        {!imageLoaded && (
          <div style={{
            width: '300px',
            height: '200px',
            background: '#f8f9fa',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#666'
          }}>
            Loading image...
          </div>
        )}

        <ControlsOverlay>
          <ControlButton
            className={showBoundingBoxes ? 'active' : ''}
            onClick={onToggleBoundingBoxes}
            title="Toggle bounding boxes"
          >
            📦 {showBoundingBoxes ? 'Hide' : 'Show'} Boxes
          </ControlButton>
          
          <ControlButton
            className={showLabels ? 'active' : ''}
            onClick={onToggleLabels}
            title="Toggle labels"
            disabled={!showBoundingBoxes}
          >
            🏷️ {showLabels ? 'Hide' : 'Show'} Labels
          </ControlButton>

          {image.blurred && (
            <ControlButton
              className={showBlurred ? 'active' : ''}
              onClick={onToggleBlurred}
              title="Toggle blurred image"
            >
              🔒 {showBlurred ? 'Show Original' : 'Show Blurred'}
            </ControlButton>
          )}
        </ControlsOverlay>

        {/* Download Buttons */}
        <div style={{ 
          position: 'absolute', 
          bottom: '10px', 
          left: '10px', 
          display: 'flex', 
          gap: '8px', 
          zIndex: 10 
        }}>
          <ControlButton
            disabled={isDownloading}
            onClick={() => {
              // Download original image
              const link = document.createElement('a');
              link.href = image.preview || image.url;
              link.download = image.filename;
              link.click();
            }}
            title="Download original image"
          >
            {isDownloading ? '⏳' : '📥'} Original
          </ControlButton>
          
          {image.blurred && (
            <ControlButton
              disabled={isDownloading}
              onClick={() => {
                // Download blurred image
                const filename = image.blurred.blurred_image_path.split('/').pop();
                const url = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/download/${filename}`;
                const link = document.createElement('a');
                link.href = url;
                link.download = `blurred_${image.filename}`;
                link.click();
              }}
              title="Download blurred image"
            >
              {isDownloading ? '⏳' : '🔒'} Blurred
            </ControlButton>
          )}
        </div>

        {detections && detections.length > 0 && (
          <DetectionInfo>
            <DetectionStats>
              <span>Faces: {detections.filter(d => d.label === 'face').length}</span>
              <span>License Plates: {detections.filter(d => d.label === 'license_plate').length}</span>
            </DetectionStats>
            
            {detections.map((detection, index) => (
              <DetectionItem key={index}>
                <DetectionLabel type={detection.label}>
                  {detection.label}
                </DetectionLabel>
                <Confidence>
                  {(detection.confidence * 100).toFixed(1)}%
                </Confidence>
                <span>
                  [{detection.x1}, {detection.y1}, {detection.x2}, {detection.y2}]
                </span>
              </DetectionItem>
            ))}
          </DetectionInfo>
        )}
      </ImageWrapper>
    </ViewerContainer>
  );
};

export default ImageViewer;
