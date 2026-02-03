/**
 * Folder Processor Component
 * Handles batch processing of images from a folder
 */

import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { mediaQueries, layoutHelpers } from '../styles/mediaKit';
import JSZip from 'jszip';
import apiService from '../services/apiService';
import FullScreenViewer from './FullScreenViewer';
import ImageViewer from './ImageViewer';

const FolderContainer = styled.div`
  ${layoutHelpers.container('xxl')}
  background: transparent;
  min-height: 100%;
  padding: 0;
`;

const Section = styled.div`
  background: rgba(12, 16, 26, 0.6);
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
`;

const SectionTitle = styled.h2`
  margin: 0 0 16px 0;
  color: #e9eefc;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const FolderInput = styled.div`
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(8, 12, 22, 0.5);
  
  &:hover {
    border-color: rgba(98, 126, 255, 0.6);
    background: rgba(98, 126, 255, 0.08);
  }
  
  &.has-files {
    border-color: rgba(39, 201, 124, 0.6);
    background: rgba(39, 201, 124, 0.08);
  }
`;

const FolderInputText = styled.div`
  color: rgba(233, 238, 252, 0.85);
  font-size: 15px;
  margin-bottom: 8px;
`;

const FolderInputSubtext = styled.div`
  color: rgba(233, 238, 252, 0.5);
  font-size: 13px;
`;

const FileList = styled.div`
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  
  &:last-child {
    border-bottom: none;
  }
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
`;

const FileIcon = styled.span`
  font-size: 18px;
`;

const FileName = styled.span`
  color: #e9eefc;
  font-size: 14px;
`;

const FileSize = styled.span`
  color: rgba(233, 238, 252, 0.6);
  font-size: 12px;
`;

const RemoveButton = styled.button`
  background: #ff5252;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  
  &:hover {
    background: #f44336;
  }
`;

const Controls = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
  margin-top: 20px;
  flex-wrap: wrap;
`;

const ControlButton = styled.button`
  background: ${props => {
    if (props.variant === 'primary') return '#667eea';
    if (props.variant === 'success') return '#4caf50';
    if (props.variant === 'danger') return '#f44336';
    return '#6c757d';
  }};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ProgressContainer = styled.div`
  margin-top: 20px;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #666;
`;

const ResultsGrid = styled.div`
  ${layoutHelpers.grid({ xs: 1, sm: 2, md: 3, lg: 4, xl: 5, xxl: 6 })}
  margin-top: 20px;
  
  ${mediaQueries.sm} {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  ${mediaQueries.md} {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  
  ${mediaQueries.lg} {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
  
  ${mediaQueries.xl} {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  ${mediaQueries.xxl} {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
`;

const ResultCard = styled.div`
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background: white;
`;

const ResultImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.02);
  }
`;

const ResultInfo = styled.div`
  padding: 15px;
`;

const ResultTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
`;

const ResultStats = styled.div`
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
`;

const ResultActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e0e0e0;
    transform: translateY(-1px);
  }
  
  &.primary {
    background: #667eea;
    color: white;
    border-color: #667eea;
    
    &:hover {
      background: #5a6fd8;
    }
  }
`;

const FolderProcessor = ({ 
  onProcessingStart, 
  onProcessingComplete, 
  onProgressUpdate,
  detectFace = true,
  detectLicensePlate = true,
  enableBlur = true,
  faceBlurStrength = 25,
  plateBlurStrength = 20,
  embedded = true
}) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [results, setResults] = useState([]);
  const [isCreatingZip, setIsCreatingZip] = useState(false);
  
  // Full-screen viewer state
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [viewerIndex, setViewerIndex] = useState(0);
  
  // Image viewer settings for each result
  const [displaySettings, setDisplaySettings] = useState({
    showBoundingBoxes: true,
    showLabels: true,
    showBlurred: false
  });
  
  // Parallel processing settings
  const [useParallelProcessing, setUseParallelProcessing] = useState(false);
  const [maxWorkers, setMaxWorkers] = useState(4);
  const [showParallelWarning, setShowParallelWarning] = useState(false);

  const handleFolderSelect = useCallback((event) => {
    const files = Array.from(event.target.files);
    const imageFiles = files.filter(file => 
      file.type.startsWith('image/') && 
      ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(file.name.split('.').pop().toLowerCase())
    );
    
    setSelectedFiles(imageFiles);
    setResults([]);
    setProgress(0);
    
    if (imageFiles.length > 0) {
      toast.success(`${imageFiles.length} image(s) selected`);
    } else {
      toast.warning('No valid image files found');
    }
  }, []);

  const removeFile = useCallback((index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const processFolder = useCallback(async () => {
    if (selectedFiles.length === 0) {
      toast.warning('Please select some images first');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setResults([]);
    onProcessingStart(selectedFiles.length);

    try {
      let processedResults = [];
      
      if (useParallelProcessing) {
        // Parallel processing
        setCurrentFile('Processing in parallel...');
        setProgress(10);
        
        try {
          const parallelResult = await apiService.processBatchParallel(selectedFiles, {
            detectFace,
            detectLicensePlate,
            enableBlur,
            faceBlurStrength,
            plateBlurStrength,
            maxWorkers: maxWorkers
          });

          console.log('🔍 Parallel processing result:', parallelResult);

          if (!parallelResult.success) {
            throw new Error(parallelResult.error);
          }

          // Check if we have results
          if (!parallelResult.data || !parallelResult.data.results) {
            console.error('❌ No results in parallel processing response:', parallelResult.data);
            throw new Error('No results returned from parallel processing');
          }

          console.log('✅ Parallel processing results:', parallelResult.data.results);

          // Convert parallel results to our format
          processedResults = parallelResult.data.results.map(result => {
            const file = selectedFiles.find(f => f.name === result.filename);
            const convertedResult = {
              id: Date.now() + Math.random(),
              filename: result.filename,
              file: file,
              preview: file ? URL.createObjectURL(file) : '',
              detection: result.detection, // This should already be the correct format
              blurred: result.blur,       // This should already be the correct format
              timestamp: new Date().toISOString()
            };
            console.log(`🔄 Converted result for ${result.filename}:`, convertedResult);
            console.log(`🔍 Detection data:`, result.detection);
            console.log(`🔍 Blur data:`, result.blur);
            return convertedResult;
          });

          console.log('📊 Final processed results:', processedResults);

          setProgress(100);
          onProgressUpdate(selectedFiles.length, selectedFiles.length);
          
          // Show parallel processing stats
          const stats = parallelResult.data;
          toast.success(
            `Parallel processing completed: ${stats.successful_count}/${stats.total_images} images processed in ${(stats.total_processing_time_ms / 1000).toFixed(1)}s (${stats.parallel_efficiency.toFixed(1)}% efficiency)`
          );
          
        } catch (parallelError) {
          console.warn('Parallel processing failed, falling back to sequential:', parallelError);
          toast.warning(`Parallel processing failed: ${parallelError.message}. Falling back to sequential processing...`);
          
          // Fallback to sequential processing
          for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            setCurrentFile(file.name);
            
            // Update progress
            const currentProgress = ((i + 1) / selectedFiles.length) * 100;
            setProgress(currentProgress);
            onProgressUpdate(i + 1, selectedFiles.length);

            try {
              // Process detection
              const detectionResult = await apiService.detectObjects(
                file,
                detectFace,
                detectLicensePlate
              );

              if (!detectionResult.success) {
                throw new Error(detectionResult.error);
              }

              // Process blur
              let blurResult = null;
              if (enableBlur) {
                blurResult = await apiService.blurObjects(
                  file,
                  detectFace,
                  detectLicensePlate,
                  faceBlurStrength,
                  plateBlurStrength
                );
              }

              if (enableBlur && !blurResult.success) {
                throw new Error(blurResult.error);
              }

              // Store result with EXACT same structure as single image processing
              processedResults.push({
                id: Date.now() + Math.random(),
                filename: file.name,
                file: file,
                preview: URL.createObjectURL(file),
                detection: detectionResult.data,
                blurred: blurResult?.data || null,
                timestamp: new Date().toISOString()
              });

            } catch (error) {
              console.error(`Error processing ${file.name}:`, error);
              toast.error(`Failed to process ${file.name}: ${error.message}`);
            }
          }
          
          toast.success(`Sequential fallback completed: ${processedResults.length} images processed`);
        }
        
      } else {
        // Sequential processing (original method)
        for (let i = 0; i < selectedFiles.length; i++) {
          const file = selectedFiles[i];
          setCurrentFile(file.name);
          
          // Update progress
          const currentProgress = ((i + 1) / selectedFiles.length) * 100;
          setProgress(currentProgress);
          onProgressUpdate(i + 1, selectedFiles.length);

          try {
            // Process detection
            const detectionResult = await apiService.detectObjects(
              file,
              detectFace,
              detectLicensePlate
            );

            if (!detectionResult.success) {
              throw new Error(detectionResult.error);
            }

            // Process blur
            let blurResult = null;
            if (enableBlur) {
              blurResult = await apiService.blurObjects(
                file,
                detectFace,
                detectLicensePlate,
                faceBlurStrength,
                plateBlurStrength
              );

              if (!blurResult.success) {
                throw new Error(blurResult.error);
              }
            }

            // Store result with EXACT same structure as single image processing
            processedResults.push({
              id: Date.now() + Math.random(),
              filename: file.name,
              file: file,
              preview: URL.createObjectURL(file),
              detection: detectionResult.data,
              blurred: blurResult?.data || null,
              timestamp: new Date().toISOString()
            });

          } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            toast.error(`Failed to process ${file.name}: ${error.message}`);
          }
        }
        
        toast.success(`Successfully processed ${processedResults.length} images sequentially`);
      }

      console.log('🎯 Setting results:', processedResults);
      setResults(processedResults);
      onProcessingComplete(processedResults.length);
      console.log('✅ Results set, count:', processedResults.length);

    } catch (error) {
      console.error('Folder processing error:', error);
      toast.error('Folder processing failed: ' + error.message);
    } finally {
      setIsProcessing(false);
      setCurrentFile('');
    }
  }, [
    selectedFiles,
    onProcessingStart,
    onProcessingComplete,
    onProgressUpdate,
    useParallelProcessing,
    maxWorkers,
    detectFace,
    detectLicensePlate,
    enableBlur,
    faceBlurStrength,
    plateBlurStrength
  ]);

  const downloadZip = useCallback(async () => {
    if (results.length === 0) {
      toast.warning('No processed results to download');
      return;
    }

    setIsCreatingZip(true);
    
    try {
      const zip = new JSZip();
      const folderName = selectedFiles[0]?.name.split('.')[0] || 'processed_images';
      
      // Add original images
      const originalsFolder = zip.folder('originals');
      for (const result of results) {
        const arrayBuffer = await result.originalFile.arrayBuffer();
        originalsFolder.file(result.originalFile.name, arrayBuffer);
      }
      
      // Add blurred images
      const blurredFolder = zip.folder('blurred');
      for (const result of results) {
        if (result.blur?.blurred_image_path) {
          try {
            const filename = result.blur.blurred_image_path.split('/').pop();
            const response = await fetch(`http://localhost:8000/download/${filename}`);
            
            if (response.ok) {
              const blob = await response.blob();
              const arrayBuffer = await blob.arrayBuffer();
              blurredFolder.file(filename, arrayBuffer);
            }
          } catch (error) {
            console.error(`Error downloading blurred image for ${result.originalFile.name}:`, error);
          }
        }
      }
      
      // Add detection results JSON
      const detectionData = results.map(result => ({
        filename: result.originalFile.name,
        detection: result.detection,
        blur: result.blur,
        processedAt: result.processedAt
      }));
      
      zip.file('detection_results.json', JSON.stringify(detectionData, null, 2));
      
      // Generate and download zip
      const zipBlob = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(zipBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${folderName}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('ZIP file downloaded successfully');
      
    } catch (error) {
      console.error('Error creating ZIP:', error);
      toast.error('Failed to create ZIP file: ' + error.message);
    } finally {
      setIsCreatingZip(false);
    }
  }, [results, selectedFiles]);

  const clearResults = useCallback(() => {
    setSelectedFiles([]);
    setResults([]);
    setProgress(0);
    setCurrentFile('');
  }, []);

  // Full-screen viewer functions
  const openViewer = useCallback((index) => {
    setViewerIndex(index);
    setIsViewerOpen(true);
  }, []);

  const closeViewer = useCallback(() => {
    setIsViewerOpen(false);
  }, []);

  const handleViewerIndexChange = useCallback((newIndex) => {
    setViewerIndex(newIndex);
  }, []);

  // Image viewer control functions
  const toggleBoundingBoxes = useCallback(() => {
    setDisplaySettings(prev => ({
      ...prev,
      showBoundingBoxes: !prev.showBoundingBoxes
    }));
  }, []);

  const toggleLabels = useCallback(() => {
    setDisplaySettings(prev => ({
      ...prev,
      showLabels: !prev.showLabels
    }));
  }, []);

  const toggleBlurred = useCallback(() => {
    setDisplaySettings(prev => ({
      ...prev,
      showBlurred: !prev.showBlurred
    }));
  }, []);


  return (
    <FolderContainer>
      <Section>
        <SectionTitle>Batch Pipeline</SectionTitle>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', color: 'rgba(233, 238, 252, 0.75)' }}>
          <span>1) Select</span>
          <span>→</span>
          <span>2) Configure</span>
          <span>→</span>
          <span>3) Run</span>
          <span>→</span>
          <span>4) Review</span>
        </div>
      </Section>
      
      <Section>
        <SectionTitle>
          📂 Process Image Folder
        </SectionTitle>
        
        <FolderInput 
          className={selectedFiles.length > 0 ? 'has-files' : ''}
          onClick={() => document.getElementById('folderInput').click()}
        >
          <input
            id="folderInput"
            type="file"
            multiple
            accept="image/*"
            onChange={handleFolderSelect}
            style={{ display: 'none' }}
          />
          <FolderInputText>
            {selectedFiles.length > 0 
              ? `${selectedFiles.length} image(s) selected`
              : 'Click to select images or drag and drop'
            }
          </FolderInputText>
          <FolderInputSubtext>
            Supports JPG, PNG, GIF, BMP, WebP formats
          </FolderInputSubtext>
        </FolderInput>

        {selectedFiles.length > 0 && (
          <FileList>
            {selectedFiles.map((file, index) => (
              <FileItem key={index}>
                <FileInfo>
                  <FileIcon>🖼️</FileIcon>
                  <FileName>{file.name}</FileName>
                  <FileSize>({(file.size / 1024).toFixed(1)} KB)</FileSize>
                </FileInfo>
                <RemoveButton onClick={() => removeFile(index)}>
                  ✕
                </RemoveButton>
              </FileItem>
            ))}
          </FileList>
        )}

        {/* Parallel Processing Options */}
        <Section style={{ marginTop: '20px', padding: '15px', background: 'rgba(8, 12, 22, 0.5)', borderRadius: '10px' }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#e9eefc', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Processing Options</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useParallelProcessing}
                onChange={(e) => {
                  setUseParallelProcessing(e.target.checked);
                  if (e.target.checked) {
                    setShowParallelWarning(true);
                  }
                }}
                disabled={isProcessing}
              />
              <span style={{ fontWeight: '500' }}>Use Parallel Processing</span>
            </label>
            
            {useParallelProcessing && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <label style={{ fontSize: '14px', color: '#666' }}>Workers:</label>
                <select
                  value={maxWorkers}
                  onChange={(e) => setMaxWorkers(parseInt(e.target.value))}
                  disabled={isProcessing}
                  style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ddd' }}
                >
                  <option value={2}>2</option>
                  <option value={4}>4</option>
                  <option value={6}>6</option>
                  <option value={8}>8</option>
                </select>
              </div>
            )}
          </div>
          
          {useParallelProcessing && (
            <div style={{ 
              padding: '10px', 
              background: '#fff3cd', 
              border: '1px solid #ffeaa7', 
              borderRadius: '4px',
              fontSize: '14px',
              color: '#856404'
            }}>
              ⚠️ <strong>Warning:</strong> Parallel processing may use more system resources and could potentially affect detection accuracy due to concurrent model loading. Use for faster processing of large batches.
            </div>
          )}
        </Section>

        <Controls>
          <ControlButton
            variant="primary"
            onClick={processFolder}
            disabled={isProcessing || selectedFiles.length === 0}
          >
            {isProcessing 
              ? (useParallelProcessing ? '⚡ Processing in parallel...' : '⏳ Processing...') 
              : (useParallelProcessing ? '⚡ Process Folder (Parallel)' : '🚀 Process Folder (Sequential)')
            }
          </ControlButton>
          
          {results.length > 0 && (
            <ControlButton
              variant="success"
              onClick={downloadZip}
              disabled={isCreatingZip}
            >
              {isCreatingZip ? '⏳ Creating ZIP...' : '📦 Download ZIP'}
            </ControlButton>
          )}
          
          <ControlButton
            variant="danger"
            onClick={clearResults}
            disabled={isProcessing}
          >
            🗑️ Clear All
          </ControlButton>
        </Controls>

        {isProcessing && (
          <ProgressContainer>
            <ProgressBar>
              <ProgressFill progress={progress} />
            </ProgressBar>
            <ProgressText>
              <span>{currentFile}</span>
              <span>{Math.round(progress)}%</span>
            </ProgressText>
          </ProgressContainer>
        )}
      </Section>

      {results.length > 0 && (
        <Section>
          <SectionTitle>
            📊 Processing Results ({results.length} images)
          </SectionTitle>

          <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <ControlButton
              variant="primary"
              onClick={toggleBoundingBoxes}
              disabled={isProcessing}
            >
              {displaySettings.showBoundingBoxes ? 'Hide Boxes' : 'Show Boxes'}
            </ControlButton>
            <ControlButton
              onClick={toggleLabels}
              disabled={isProcessing || !displaySettings.showBoundingBoxes}
            >
              {displaySettings.showLabels ? 'Hide Labels' : 'Show Labels'}
            </ControlButton>
            {results.some(r => r.blurred) && (
              <ControlButton
                onClick={toggleBlurred}
                disabled={isProcessing}
              >
                {displaySettings.showBlurred ? 'Original View' : 'Blurred View'}
              </ControlButton>
            )}
          </div>
          
          <ResultsGrid>
            {results.map((result, index) => {
              console.log(`🎨 Rendering result ${index}:`, result);
              
              return (
                <ResultCard key={index}>
                  <div style={{ position: 'relative' }}>
                    <ImageViewer
                      image={result}  // Pass the entire result object like in single image processing
                      detections={result.detection?.detections || []}  // Use the same structure as single image
                      showBoundingBoxes={displaySettings.showBoundingBoxes}
                      showLabels={displaySettings.showLabels}
                      showBlurred={displaySettings.showBlurred}
                      onToggleBoundingBoxes={toggleBoundingBoxes}
                      onToggleLabels={toggleLabels}
                      onToggleBlurred={toggleBlurred}
                      showControlsOverlay={false}
                      enableZoomPan
                    />
                  </div>
                  <ResultInfo>
                    <ResultTitle>{result.filename}</ResultTitle>
                    <ResultStats>
                      <span>👤 Faces: {result.detection?.total_faces || 0}</span>
                      <span>🚗 Plates: {result.detection?.total_license_plates || 0}</span>
                    </ResultStats>
                    <ResultActions>
                      <ActionButton 
                        className="primary"
                        onClick={() => openViewer(index)}
                        title="View full screen"
                      >
                        🔍 Full Screen
                      </ActionButton>
                    </ResultActions>
                  </ResultInfo>
                </ResultCard>
              );
            })}
          </ResultsGrid>
        </Section>
      )}

      <FullScreenViewer
        isOpen={isViewerOpen}
        onClose={closeViewer}
        images={results}
        currentIndex={viewerIndex}
        onIndexChange={handleViewerIndexChange}
      />
    </FolderContainer>
  );
};

export default FolderProcessor;
