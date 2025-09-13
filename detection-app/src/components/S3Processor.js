/**
 * S3 Processor Component
 * Handles S3 image processing with progress tracking
 */

import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { s3Service } from '../services/s3Service';
import S3ImageViewer from './S3ImageViewer';

const S3Container = styled.div`
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

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 500;
  color: #333;
  font-size: 14px;
`;

const Input = styled.input`
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
  
  &:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
  }
`;


const CheckboxGroup = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
  margin: 15px 0;
`;

const Checkbox = styled.input`
  margin-right: 8px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #333;
  cursor: pointer;
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
    if (props.variant === 'warning') return '#ff9800';
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

const StatusCard = styled.div`
  background: ${props => {
    if (props.status === 'success') return '#e8f5e8';
    if (props.status === 'error') return '#ffeaea';
    if (props.status === 'warning') return '#fff3cd';
    return '#f0f4ff';
  }};
  border: 1px solid ${props => {
    if (props.status === 'success') return '#4caf50';
    if (props.status === 'error') return '#f44336';
    if (props.status === 'warning') return '#ff9800';
    return '#667eea';
  }};
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
`;

const StatusTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StatusText = styled.p`
  margin: 5px 0;
  color: #666;
  font-size: 14px;
`;

const ProgressContainer = styled.div`
  margin: 20px 0;
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

const FileList = styled.div`
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
  margin: 15px 0;
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
  
  &.processing {
    background: #fff3cd;
  }
  
  &.success {
    background: #e8f5e8;
  }
  
  &.error {
    background: #ffeaea;
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

const S3Processor = ({ 
  onProcessingStart, 
  onProcessingComplete, 
  onProgressUpdate 
}) => {
  // Credentials state
  const [credentials, setCredentials] = useState({
    aws_access_key_id: '',
    aws_secret_access_key: '',
    aws_session_token: ''
  });

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [isTestingCredentials, setIsTestingCredentials] = useState(false);
  const [isListingFolder, setIsListingFolder] = useState(false);
  
  // S3 paths
  const [inputS3Path, setInputS3Path] = useState('');
  const [outputS3Path, setOutputS3Path] = useState('');
  const [inputS3Folder, setInputS3Folder] = useState('');
  const [outputS3Folder, setOutputS3Folder] = useState('');
  
  // Detection settings
  const [detectFace, setDetectFace] = useState(true);
  const [detectLicensePlate, setDetectLicensePlate] = useState(true);
  const [faceBlurStrength, setFaceBlurStrength] = useState(25);
  const [plateBlurStrength, setPlateBlurStrength] = useState(20);
  
  // Processing mode
  const [processingMode, setProcessingMode] = useState('single'); // 'single' or 'folder'
  
  // Status and progress
  const [status, setStatus] = useState({ type: 'idle', message: '', details: '' });
  const [progress, setProgress] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  
  // Results
  const [folderFiles, setFolderFiles] = useState([]);
  const [processingResults, setProcessingResults] = useState([]);
  const [credentialsValid, setCredentialsValid] = useState(false);
  
  // Image viewer
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [viewerIndex, setViewerIndex] = useState(0);

  // Test credentials
  const testCredentials = useCallback(async () => {
    if (!credentials.aws_access_key_id || !credentials.aws_secret_access_key) {
      toast.warning('Please enter AWS credentials');
      return;
    }

    setIsTestingCredentials(true);
    setStatus({ type: 'info', message: 'Testing AWS credentials...', details: '' });

    try {
      const result = await s3Service.testCredentials(credentials);
      
      if (result.success) {
        setCredentialsValid(true);
        setStatus({ type: 'success', message: 'AWS credentials are valid!', details: 'Connection established successfully' });
        toast.success('AWS credentials validated');
      } else {
        setCredentialsValid(false);
        setStatus({ type: 'error', message: 'Invalid AWS credentials', details: result.error });
        toast.error('AWS credentials test failed');
      }
    } catch (error) {
      setCredentialsValid(false);
      setStatus({ type: 'error', message: 'Credentials test failed', details: error.message });
      toast.error('Failed to test credentials');
    } finally {
      setIsTestingCredentials(false);
    }
  }, [credentials]);

  // List S3 folder
  const listS3Folder = useCallback(async () => {
    if (!credentialsValid) {
      toast.warning('Please test credentials first');
      return;
    }

    if (!inputS3Folder) {
      toast.warning('Please enter S3 folder path');
      return;
    }

    setIsListingFolder(true);
    setStatus({ type: 'info', message: 'Listing S3 folder contents...', details: '' });

    try {
      const result = await s3Service.listS3Folder(credentials, inputS3Folder);
      
      if (result.success) {
        setFolderFiles(result.data.files);
        setTotalFiles(result.data.total_count);
        setStatus({ 
          type: 'success', 
          message: `Found ${result.data.total_count} images in folder`, 
          details: `Folder: ${result.data.folder_path}` 
        });
        toast.success(`Found ${result.data.total_count} images`);
      } else {
        setStatus({ type: 'error', message: 'Failed to list folder', details: result.error });
        toast.error('Failed to list S3 folder');
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Folder listing failed', details: error.message });
      toast.error('Failed to list folder');
    } finally {
      setIsListingFolder(false);
    }
  }, [credentials, inputS3Folder, credentialsValid]);

  // Process single image
  const processSingleImage = useCallback(async () => {
    if (!credentialsValid) {
      toast.warning('Please test credentials first');
      return;
    }

    if (!inputS3Path || !outputS3Path) {
      toast.warning('Please enter both input and output S3 paths');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setStatus({ type: 'info', message: 'Processing single image...', details: '' });
    onProcessingStart(1);

    try {
      const requestData = {
        credentials,
        input_s3_path: inputS3Path,
        output_s3_path: outputS3Path,
        detect_face: detectFace,
        detect_license_plate: detectLicensePlate,
        face_blur_strength: faceBlurStrength,
        plate_blur_strength: plateBlurStrength
      };

      const result = await s3Service.processSingleImage(requestData);
      
      if (result.success) {
        setProgress(100);
        setStatus({ 
          type: 'success', 
          message: 'Image processed successfully!', 
          details: `Faces: ${result.data.result.faces_detected}, Plates: ${result.data.result.license_plates_detected}` 
        });
        setProcessingResults([result.data.result]);
        onProcessingComplete(1);
        toast.success('Image processed successfully');
      } else {
        setStatus({ type: 'error', message: 'Processing failed', details: result.error });
        toast.error('Failed to process image');
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Processing failed', details: error.message });
      toast.error('Failed to process image');
    } finally {
      setIsProcessing(false);
    }
  }, [credentials, inputS3Path, outputS3Path, detectFace, detectLicensePlate, faceBlurStrength, plateBlurStrength, credentialsValid, onProcessingStart, onProcessingComplete]);

  // Process folder
  const processFolder = useCallback(async () => {
    if (!credentialsValid) {
      toast.warning('Please test credentials first');
      return;
    }

    if (!inputS3Folder || !outputS3Folder) {
      toast.warning('Please enter both input and output S3 folder paths');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setStatus({ type: 'info', message: 'Starting folder processing...', details: '' });
    onProcessingStart(totalFiles);

    try {
      const requestData = {
        credentials,
        input_s3_folder: inputS3Folder,
        output_s3_folder: outputS3Folder,
        detect_face: detectFace,
        detect_license_plate: detectLicensePlate,
        face_blur_strength: faceBlurStrength,
        plate_blur_strength: plateBlurStrength
      };

      const result = await s3Service.processFolder(requestData);
      
      if (result.success) {
        setProgress(100);
        setStatus({ 
          type: 'success', 
          message: `Folder processing completed!`, 
          details: `Processed ${result.data.successful_count}/${result.data.total_images} images successfully` 
        });
        setProcessingResults(result.data.results);
        onProcessingComplete(result.data.successful_count);
        toast.success(`Processed ${result.data.successful_count} images`);
      } else {
        setStatus({ type: 'error', message: 'Folder processing failed', details: result.error });
        toast.error('Failed to process folder');
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Folder processing failed', details: error.message });
      toast.error('Failed to process folder');
    } finally {
      setIsProcessing(false);
    }
  }, [credentials, inputS3Folder, outputS3Folder, detectFace, detectLicensePlate, faceBlurStrength, plateBlurStrength, credentialsValid, totalFiles, onProcessingStart, onProcessingComplete]);

  // Image viewer functions
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
    <S3Container>
      {/* Credentials Section */}
      <Section>
        <SectionTitle>
          🔐 AWS S3 Credentials
        </SectionTitle>
        
        <FormGrid>
          <FormGroup>
            <Label>AWS Access Key ID</Label>
            <Input
              type="text"
              value={credentials.aws_access_key_id}
              onChange={(e) => setCredentials(prev => ({ ...prev, aws_access_key_id: e.target.value }))}
              placeholder="AKIA..."
              disabled={isProcessing}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>AWS Secret Access Key</Label>
            <Input
              type="password"
              value={credentials.aws_secret_access_key}
              onChange={(e) => setCredentials(prev => ({ ...prev, aws_secret_access_key: e.target.value }))}
              placeholder="Your secret key"
              disabled={isProcessing}
            />
          </FormGroup>
        </FormGrid>
        
        <FormGroup>
          <Label>AWS Session Token (Optional)</Label>
          <Input
            type="text"
            value={credentials.aws_session_token}
            onChange={(e) => setCredentials(prev => ({ ...prev, aws_session_token: e.target.value }))}
            placeholder="For temporary credentials"
            disabled={isProcessing}
          />
        </FormGroup>
        
        <Controls>
          <ControlButton
            variant="primary"
            onClick={testCredentials}
            disabled={isTestingCredentials || isProcessing}
          >
            {isTestingCredentials ? '⏳ Testing...' : '🔐 Test Credentials'}
          </ControlButton>
        </Controls>
      </Section>

      {/* Processing Mode Selection */}
      <Section>
        <SectionTitle>
          ⚙️ Processing Mode
        </SectionTitle>
        
        <CheckboxGroup>
          <CheckboxLabel>
            <Checkbox
              type="radio"
              name="processingMode"
              checked={processingMode === 'single'}
              onChange={() => setProcessingMode('single')}
              disabled={isProcessing}
            />
            Single Image
          </CheckboxLabel>
          <CheckboxLabel>
            <Checkbox
              type="radio"
              name="processingMode"
              checked={processingMode === 'folder'}
              onChange={() => setProcessingMode('folder')}
              disabled={isProcessing}
            />
            Folder Processing
          </CheckboxLabel>
        </CheckboxGroup>
      </Section>

      {/* Single Image Processing */}
      {processingMode === 'single' && (
        <Section>
          <SectionTitle>
            🖼️ Single Image Processing
          </SectionTitle>
          
          <FormGrid>
            <FormGroup>
              <Label>Input S3 Path</Label>
              <Input
                type="text"
                value={inputS3Path}
                onChange={(e) => setInputS3Path(e.target.value)}
                placeholder="s3://bucket/path/image.jpg"
                disabled={isProcessing}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Output S3 Path</Label>
              <Input
                type="text"
                value={outputS3Path}
                onChange={(e) => setOutputS3Path(e.target.value)}
                placeholder="s3://bucket/path/image-blurred.jpg"
                disabled={isProcessing}
              />
            </FormGroup>
          </FormGrid>
          
          <Controls>
            <ControlButton
              variant="success"
              onClick={processSingleImage}
              disabled={!credentialsValid || isProcessing}
            >
              {isProcessing ? '⏳ Processing...' : '🚀 Process Image'}
            </ControlButton>
          </Controls>
        </Section>
      )}

      {/* Folder Processing */}
      {processingMode === 'folder' && (
        <>
          <Section>
            <SectionTitle>
              📁 Folder Processing
            </SectionTitle>
            
            <FormGrid>
              <FormGroup>
                <Label>Input S3 Folder</Label>
                <Input
                  type="text"
                  value={inputS3Folder}
                  onChange={(e) => setInputS3Folder(e.target.value)}
                  placeholder="s3://bucket/input/"
                  disabled={isProcessing}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Output S3 Folder</Label>
                <Input
                  type="text"
                  value={outputS3Folder}
                  onChange={(e) => setOutputS3Folder(e.target.value)}
                  placeholder="s3://bucket/output/"
                  disabled={isProcessing}
                />
              </FormGroup>
            </FormGrid>
            
            <Controls>
              <ControlButton
                variant="warning"
                onClick={listS3Folder}
                disabled={!credentialsValid || isListingFolder || isProcessing}
              >
                {isListingFolder ? '⏳ Listing...' : '📋 List Folder'}
              </ControlButton>
              
              <ControlButton
                variant="success"
                onClick={processFolder}
                disabled={!credentialsValid || totalFiles === 0 || isProcessing}
              >
                {isProcessing ? '⏳ Processing...' : '🚀 Process Folder'}
              </ControlButton>
            </Controls>
          </Section>

          {/* Folder Files List */}
          {folderFiles.length > 0 && (
            <Section>
              <SectionTitle>
                📋 Folder Contents ({folderFiles.length} files)
              </SectionTitle>
              
              <FileList>
                {folderFiles.map((file, index) => (
                  <FileItem key={index}>
                    <FileInfo>
                      <FileIcon>🖼️</FileIcon>
                      <FileName>{file.filename}</FileName>
                    </FileInfo>
                  </FileItem>
                ))}
              </FileList>
            </Section>
          )}
        </>
      )}

      {/* Detection Settings */}
      <Section>
        <SectionTitle>
          🎯 Detection Settings
        </SectionTitle>
        
        <CheckboxGroup>
          <CheckboxLabel>
            <Checkbox
              type="checkbox"
              checked={detectFace}
              onChange={(e) => setDetectFace(e.target.checked)}
              disabled={isProcessing}
            />
            Detect Faces
          </CheckboxLabel>
          <CheckboxLabel>
            <Checkbox
              type="checkbox"
              checked={detectLicensePlate}
              onChange={(e) => setDetectLicensePlate(e.target.checked)}
              disabled={isProcessing}
            />
            Detect License Plates
          </CheckboxLabel>
        </CheckboxGroup>
        
        <FormGrid>
          <FormGroup>
            <Label>Face Blur Strength</Label>
            <Input
              type="number"
              value={faceBlurStrength}
              onChange={(e) => setFaceBlurStrength(parseInt(e.target.value))}
              min="5"
              max="100"
              disabled={isProcessing}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Plate Blur Strength</Label>
            <Input
              type="number"
              value={plateBlurStrength}
              onChange={(e) => setPlateBlurStrength(parseInt(e.target.value))}
              min="5"
              max="100"
              disabled={isProcessing}
            />
          </FormGroup>
        </FormGrid>
      </Section>

      {/* Status and Progress */}
      {status.type !== 'idle' && (
        <Section>
          <SectionTitle>
            📊 Processing Status
          </SectionTitle>
          
          <StatusCard status={status.type}>
            <StatusTitle>
              {status.type === 'success' && '✅'}
              {status.type === 'error' && '❌'}
              {status.type === 'warning' && '⚠️'}
              {status.type === 'info' && 'ℹ️'}
              {status.message}
            </StatusTitle>
            {status.details && <StatusText>{status.details}</StatusText>}
          </StatusCard>
          
          {isProcessing && (
            <ProgressContainer>
              <ProgressBar>
                <ProgressFill progress={progress} />
              </ProgressBar>
              <ProgressText>
                <span>Processing...</span>
                <span>{Math.round(progress)}%</span>
              </ProgressText>
            </ProgressContainer>
          )}
        </Section>
      )}

      {/* Results */}
      {processingResults.length > 0 && (
        <Section>
          <SectionTitle>
            📊 Processing Results ({processingResults.length} images)
          </SectionTitle>
          
          <ResultsGrid>
            {processingResults.map((result, index) => (
              <ResultCard key={index}>
                <ResultInfo>
                  <ResultTitle>{result.original_filename || `Result ${index + 1}`}</ResultTitle>
                  <ResultStats>
                    <span>👤 Faces: {result.faces_detected || 0}</span>
                    <span>🚗 Plates: {result.license_plates_detected || 0}</span>
                    <span>⏱️ Time: {result.processing_time_seconds || 0}s</span>
                  </ResultStats>
                  <ResultActions>
                    <ActionButton
                      className="primary"
                      onClick={() => openViewer(index)}
                    >
                      👁️ View Here
                    </ActionButton>
                    <ActionButton
                      onClick={() => window.open(result.output_s3_url, '_blank')}
                    >
                      🔗 View in S3
                    </ActionButton>
                  </ResultActions>
                </ResultInfo>
              </ResultCard>
            ))}
          </ResultsGrid>
        </Section>
      )}

      {/* S3 Image Viewer */}
      <S3ImageViewer
        isOpen={isViewerOpen}
        onClose={closeViewer}
        images={processingResults}
        currentIndex={viewerIndex}
        onIndexChange={handleViewerIndexChange}
        credentials={credentials}
      />
    </S3Container>
  );
};

export default S3Processor;
