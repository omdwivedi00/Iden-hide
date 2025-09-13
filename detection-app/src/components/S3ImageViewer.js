import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { s3Service } from '../services/s3Service';

const ViewerOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
`;

const ViewerContainer = styled.div`
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ImageContainer = styled.div`
  position: relative;
  max-width: 100%;
  max-height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
`;

const Image = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(0, 0, 0, 0.8);
  padding: 15px 25px;
  border-radius: 25px;
  backdrop-filter: blur(10px);
`;

const Button = styled.button`
  background: ${props => props.variant === 'primary' ? '#007bff' : 'transparent'};
  color: white;
  border: 2px solid ${props => props.variant === 'primary' ? '#007bff' : 'rgba(255, 255, 255, 0.3)'};
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;

  &:hover {
    background: ${props => props.variant === 'primary' ? '#0056b3' : 'rgba(255, 255, 255, 0.1)'};
    border-color: ${props => props.variant === 'primary' ? '#0056b3' : 'rgba(255, 255, 255, 0.5)'};
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: -50px;
  right: 0;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 10px 15px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
    transform: scale(1.1);
  }
`;

const ImageInfo = styled.div`
  color: white;
  text-align: center;
  margin-bottom: 15px;
  font-size: 14px;
  opacity: 0.8;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  gap: 10px;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  text-align: center;
  padding: 20px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 8px;
  margin: 20px 0;
`;

const S3ImageViewer = ({ 
  isOpen, 
  onClose, 
  images, 
  currentIndex, 
  onIndexChange,
  credentials 
}) => {
  const [currentImage, setCurrentImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [presignedUrl, setPresignedUrl] = useState(null);

  const loadImage = useCallback(async (imageData) => {
    if (!imageData || !credentials) return;

    setLoading(true);
    setError(null);
    setPresignedUrl(null);

    try {
      // Get the S3 URI from the image data
      const s3Uri = imageData.output_s3_url || imageData.output_s3_path;
      
      if (!s3Uri) {
        throw new Error('No S3 URI found for this image');
      }

      console.log('Loading S3 image:', s3Uri);

      // Get presigned URL
      const result = await s3Service.viewS3Image(credentials, s3Uri, 300);
      
      if (result.success) {
        setPresignedUrl(result.data.presigned_url);
        setCurrentImage(imageData);
        console.log('Presigned URL generated:', result.data.presigned_url);
      } else {
        throw new Error(result.error || 'Failed to generate presigned URL');
      }
    } catch (err) {
      console.error('Error loading image:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [credentials]);

  // Load image when component opens or index changes
  useEffect(() => {
    if (isOpen && images && images.length > 0 && currentIndex >= 0 && currentIndex < images.length) {
      loadImage(images[currentIndex]);
    }
  }, [isOpen, currentIndex, images, loadImage]);

  const handlePrevious = () => {
    if (currentIndex > 0) {
      onIndexChange(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < images.length - 1) {
      onIndexChange(currentIndex + 1);
    }
  };

  const handleKeyDown = (e) => {
    if (!isOpen) return;
    
    switch (e.key) {
      case 'Escape':
        onClose();
        break;
      case 'ArrowLeft':
        handlePrevious();
        break;
      case 'ArrowRight':
        handleNext();
        break;
      default:
        break;
    }
  };

  // Add keyboard event listeners
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, currentIndex, images]);

  if (!isOpen || !images || images.length === 0) {
    return null;
  }

  const currentImageData = images[currentIndex];
  const filename = currentImageData?.original_filename || 
                  currentImageData?.input_s3_path?.split('/').pop() || 
                  'Unknown';

  return (
    <ViewerOverlay onClick={(e) => e.target === e.currentTarget && onClose()}>
      <ViewerContainer>
        <CloseButton onClick={onClose} title="Close (Esc)">
          ✕
        </CloseButton>

        <ImageInfo>
          {filename} ({currentIndex + 1} of {images.length})
        </ImageInfo>

        <ImageContainer>
          {loading && (
            <LoadingSpinner>
              <div>⏳</div>
              <div>Loading image...</div>
            </LoadingSpinner>
          )}

          {error && (
            <ErrorMessage>
              <div>❌ Error loading image</div>
              <div>{error}</div>
            </ErrorMessage>
          )}

          {presignedUrl && !loading && !error && (
            <Image 
              src={presignedUrl} 
              alt={filename}
              onError={() => setError('Failed to load image from S3')}
            />
          )}
        </ImageContainer>

        <Controls>
          <Button 
            onClick={handlePrevious}
            disabled={currentIndex <= 0 || loading}
          >
            ← Previous
          </Button>
          
          <Button 
            variant="primary"
            onClick={handleNext}
            disabled={currentIndex >= images.length - 1 || loading}
          >
            Next →
          </Button>
        </Controls>
      </ViewerContainer>
    </ViewerOverlay>
  );
};

export default S3ImageViewer;
