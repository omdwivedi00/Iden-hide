/**
 * Full Screen Image Viewer Component
 * Modal for viewing images in full screen with navigation
 */

import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import ImageViewer from './ImageViewer';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(3, 6, 12, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
`;

const ModalContent = styled.div`
  position: relative;
  max-width: 95vw;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const ImageContainer = styled.div`
  position: relative;
  max-width: 100%;
  max-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
`;

const MainImage = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
`;

const NavigationButton = styled.button`
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  
  &:hover {
    background: white;
    transform: translateY(-50%) scale(1.1);
  }
  
  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    transform: translateY(-50%);
  }
  
  &.prev {
    left: -25px;
  }
  
  &.next {
    right: -25px;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: -60px;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: white;
    transform: scale(1.1);
  }
`;

const ImageInfo = styled.div`
  background: rgba(15, 20, 32, 0.8);
  border-radius: 12px;
  padding: 15px 20px;
  text-align: center;
  min-width: 300px;
  color: #e9eefc;
  border: 1px solid rgba(255, 255, 255, 0.08);
`;

const ImageTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #e9eefc;
  font-size: 18px;
`;

const ImageStats = styled.div`
  display: flex;
  gap: 20px;
  justify-content: center;
  font-size: 14px;
  color: rgba(233, 238, 252, 0.7);
  margin-bottom: 15px;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const ImageCounter = styled.div`
  font-size: 14px;
  color: rgba(233, 238, 252, 0.7);
  margin-bottom: 10px;
`;

const ViewerToolbar = styled.div`
  display: flex;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(15, 20, 32, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
`;

const ToolbarButton = styled.button`
  background: ${({ $active }) => ($active ? 'rgba(98, 126, 255, 0.25)' : 'transparent')};
  color: #e9eefc;
  border: 1px solid ${({ $active }) => ($active ? 'rgba(120, 150, 255, 0.35)' : 'rgba(255, 255, 255, 0.08)')};
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
  justify-content: center;
`;

const ActionButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
  
  &:hover {
    background: #5a6fd8;
    transform: translateY(-2px);
  }
  
  &.secondary {
    background: #6c757d;
    
    &:hover {
      background: #5a6268;
    }
  }
`;

const ThumbnailStrip = styled.div`
  display: flex;
  gap: 10px;
  max-width: 100%;
  overflow-x: auto;
  padding: 10px 0;
  margin-top: 10px;
`;

const Thumbnail = styled.img`
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid ${props => props.active ? '#667eea' : 'transparent'};
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    transform: scale(1.05);
  }
`;

const FullScreenViewer = ({ 
  isOpen, 
  onClose, 
  images, 
  currentIndex, 
  onIndexChange 
}) => {
  const [showThumbnails, setShowThumbnails] = useState(false);
  const [imageViewerSettings, setImageViewerSettings] = useState({
    showBoundingBoxes: true,
    showLabels: true,
    showBlurred: false
  });

  // Image viewer control functions
  const toggleBoundingBoxes = useCallback(() => {
    setImageViewerSettings(prev => ({
      ...prev,
      showBoundingBoxes: !prev.showBoundingBoxes
    }));
  }, []);

  const toggleLabels = useCallback(() => {
    setImageViewerSettings(prev => ({
      ...prev,
      showLabels: !prev.showLabels
    }));
  }, []);

  const toggleBlurred = useCallback(() => {
    setImageViewerSettings(prev => ({
      ...prev,
      showBlurred: !prev.showBlurred
    }));
  }, []);


  // Handle keyboard navigation
  const handleKeyDown = useCallback((event) => {
    if (!isOpen) return;
    
    switch (event.key) {
      case 'Escape':
        onClose();
        break;
      case 'ArrowLeft':
        if (currentIndex > 0) {
          onIndexChange(currentIndex - 1);
        }
        break;
      case 'ArrowRight':
        if (currentIndex < images.length - 1) {
          onIndexChange(currentIndex + 1);
        }
        break;
      default:
        break;
    }
  }, [isOpen, currentIndex, images.length, onClose, onIndexChange]);

  // Add keyboard event listeners
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen || !images || images.length === 0) return null;

  const currentImage = images[currentIndex];
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < images.length - 1;

  const handlePrevious = () => {
    if (hasPrevious) {
      onIndexChange(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (hasNext) {
      onIndexChange(currentIndex + 1);
    }
  };

  const handleThumbnailClick = (index) => {
    onIndexChange(index);
  };

  const downloadOriginal = () => {
    if (currentImage.file) {
      const link = document.createElement('a');
      link.href = URL.createObjectURL(currentImage.file);
      link.download = currentImage.filename;
      link.click();
    }
  };

  const downloadBlurred = () => {
    if (currentImage.blurred?.blurred_image_path) {
      const filename = currentImage.blurred.blurred_image_path.split('/').pop();
      const link = document.createElement('a');
      link.href = `http://localhost:8000/download/${filename}`;
      link.download = `blurred_${currentImage.filename}`;
      link.click();
    }
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <CloseButton onClick={onClose}>
          ✕
        </CloseButton>

        <ImageContainer>
          <NavigationButton
            className="prev"
            onClick={handlePrevious}
            disabled={!hasPrevious}
            title="Previous image (←)"
          >
            ‹
          </NavigationButton>

          <div style={{ position: 'relative', maxWidth: '100%', maxHeight: '100%' }}>
            <ImageViewer
              image={currentImage}  // Pass the entire image object like in single image processing
              detections={currentImage.detection?.detections || []}  // Use the same structure as single image
              showBoundingBoxes={imageViewerSettings.showBoundingBoxes}
              showLabels={imageViewerSettings.showLabels}
              showBlurred={imageViewerSettings.showBlurred}
              onToggleBoundingBoxes={toggleBoundingBoxes}
              onToggleLabels={toggleLabels}
              onToggleBlurred={toggleBlurred}
              showControlsOverlay={false}
              enableZoomPan
              resetSignal={0}
            />
          </div>

          <NavigationButton
            className="next"
            onClick={handleNext}
            disabled={!hasNext}
            title="Next image (→)"
          >
            ›
          </NavigationButton>
        </ImageContainer>

        <ViewerToolbar>
          <ToolbarButton $active={imageViewerSettings.showBoundingBoxes} onClick={toggleBoundingBoxes}>
            Boxes
          </ToolbarButton>
          <ToolbarButton $active={imageViewerSettings.showLabels} onClick={toggleLabels}>
            Labels
          </ToolbarButton>
          {currentImage.blurred && (
            <ToolbarButton $active={imageViewerSettings.showBlurred} onClick={toggleBlurred}>
              {imageViewerSettings.showBlurred ? 'Blurred' : 'Original'}
            </ToolbarButton>
          )}
        </ViewerToolbar>

        <ImageInfo>
          <ImageTitle>{currentImage.filename}</ImageTitle>
          
          <ImageCounter>
            {currentIndex + 1} of {images.length}
          </ImageCounter>

          <ImageStats>
            <StatItem>
              <span>👤</span>
              <span>Faces: {currentImage.detection?.total_faces || 0}</span>
            </StatItem>
            <StatItem>
              <span>🚗</span>
              <span>Plates: {currentImage.detection?.total_license_plates || 0}</span>
            </StatItem>
            <StatItem>
              <span>📏</span>
              <span>{(currentImage.file.size / 1024).toFixed(1)} KB</span>
            </StatItem>
          </ImageStats>

          <ActionButtons>
            <ActionButton onClick={downloadOriginal}>
              📥 Download Original
            </ActionButton>
            {currentImage.blurred?.blurred_image_path && (
              <ActionButton onClick={downloadBlurred}>
                🔒 Download Blurred
              </ActionButton>
            )}
            <ActionButton 
              className="secondary"
              onClick={() => setShowThumbnails(!showThumbnails)}
            >
              {showThumbnails ? '🖼️ Hide Thumbnails' : '🖼️ Show Thumbnails'}
            </ActionButton>
          </ActionButtons>

          {showThumbnails && (
            <ThumbnailStrip>
              {images.map((image, index) => (
                <Thumbnail
                  key={index}
                  src={image.preview}
                  alt={image.filename}
                  active={index === currentIndex}
                  onClick={() => handleThumbnailClick(index)}
                  title={image.filename}
                />
              ))}
            </ThumbnailStrip>
          )}
        </ImageInfo>
      </ModalContent>
    </ModalOverlay>
  );
};

export default FullScreenViewer;
