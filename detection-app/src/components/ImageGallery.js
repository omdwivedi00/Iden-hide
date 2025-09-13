/**
 * Image Gallery Component
 * Displays processed images with results and bounding box controls
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import ImageViewer from './ImageViewer';

const GalleryContainer = styled.div`
  margin-top: 20px;
`;

const GalleryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ImageCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled.div`
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
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

      {selectedImage && (
        <Modal onClick={closeModal}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={closeModal}>×</CloseButton>
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
          </ModalContent>
        </Modal>
      )}
    </GalleryContainer>
  );
};

export default ImageGallery;