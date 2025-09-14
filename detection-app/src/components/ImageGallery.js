/**
 * Image Gallery Component
 * Displays processed images with results and bounding box controls
 */

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import styled from 'styled-components';
import { mediaQueries, layoutHelpers } from '../styles/mediaKit';
import ImageViewer from './ImageViewer';

const GalleryContainer = styled.div`
  margin-top: 20px;
`;

const GalleryGrid = styled.div`
  ${layoutHelpers.grid({ xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 })}
  margin-top: 20px;
  
  ${mediaQueries.sm} {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  ${mediaQueries.md} {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
  
  ${mediaQueries.lg} {
    grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  }
  
  ${mediaQueries.xl} {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
  
  ${mediaQueries.xxl} {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
`;

const ImageCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    border-color: #007bff;
    
    .click-indicator {
      opacity: 1;
    }
  }
`;

const ImageContainer = styled.div`
  position: relative;
  width: 100%;
  background: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 250px;
`;

const ImageInfo = styled.div`
  padding: 15px;
`;

const ImageTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ImageStats = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
  gap: 10px;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const DetectionList = styled.div`
  margin-top: 10px;
  max-height: 120px;
  overflow-y: auto;
`;

const DetectionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
  font-size: 12px;

  &:last-child {
    border-bottom: none;
  }
`;

const DetectionLabel = styled.span`
  font-weight: 500;
  color: ${props => props.type === 'face' ? '#28a745' : '#dc3545'};
`;

const Confidence = styled.span`
  color: #666;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 5px;
  margin-top: 10px;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;

  &:hover {
    background: #f8f9fa;
  }

  &.primary {
    background: #007bff;
    color: white;
    border-color: #007bff;

    &:hover {
      background: #0056b3;
    }
  }

  &.danger {
    background: #dc3545;
    color: white;
    border-color: #dc3545;

    &:hover {
      background: #c82333;
    }
  }
`;

const ViewControls = styled.div`
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
`;

const ViewButton = styled.button`
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: ${props => props.active ? '#007bff' : 'white'};
  color: ${props => props.active ? 'white' : '#333'};
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f8f9fa'};
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  backdrop-filter: blur(5px);
`;

const ModalContent = styled.div`
  width: 95vw;
  height: 95vh;
  max-width: 95vw;
  max-height: 95vh;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 18px;
  z-index: 10;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
`;

const ImageGallery = ({ images, onDownload, onDelete, isDownloading, showBoundingBoxes, showLabels, showBlurred, onToggleBoundingBoxes, onToggleLabels, onToggleBlurred }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const openModal = (image) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && selectedImage) {
        closeModal();
      }
    };

    if (selectedImage) {
      document.addEventListener('keydown', handleKeyDown);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [selectedImage]);

  const handleDownload = (image, type) => {
    if (onDownload) {
      onDownload(image, type);
    }
  };

  const handleDelete = (image) => {
    if (onDelete) {
      onDelete(image);
    }
  };

  const toggleBlurred = () => {
    if (onToggleBlurred) {
      onToggleBlurred();
    }
  };

  if (images.length === 0) {
    return (
      <GalleryContainer>
        <EmptyState>
          <h3>No images processed yet</h3>
          <p>Upload some images and run detection to see results here.</p>
        </EmptyState>
      </GalleryContainer>
    );
  }

  return (
    <GalleryContainer>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3>Processed Images ({images.length})</h3>
        
        <ViewControls>
          <ViewButton
            active={viewMode === 'grid'}
            onClick={() => setViewMode('grid')}
          >
            Grid View
          </ViewButton>
          <ViewButton
            active={viewMode === 'list'}
            onClick={() => setViewMode('list')}
          >
            List View
          </ViewButton>
        </ViewControls>
      </div>
      
      <GalleryGrid style={{ gridTemplateColumns: viewMode === 'list' ? '1fr' : 'repeat(auto-fill, minmax(400px, 1fr))' }}>
        {images.map((image, index) => (
          <ImageCard key={index}>
            <ImageContainer onClick={() => openModal(image)}>
            <ImageViewer
              image={image}
              detections={image.detection?.detections || []}
              showBoundingBoxes={showBoundingBoxes}
              showLabels={showLabels}
              showBlurred={showBlurred}
              onToggleBoundingBoxes={onToggleBoundingBoxes}
              onToggleLabels={onToggleLabels}
              onToggleBlurred={toggleBlurred}
            />
            {/* Click indicator */}
            <div style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              background: 'rgba(0,0,0,0.7)',
              color: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              opacity: 0,
              transition: 'opacity 0.3s ease',
              pointerEvents: 'none'
            }} className="click-indicator">
              🔍 Click to view full screen
            </div>
            </ImageContainer>
            
            <ImageInfo>
              <ImageTitle>
                {image.filename}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '12px', color: '#666' }}>
                    {new Date(image.timestamp).toLocaleTimeString()}
                  </span>
                  {image.blurred && (
                    <span style={{ 
                      fontSize: '10px', 
                      background: '#28a745', 
                      color: 'white', 
                      padding: '2px 6px', 
                      borderRadius: '3px' 
                    }}>
                      🔒 Blurred Available
                    </span>
                  )}
                </div>
              </ImageTitle>
              
              <ImageStats>
                <StatItem>
                  <span>👤</span>
                  <span>Faces: {image.detection?.total_faces || 0}</span>
                </StatItem>
                <StatItem>
                  <span>🚗</span>
                  <span>Plates: {image.detection?.total_license_plates || 0}</span>
                </StatItem>
                <StatItem>
                  <span>⏱️</span>
                  <span>{image.detection?.processing_time_ms || 0}ms</span>
                </StatItem>
              </ImageStats>
              
              {image.detection?.detections && image.detection.detections.length > 0 && (
                <DetectionList>
                  {image.detection.detections.map((detection, idx) => (
                    <DetectionItem key={idx}>
                      <DetectionLabel type={detection.label}>
                        {detection.label}
                      </DetectionLabel>
                      <Confidence>
                        {(detection.confidence * 100).toFixed(1)}%
                      </Confidence>
                    </DetectionItem>
                  ))}
                </DetectionList>
              )}
              
              <ActionButtons>
                <ActionButton 
                  className="primary"
                  disabled={isDownloading}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDownload(image, 'original');
                  }}
                >
                  {isDownloading ? '⏳' : '📥'} Download Original
                </ActionButton>
                
                {image.blurred && (
                  <ActionButton 
                    className="primary"
                    disabled={isDownloading}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(image, 'blurred');
                    }}
                  >
                    {isDownloading ? '⏳' : '🔒'} Download Blurred
                  </ActionButton>
                )}
                
                <ActionButton 
                  className="danger"
                  disabled={isDownloading}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(image);
                  }}
                >
                  🗑️ Delete
                </ActionButton>
              </ActionButtons>
            </ImageInfo>
          </ImageCard>
        ))}
      </GalleryGrid>

      {selectedImage && createPortal(
        <Modal onClick={closeModal}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={closeModal}>×</CloseButton>
            
            {/* Image Header */}
            <div style={{ 
              padding: '15px 20px', 
              borderBottom: '1px solid #eee',
              background: '#f8f9fa',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h3 style={{ margin: '0 0 5px 0', fontSize: '18px', color: '#333' }}>
                  {selectedImage.filename}
                </h3>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  <span>👤 Faces: {selectedImage.detection?.total_faces || 0}</span>
                  <span style={{ margin: '0 15px' }}>🚗 Plates: {selectedImage.detection?.total_license_plates || 0}</span>
                  <span>⏱️ {selectedImage.detection?.processing_time_ms || 0}ms</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <ActionButton 
                  className="primary"
                  disabled={isDownloading}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDownload(selectedImage, 'original');
                  }}
                >
                  {isDownloading ? '⏳' : '📥'} Original
                </ActionButton>
                {selectedImage.blurred && (
                  <ActionButton 
                    className="primary"
                    disabled={isDownloading}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(selectedImage, 'blurred');
                    }}
                  >
                    {isDownloading ? '⏳' : '🔒'} Blurred
                  </ActionButton>
                )}
              </div>
            </div>
            
            {/* Image Viewer */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
              <ImageViewer
                image={selectedImage}
                detections={selectedImage.detection?.detections || []}
                isDownloading={isDownloading}
                showBoundingBoxes={showBoundingBoxes}
                showLabels={showLabels}
                showBlurred={showBlurred}
                onToggleBoundingBoxes={onToggleBoundingBoxes}
                onToggleLabels={onToggleLabels}
                onToggleBlurred={toggleBlurred}
              />
            </div>
            
            {/* Image Footer with Controls */}
            <div style={{ 
              padding: '15px 20px', 
              borderTop: '1px solid #eee',
              background: '#f8f9fa',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: '#666' }}>Controls:</span>
                <ActionButton 
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleBoundingBoxes();
                  }}
                  style={{ background: showBoundingBoxes ? '#007bff' : '#f8f9fa', color: showBoundingBoxes ? 'white' : '#333' }}
                >
                  📦 Bounding Boxes
                </ActionButton>
                <ActionButton 
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleLabels();
                  }}
                  style={{ background: showLabels ? '#007bff' : '#f8f9fa', color: showLabels ? 'white' : '#333' }}
                >
                  🏷️ Labels
                </ActionButton>
                <ActionButton 
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleBlurred();
                  }}
                  style={{ background: showBlurred ? '#007bff' : '#f8f9fa', color: showBlurred ? 'white' : '#333' }}
                >
                  🔒 Blurred View
                </ActionButton>
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>
                Click outside to close • ESC to close
              </div>
            </div>
          </ModalContent>
        </Modal>,
        document.body
      )}
    </GalleryContainer>
  );
};

export default ImageGallery;