/**
 * S3 Processor Component
 * Handles S3 image processing with progress tracking
 */

import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { mediaQueries, layoutHelpers } from '../styles/mediaKit';
import { s3Service } from '../services/s3Service';
import S3ImageViewer from './S3ImageViewer';

const S3Container = styled.div`
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

const FormGrid = styled.div`
  ${layoutHelpers.grid({ xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 })}
  margin-bottom: 20px;
  
  ${mediaQueries.lg} {
    grid-template-columns: 1fr 1fr;
  }
  
  ${mediaQueries.xl} {
    grid-template-columns: 1fr 1fr 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 500;
  color: rgba(233, 238, 252, 0.8);
  font-size: 13px;
`;

const Input = styled.input`
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  font-size: 14px;
  color: #e9eefc;
  background: rgba(8, 12, 22, 0.6);
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: rgba(98, 126, 255, 0.8);
  }
  
  &:disabled {
    opacity: 0.5;
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
  font-size: 13px;
  color: rgba(233, 238, 252, 0.75);
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
  background: rgba(12, 16, 26, 0.6);
  color: #e9eefc;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(98, 126, 255, 0.15);
  }
  
  &.primary {
    background: linear-gradient(135deg, #627eff 0%, #8f6bff 100%);
    color: white;
    border-color: transparent;
  }
`;

const StepRail = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const StepItem = styled.div`
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: ${({ $active }) => ($active ? '#e9eefc' : 'rgba(233, 238, 252, 0.5)')};
  background: ${({ $active }) => ($active ? 'rgba(98, 126, 255, 0.25)' : 'rgba(8, 12, 22, 0.6)')};
`;

const S3Processor = ({ 
  onProcessingStart, 
  onProcessingComplete, 
  onProgressUpdate,
  detectFace: detectFaceProp = true,
  detectLicensePlate: detectLicensePlateProp = true,
  faceBlurStrength: faceBlurStrengthProp = 25,
  plateBlurStrength: plateBlurStrengthProp = 20,
  embedded = true,
  showDetectionControls = true
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
  const [detectFace, setDetectFace] = useState(detectFaceProp);
  const [detectLicensePlate, setDetectLicensePlate] = useState(detectLicensePlateProp);
  const [faceBlurStrength, setFaceBlurStrength] = useState(faceBlurStrengthProp);
  const [plateBlurStrength, setPlateBlurStrength] = useState(plateBlurStrengthProp);
  
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
  
  // Parallel processing settings
  const [useParallelProcessing, setUseParallelProcessing] = useState(false);
  const [maxWorkers, setMaxWorkers] = useState(4);

  useEffect(() => {
    setDetectFace(detectFaceProp);
    setDetectLicensePlate(detectLicensePlateProp);
    setFaceBlurStrength(faceBlurStrengthProp);
    setPlateBlurStrength(plateBlurStrengthProp);
  }, [detectFaceProp, detectLicensePlateProp, faceBlurStrengthProp, plateBlurStrengthProp]);

  const hasSelection = processingMode === 'single'
    ? Boolean(inputS3Path && outputS3Path)
    : Boolean(inputS3Folder && outputS3Folder);

  const hasResults = processingResults.length > 0;
  const activeStep = !credentialsValid ? 1 : !hasSelection ? 2 : isProcessing ? 3 : hasResults ? 4 : 3;

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

      const result = useParallelProcessing 
        ? await s3Service.processFolderParallel(requestData, maxWorkers)
        : await s3Service.processFolder(requestData);
      
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
      <Section>
        <SectionTitle>S3 Pipeline</SectionTitle>
        <StepRail>
          <StepItem $active={activeStep >= 1}>1) Credentials</StepItem>
          <StepItem $active={activeStep >= 2}>2) Select</StepItem>
          <StepItem $active={activeStep >= 3}>3) Run</StepItem>
          <StepItem $active={activeStep >= 4}>4) Review</StepItem>
        </StepRail>
      </Section>
      
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
              disabled={!credentialsValid || isProcessing}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>AWS Secret Access Key</Label>
            <Input
              type="password"
              value={credentials.aws_secret_access_key}
              onChange={(e) => setCredentials(prev => ({ ...prev, aws_secret_access_key: e.target.value }))}
              placeholder="Your secret key"
              disabled={!credentialsValid || isProcessing}
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
              disabled={!credentialsValid || isProcessing}
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
              disabled={!credentialsValid || isProcessing}
            />
            Single Image
          </CheckboxLabel>
          <CheckboxLabel>
            <Checkbox
              type="radio"
              name="processingMode"
              checked={processingMode === 'folder'}
              onChange={() => setProcessingMode('folder')}
              disabled={!credentialsValid || isProcessing}
            />
            Folder Processing
          </CheckboxLabel>
        </CheckboxGroup>
        
        {/* Parallel Processing Options */}
        <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(8, 12, 22, 0.5)', borderRadius: '10px' }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#e9eefc', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Processing Options</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useParallelProcessing}
                onChange={(e) => setUseParallelProcessing(e.target.checked)}
              disabled={!credentialsValid || isProcessing}
              />
              <span style={{ fontWeight: '500' }}>Use Parallel Processing</span>
            </label>
            
            {useParallelProcessing && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <label style={{ fontSize: '13px', color: 'rgba(233, 238, 252, 0.6)' }}>Workers:</label>
                <select
                  value={maxWorkers}
                  onChange={(e) => setMaxWorkers(parseInt(e.target.value))}
                  disabled={isProcessing}
                  style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.12)', background: 'rgba(8, 12, 22, 0.6)', color: '#e9eefc' }}
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
              background: 'rgba(255, 197, 85, 0.1)', 
              border: '1px solid rgba(255, 197, 85, 0.3)', 
              borderRadius: '8px',
              fontSize: '12px',
              color: 'rgba(255, 226, 168, 0.9)'
            }}>
              ⚠️ <strong>Warning:</strong> Parallel processing may use more system resources and could potentially affect detection accuracy due to concurrent model loading. Use for faster processing of large batches.
            </div>
          )}
        </div>
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
              {isProcessing 
                ? (useParallelProcessing ? '⚡ Processing in parallel...' : '⏳ Processing...') 
                : (useParallelProcessing ? '⚡ Process Image (Parallel)' : '🚀 Process Image (Sequential)')
              }
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
                {isProcessing 
                  ? (useParallelProcessing ? '⚡ Processing in parallel...' : '⏳ Processing...') 
                  : (useParallelProcessing ? '⚡ Process Folder (Parallel)' : '🚀 Process Folder (Sequential)')
                }
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

      {showDetectionControls && (
        <Section>
          <SectionTitle>
            Detection Settings
          </SectionTitle>
          
          <CheckboxGroup>
            <CheckboxLabel>
              <Checkbox
                type="checkbox"
                checked={detectFace}
                onChange={(e) => setDetectFace(e.target.checked)}
                disabled={!credentialsValid || isProcessing}
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
      )}

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
