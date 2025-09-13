/**
 * Folder Processor Component
 * Handles batch processing of images from a folder
 */

import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import JSZip from 'jszip';
import apiService from '../services/apiService';
import FullScreenViewer from './FullScreenViewer';

const FolderContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const Section = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const SectionTitle = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const FolderInput = styled.div`
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
  
  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
  
  &.has-files {
    border-color: #4caf50;
    background: #f1f8e9;
  }
`;

const FolderInputText = styled.div`
  color: #666;
  font-size: 16px;
  margin-bottom: 10px;
`;

const FolderInputSubtext = styled.div`
  color: #999;
  font-size: 14px;
`;

const FileList = styled.div`
  margin-top: 20px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  
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
  color: #333;
  font-size: 14px;
`;

const FileSize = styled.span`
  color: #666;
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
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
  onProgressUpdate 
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
      const processedResults = [];
      
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
            true, // detect_face
            true  // detect_license_plate
          );

          if (!detectionResult.success) {
            throw new Error(detectionResult.error);
          }

          // Process blur
          const blurResult = await apiService.blurObjects(
            file,
            true, // detect_face
            true, // detect_license_plate
            25,   // face_blur_strength
            20    // plate_blur_strength
          );

          if (!blurResult.success) {
            throw new Error(blurResult.error);
          }

          // Store result
          processedResults.push({
            originalFile: file,
            detection: detectionResult.data,
            blur: blurResult.data,
            processedAt: new Date().toISOString()
          });

        } catch (error) {
          console.error(`Error processing ${file.name}:`, error);
          toast.error(`Failed to process ${file.name}: ${error.message}`);
        }
      }

      setResults(processedResults);
      onProcessingComplete(processedResults.length);
      toast.success(`Successfully processed ${processedResults.length} images`);

    } catch (error) {
      console.error('Folder processing error:', error);
      toast.error('Folder processing failed: ' + error.message);
    } finally {
      setIsProcessing(false);
      setCurrentFile('');
    }
  }, [selectedFiles, onProcessingStart, onProcessingComplete, onProgressUpdate]);

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

  return (
    <FolderContainer>
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

        <Controls>
          <ControlButton
            variant="primary"
            onClick={processFolder}
            disabled={isProcessing || selectedFiles.length === 0}
          >
            {isProcessing ? '⏳ Processing...' : '🚀 Process Folder'}
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
          
          <ResultsGrid>
            {results.map((result, index) => (
              <ResultCard key={index}>
                <ResultImage 
                  src={URL.createObjectURL(result.originalFile)}
                  alt={result.originalFile.name}
                  onClick={() => openViewer(index)}
                  title="Click to view full screen"
                />
                <ResultInfo>
                  <ResultTitle>{result.originalFile.name}</ResultTitle>
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
                    <ActionButton onClick={() => {
                      const link = document.createElement('a');
                      link.href = URL.createObjectURL(result.originalFile);
                      link.download = result.originalFile.name;
                      link.click();
                    }}>
                      📥 Original
                    </ActionButton>
                    {result.blur?.blurred_image_path && (
                      <ActionButton onClick={() => {
                        const filename = result.blur.blurred_image_path.split('/').pop();
                        const link = document.createElement('a');
                        link.href = `http://localhost:8000/download/${filename}`;
                        link.download = `blurred_${result.originalFile.name}`;
                        link.click();
                      }}>
                        🔒 Blurred
                      </ActionButton>
                    )}
                  </ResultActions>
                </ResultInfo>
              </ResultCard>
            ))}
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
