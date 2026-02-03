/**
 * Main App Component
 * Unified Detection System - React Frontend
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import FileUpload from './components/FileUpload';
import DetectionControls from './components/DetectionControls';
import ImageGallery from './components/ImageGallery';
import StatusBar from './components/StatusBar';
import FolderProcessor from './components/FolderProcessor';
import S3Processor from './components/S3Processor';
import apiService from './services/apiService';
import { FileUtils } from './utils/fileUtils';

import styled from 'styled-components';
import { mediaQueries } from './styles/mediaKit';

const AppContainer = styled.div`
  font-family: 'Space Grotesk', 'Manrope', 'Inter', system-ui, sans-serif;
  background: radial-gradient(1200px 800px at 20% -10%, rgba(72, 98, 255, 0.18), transparent),
    radial-gradient(800px 600px at 90% 10%, rgba(0, 201, 255, 0.16), transparent),
    #0b0f1a;
  min-height: 100vh;
  width: 100%;
  max-width: 100vw;
  padding: 0.75rem;
  box-sizing: border-box;
  overflow-x: hidden;
  color: #e9eefc;
`;

const Shell = styled.div`
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 0.75rem;
  min-height: calc(100vh - 1.5rem);

  ${mediaQueries.md} {
    grid-template-columns: 240px 1fr;
  }
`;

const Sidebar = styled.aside`
  background: rgba(18, 24, 40, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(18px);
`;

const SidebarHeader = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Brand = styled.div`
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
`;

const BrandSub = styled.div`
  font-size: 0.75rem;
  opacity: 0.7;
`;

const Nav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const NavItem = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: ${({ $active }) => ($active ? 'rgba(98, 126, 255, 0.18)' : 'transparent')};
  color: ${({ $active }) => ($active ? '#e9eefc' : 'rgba(233, 238, 252, 0.7)')};
  border: 1px solid ${({ $active }) => ($active ? 'rgba(120, 150, 255, 0.35)' : 'transparent')};
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  text-align: left;

  &:hover {
    background: rgba(98, 126, 255, 0.12);
  }
`;

const SidebarFooter = styled.div`
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 0.75rem;
  opacity: 0.7;
`;

const StatusPill = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0, 255, 179, 0.12);
  color: #8dffd8;
  font-weight: 600;
  font-size: 0.75rem;
`;

const Content = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;

  ${mediaQueries.lg} {
    grid-template-columns: 1fr 360px;
  }
`;

const MainCanvas = styled.main`
  background: rgba(15, 20, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(16px);
`;

const CanvasHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
`;

const CanvasTitle = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const CanvasTitleMain = styled.div`
  font-size: 1.1rem;
  font-weight: 600;
`;

const CanvasTitleSub = styled.div`
  font-size: 0.85rem;
  opacity: 0.7;
`;

const CanvasBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 320px;
`;

const ViewerToolbar = styled.div`
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
`;

const ToolbarButton = styled.button`
  background: ${({ $active }) => ($active ? 'rgba(98, 126, 255, 0.25)' : 'rgba(12, 16, 26, 0.6)')};
  color: #e9eefc;
  border: 1px solid ${({ $active }) => ($active ? 'rgba(120, 150, 255, 0.35)' : 'rgba(255, 255, 255, 0.08)')};
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
`;

const ContextPanel = styled.aside`
  background: rgba(18, 24, 40, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(16px);
`;

const PanelSection = styled.section`
  background: rgba(12, 16, 26, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
`;

const PanelTitle = styled.h3`
  margin: 0 0 10px 0;
  font-size: 0.9rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  opacity: 0.7;
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
  const [apiHealthy, setApiHealthy] = useState(true);
  
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
  const [resetViewerSignal, setResetViewerSignal] = useState(0);

  const checkApiHealth = useCallback(async () => {
    const result = await apiService.checkHealth();
    if (!result.success) {
      setApiHealthy(false);
      showStatus('error', 'API Connection Failed', 'Cannot connect to detection server. Please ensure the server is running.');
    } else {
      setApiHealthy(true);
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
    // For single image processing, replace files but keep previous results
    if (currentMode === 'single') {
      setFiles(selectedFiles);
      // Don't clear processedImages - keep previous results
      showToast(`${selectedFiles.length} file(s) selected`, 'success');
    } else {
      // For other modes, append files
      setFiles(prevFiles => [...prevFiles, ...selectedFiles]);
      showToast(`${selectedFiles.length} file(s) added`, 'success');
    }
  }, [currentMode]);

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

      // Always append results to preserve previous ones
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

      // Always append results to preserve previous ones
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
      <Shell>
        <Sidebar>
          <SidebarHeader>
            <Brand>Iden‑Hide</Brand>
            <BrandSub>AI Privacy Studio</BrandSub>
          </SidebarHeader>
          <Nav>
            <NavItem $active={currentMode === 'single'} onClick={() => handleModeChange('single')}>
              Single Image
            </NavItem>
            <NavItem $active={currentMode === 'folder'} onClick={() => handleModeChange('folder')}>
              Batch (Local)
            </NavItem>
            <NavItem $active={currentMode === 's3'} onClick={() => handleModeChange('s3')}>
              Batch (S3)
            </NavItem>
            <NavItem $active={currentMode === 'history'} onClick={() => handleModeChange('history')}>
              History / Outputs
            </NavItem>
            <NavItem $active={currentMode === 'settings'} onClick={() => handleModeChange('settings')}>
              Settings
            </NavItem>
          </Nav>
          <SidebarFooter>
            <StatusPill>{apiHealthy ? 'API Connected' : 'API Offline'}</StatusPill>
            <div>Device: CPU</div>
          </SidebarFooter>
        </Sidebar>

        <Content>
          <MainCanvas>
            <CanvasHeader>
              <CanvasTitle>
                <CanvasTitleMain>
                  {currentMode === 'single' && 'Single Image Workspace'}
                  {currentMode === 'folder' && 'Batch Processing (Local)'}
                  {currentMode === 's3' && 'Batch Processing (S3)'}
                  {currentMode === 'history' && 'History & Outputs'}
                  {currentMode === 'settings' && 'System Settings'}
                </CanvasTitleMain>
                <CanvasTitleSub>
                  {currentMode === 'single' && `${processedImages.length} results • ${files.length} selected`}
                  {currentMode === 'folder' && `${processedCount}/${totalCount || 0} processed`}
                  {currentMode === 's3' && `${processedCount}/${totalCount || 0} processed`}
                  {currentMode === 'history' && 'Recent processed outputs'}
                  {currentMode === 'settings' && 'Configure detection defaults'}
                </CanvasTitleSub>
              </CanvasTitle>
            </CanvasHeader>

            {currentMode === 'single' && (
              <ViewerToolbar>
                <ToolbarButton $active={showBoundingBoxes} onClick={() => setShowBoundingBoxes(!showBoundingBoxes)}>
                  Boxes
                </ToolbarButton>
                <ToolbarButton
                  $active={showLabels}
                  onClick={() => setShowLabels(!showLabels)}
                  disabled={!showBoundingBoxes}
                >
                  Labels
                </ToolbarButton>
                {processedImages.some(img => img.blurred) && (
                  <ToolbarButton $active={showBlurred} onClick={() => setShowBlurred(!showBlurred)}>
                    {showBlurred ? 'Blurred' : 'Original'}
                  </ToolbarButton>
                )}
                <ToolbarButton onClick={() => setResetViewerSignal(prev => prev + 1)}>
                  Reset View
                </ToolbarButton>
              </ViewerToolbar>
            )}

            {currentMode === 'single' && (
              <StatusBar
                status={status.type}
                title={status.title}
                message={status.message}
                show={status.show}
                onClose={() => setStatus(prev => ({ ...prev, show: false }))}
              />
            )}

            <CanvasBody>
              {currentMode === 'single' && (
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
                  showHeader={false}
                  compact
                  showViewerControls={false}
                  enableZoomPan
                  resetSignal={resetViewerSignal}
                />
              )}

              {currentMode === 'folder' && (
                <FolderProcessor
                  onProcessingStart={handleProcessingStart}
                  onProcessingComplete={handleProcessingComplete}
                  onProgressUpdate={handleProgressUpdate}
                  detectFace={detectFace}
                  detectLicensePlate={detectLicensePlate}
                  enableBlur={enableBlur}
                  faceBlurStrength={faceBlurStrength}
                  plateBlurStrength={plateBlurStrength}
                  embedded
                />
              )}

              {currentMode === 's3' && (
                <S3Processor
                  onProcessingStart={handleProcessingStart}
                  onProcessingComplete={handleProcessingComplete}
                  onProgressUpdate={handleProgressUpdate}
                  detectFace={detectFace}
                  detectLicensePlate={detectLicensePlate}
                  faceBlurStrength={faceBlurStrength}
                  plateBlurStrength={plateBlurStrength}
                  embedded
                  showDetectionControls={false}
                />
              )}

              {currentMode === 'history' && (
                <div>History view is coming next. Your output images are available on the server.</div>
              )}

              {currentMode === 'settings' && (
                <div>Settings view is coming next. Configure defaults and model selection here.</div>
              )}
            </CanvasBody>
          </MainCanvas>

          <ContextPanel>
            {currentMode === 'single' && (
              <>
                <PanelSection>
                  <PanelTitle>Upload</PanelTitle>
                  <FileUpload onFilesSelected={handleFilesSelected} maxFiles={10} />
                </PanelSection>
                <PanelSection>
                  <PanelTitle>Detection & Blur</PanelTitle>
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
                    showDisplayOptions={false}
                  />
                </PanelSection>
              </>
            )}

            {currentMode !== 'single' && (
              <>
                <PanelSection>
                  <PanelTitle>Configuration</PanelTitle>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px', color: 'rgba(233, 238, 252, 0.75)' }}>
                    <label>
                      <input type="checkbox" checked={detectFace} onChange={() => setDetectFace(!detectFace)} />
                      <span style={{ marginLeft: '8px' }}>Detect faces</span>
                    </label>
                    <label>
                      <input type="checkbox" checked={detectLicensePlate} onChange={() => setDetectLicensePlate(!detectLicensePlate)} />
                      <span style={{ marginLeft: '8px' }}>Detect plates</span>
                    </label>
                    <label>
                      <input type="checkbox" checked={enableBlur} onChange={() => setEnableBlur(!enableBlur)} />
                      <span style={{ marginLeft: '8px' }}>Enable blur</span>
                    </label>
                    {enableBlur && (
                      <>
                        <label>
                          Face blur strength: {faceBlurStrength}
                          <input
                            type="range"
                            min="1"
                            max="100"
                            value={faceBlurStrength}
                            onChange={(e) => setFaceBlurStrength(parseInt(e.target.value))}
                            style={{ width: '100%' }}
                          />
                        </label>
                        <label>
                          Plate blur strength: {plateBlurStrength}
                          <input
                            type="range"
                            min="1"
                            max="100"
                            value={plateBlurStrength}
                            onChange={(e) => setPlateBlurStrength(parseInt(e.target.value))}
                            style={{ width: '100%' }}
                          />
                        </label>
                      </>
                    )}
                  </div>
                </PanelSection>

                <PanelSection>
                  <PanelTitle>Job Status</PanelTitle>
                  <div>Status: {processingStatus}</div>
                  <div>Processed: {processedCount}</div>
                  <div>Total: {totalCount}</div>
                </PanelSection>
              </>
            )}
          </ContextPanel>
        </Content>
      </Shell>

      <ToastContainer />
    </AppContainer>
  );
}

export default App;
