/**
 * Main App Component
 * Unified Detection System - React Frontend
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import DetectionControls from './components/DetectionControls';
import ImageGallery from './components/ImageGallery';
import StatusBar from './components/StatusBar';
import FolderProcessor from './components/FolderProcessor';
import S3Processor from './components/S3Processor';
import apiService from './services/apiService';
import { FileUtils } from './utils/fileUtils';

import styled from 'styled-components';

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
`;

const Title = styled.h1`
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 700;
`;

const Subtitle = styled.p`
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
`;

const MainContent = styled.main`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
`;

const Section = styled.section`
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const SectionTitle = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
`;

function App() {
  // Navigation state
  const [currentMode, setCurrentMode] = useState('single'); // 'single' or 'folder'
  
  // State management
  const [files, setFiles] = useState([]);
  const [processedImages, setProcessedImages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [status, setStatus] = useState({ show: false, type: 'idle', title: '', message: '' });
  
  // Folder processing state
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [processedCount, setProcessedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  
  // Detection settings
  const [detectFace, setDetectFace] = useState(true);
  const [detectLicensePlate, setDetectLicensePlate] = useState(true);
  const [enableBlur, setEnableBlur] = useState(false);
  const [faceBlurStrength, setFaceBlurStrength] = useState(25);
  const [plateBlurStrength, setPlateBlurStrength] = useState(20);
  
  // Display settings
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [showBlurred, setShowBlurred] = useState(false);

  const checkApiHealth = useCallback(async () => {
    const result = await apiService.checkHealth();
    if (!result.success) {
      showStatus('error', 'API Connection Failed', 'Cannot connect to detection server. Please ensure the server is running.');
    }
  }, []);

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
  }, [checkApiHealth]);

  const showStatus = (type, title, message, show = true) => {
    setStatus({ show, type, title, message });
    if (show) {
      setTimeout(() => setStatus(prev => ({ ...prev, show: false })), 5000);
    }
  };

  const showToast = (message, type = 'info') => {
    toast[type](message, {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  };

  // File handling
  const handleFilesSelected = useCallback((selectedFiles) => {
    setFiles(prevFiles => [...prevFiles, ...selectedFiles]);
    showToast(`${selectedFiles.length} file(s) selected`, 'success');
  }, []);

  const handleClearFiles = () => {
    setFiles([]);
    setProcessedImages([]);
    showToast('All files cleared', 'info');
  };

  // Detection functions
  const processImage = async (file, options) => {
    try {
      // Detect objects
      const detectionResult = await apiService.detectObjects(
        file,
        options.detectFace,
        options.detectLicensePlate
      );

      if (!detectionResult.success) {
        throw new Error(detectionResult.error);
      }

      let blurResult = null;
      if (options.enableBlur) {
        blurResult = await apiService.blurObjects(
          file,
          options.detectFace,
          options.detectLicensePlate,
          options.faceBlurStrength,
          options.plateBlurStrength
        );

        if (!blurResult.success) {
          throw new Error(blurResult.error);
        }
      }

      // Create preview URL
      const previewUrl = FileUtils.createPreviewUrl(file);

      // Create processed image data
      const processedImage = {
        id: Date.now() + Math.random(),
        filename: file.name,
        file: file,
        preview: previewUrl,
        detection: detectionResult.data,
        blurred: blurResult?.data || null,
        timestamp: new Date().toISOString()
      };

      return processedImage;
    } catch (error) {
      console.error('Error processing image:', error);
      throw error;
    }
  };

  const handleDetect = async () => {
    if (files.length === 0) {
      showToast('Please select some images first', 'warning');
      return;
    }

    setIsProcessing(true);
    showStatus('processing', 'Processing Images', 'Detecting objects in images...', true);

    try {
      const options = {
        detectFace,
        detectLicensePlate,
        enableBlur: false
      };

      const results = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        showStatus('processing', 'Processing Images', `Processing ${i + 1}/${files.length}: ${file.name}`, true);
        
        try {
          const processedImage = await processImage(file, options);
          results.push(processedImage);
        } catch (error) {
          console.error(`Error processing ${file.name}:`, error);
          showToast(`Error processing ${file.name}: ${error.message}`, 'error');
        }
      }

      setProcessedImages(prev => [...prev, ...results]);
      showStatus('success', 'Detection Complete', `Successfully processed ${results.length} image(s)`);
      showToast(`Detection completed for ${results.length} image(s)`, 'success');
    } catch (error) {
      showStatus('error', 'Detection Failed', error.message);
      showToast('Detection failed: ' + error.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBlur = async () => {
    if (files.length === 0) {
      showToast('Please select some images first', 'warning');
      return;
    }

    setIsProcessing(true);
    showStatus('processing', 'Blurring Images', 'Applying privacy blur to images...', true);

    try {
      const options = {
        detectFace,
        detectLicensePlate,
        enableBlur: true,
        faceBlurStrength,
        plateBlurStrength
      };

      const results = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        showStatus('processing', 'Blurring Images', `Blurring ${i + 1}/${files.length}: ${file.name}`, true);
        
        try {
          const processedImage = await processImage(file, options);
          
          // If blur was applied, wait a bit to ensure file is written
          if (processedImage.blurred) {
            console.log(`Waiting for blur file to be written: ${processedImage.blurred.blurred_image_path}`);
            await new Promise(resolve => setTimeout(resolve, 2000));
          }
          
          results.push(processedImage);
        } catch (error) {
          console.error(`Error blurring ${file.name}:`, error);
          showToast(`Error blurring ${file.name}: ${error.message}`, 'error');
        }
      }

      setProcessedImages(prev => [...prev, ...results]);
      showStatus('success', 'Blur Complete', `Successfully blurred ${results.length} image(s)`);
      showToast(`Blur completed for ${results.length} image(s)`, 'success');
    } catch (error) {
      showStatus('error', 'Blur Failed', error.message);
      showToast('Blur failed: ' + error.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  // Image gallery functions
  const handleDownload = async (image, type) => {
    if (isDownloading) {
      showToast('Download already in progress...', 'warning');
      return;
    }

    setIsDownloading(true);
    try {
      if (type === 'original') {
        // Download original file
        FileUtils.downloadFile(image.file, image.filename);
        showToast('Download started', 'success');
      } else if (type === 'blurred' && image.blurred) {
        // Download blurred image from server with retry mechanism
        const filename = image.blurred.blurred_image_path.split('/').pop();
        
        showToast('Preparing blurred image download...', 'info');
        
        // Add a small delay to ensure the file is fully written
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const result = await downloadWithRetry(filename, 3);
        if (result.success) {
          // Validate the download data before using it
          if (!result.data || !result.data.blob) {
            throw new Error('Invalid download data received');
          }
          
          FileUtils.downloadFile(result.data.blob, `blurred_${image.filename}`);
          showToast(`Download started (${Math.round(result.data.size/1024)}KB)`, 'success');
        } else {
          throw new Error(result.error);
        }
      }
    } catch (error) {
      console.error('Download error:', error);
      showToast('Download failed: ' + error.message, 'error');
    } finally {
      setIsDownloading(false);
    }
  };

  // Helper function to retry download with exponential backoff
  const downloadWithRetry = async (filename, maxRetries = 3) => {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Download attempt ${attempt}/${maxRetries} for ${filename}`);
        const result = await apiService.downloadImage(filename);
        
        if (result.success) {
          return result;
        }
        
        if (attempt === maxRetries) {
          return result; // Return the last error
        }
        
        // Wait before retry with exponential backoff
        const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
        console.log(`Waiting ${delay}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        
      } catch (error) {
        console.error(`Download attempt ${attempt} failed:`, error);
        
        if (attempt === maxRetries) {
          return { success: false, error: error.message };
        }
        
        // Wait before retry
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  };

  const handleDeleteImage = (imageToDelete) => {
    setProcessedImages(prev => {
      const updated = prev.filter(img => img.id !== imageToDelete.id);
      FileUtils.revokePreviewUrl(imageToDelete.preview);
      return updated;
    });
    showToast('Image removed', 'info');
  };

  // Folder processing callbacks
  const handleProcessingStart = useCallback((total) => {
    setTotalCount(total);
    setProcessedCount(0);
    setProcessingStatus('processing');
    setIsProcessing(true);
  }, []);

  const handleProcessingComplete = useCallback((completed) => {
    setProcessedCount(completed);
    setProcessingStatus('success');
    setIsProcessing(false);
  }, []);

  const handleProgressUpdate = useCallback((current, total) => {
    setProcessedCount(current);
    setTotalCount(total);
  }, []);

  const handleModeChange = useCallback((mode) => {
    setCurrentMode(mode);
    if (mode === 'single') {
      setProcessedImages([]);
      setFiles([]);
    }
  }, []);

  return (
    <AppContainer>
      <Navbar
        currentMode={currentMode}
        onModeChange={handleModeChange}
        isProcessing={isProcessing}
        processingStatus={processingStatus}
        processedCount={processedCount}
        totalCount={totalCount}
      />
      
      {currentMode === 'single' && (
        <>
          <Header>
            <Title>🔍 Single Image Processing</Title>
            <Subtitle>Face & License Plate Detection with Privacy Protection</Subtitle>
          </Header>

      <StatusBar
        status={status.type}
        title={status.title}
        message={status.message}
        show={status.show}
        onClose={() => setStatus(prev => ({ ...prev, show: false }))}
      />

      <MainContent>
        <LeftPanel>
          <Section>
            <SectionTitle>📁 Upload Images</SectionTitle>
            <FileUpload
              onFilesSelected={handleFilesSelected}
              maxFiles={10}
            />
          </Section>

          <Section>
            <DetectionControls
              detectFace={detectFace}
              detectLicensePlate={detectLicensePlate}
              enableBlur={enableBlur}
              faceBlurStrength={faceBlurStrength}
              plateBlurStrength={plateBlurStrength}
              showBoundingBoxes={showBoundingBoxes}
              showLabels={showLabels}
              showBlurred={showBlurred}
              onDetectFaceChange={setDetectFace}
              onDetectLicensePlateChange={setDetectLicensePlate}
              onEnableBlurChange={setEnableBlur}
              onFaceBlurStrengthChange={setFaceBlurStrength}
              onPlateBlurStrengthChange={setPlateBlurStrength}
              onShowBoundingBoxesChange={() => setShowBoundingBoxes(!showBoundingBoxes)}
              onShowLabelsChange={() => setShowLabels(!showLabels)}
              onShowBlurredChange={() => setShowBlurred(!showBlurred)}
              onDetect={handleDetect}
              onBlur={handleBlur}
              onClear={handleClearFiles}
              isProcessing={isProcessing}
              hasFiles={files.length > 0}
            />
          </Section>
        </LeftPanel>

        <RightPanel>
          <Section>
            <SectionTitle>🖼️ Processed Images</SectionTitle>
            <ImageGallery
              images={processedImages}
              onDownload={handleDownload}
              onDelete={handleDeleteImage}
              isDownloading={isDownloading}
              showBoundingBoxes={showBoundingBoxes}
              showLabels={showLabels}
              showBlurred={showBlurred}
              onToggleBoundingBoxes={() => setShowBoundingBoxes(!showBoundingBoxes)}
              onToggleLabels={() => setShowLabels(!showLabels)}
              onToggleBlurred={() => setShowBlurred(!showBlurred)}
            />
          </Section>
        </RightPanel>
      </MainContent>
        </>
      )}

      {currentMode === 'folder' && (
        <FolderProcessor
          onProcessingStart={handleProcessingStart}
          onProcessingComplete={handleProcessingComplete}
          onProgressUpdate={handleProgressUpdate}
        />
      )}

      {currentMode === 's3' && (
        <S3Processor
          onProcessingStart={handleProcessingStart}
          onProcessingComplete={handleProcessingComplete}
          onProgressUpdate={handleProgressUpdate}
        />
      )}

      <ToastContainer />
    </AppContainer>
  );
}

export default App;
