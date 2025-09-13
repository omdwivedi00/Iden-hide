/**
 * File Upload Component
 * Handles file selection and validation
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileUtils } from '../utils/fileUtils';
import styled from 'styled-components';

const UploadContainer = styled.div`
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: ${props => props.isDragActive ? '#f0f8ff' : '#fafafa'};
  border-color: ${props => props.isDragActive ? '#007bff' : '#ccc'};

  &:hover {
    border-color: #007bff;
    background-color: #f0f8ff;
  }
`;

const UploadText = styled.div`
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
`;

const FileList = styled.div`
  margin-top: 20px;
  text-align: left;
`;

const FileItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin: 4px 0;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid ${props => props.isValid ? '#28a745' : '#dc3545'};
`;

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.div`
  font-weight: 500;
  color: #333;
`;

const FileSize = styled.div`
  font-size: 12px;
  color: #666;
`;

const RemoveButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;

  &:hover {
    background: #c82333;
  }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  font-size: 14px;
  margin-top: 10px;
`;

const FileUpload = ({ onFilesSelected, maxFiles = 10, accept = "image/*" }) => {
  const [files, setFiles] = useState([]);
  const [errors, setErrors] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Validate files
    const validation = FileUtils.validateFiles(acceptedFiles);
    
    // Update files state
    setFiles(prevFiles => [...prevFiles, ...validation.validFiles]);
    
    // Update errors state
    setErrors(prevErrors => [...prevErrors, ...validation.invalidFiles]);
    
    // Notify parent component
    if (validation.validFiles.length > 0) {
      onFilesSelected(validation.validFiles);
    }
  }, [onFilesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles,
    multiple: true
  });

  const removeFile = (index) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setFiles([]);
    setErrors([]);
  };

  return (
    <div>
      <UploadContainer {...getRootProps()} isDragActive={isDragActive}>
        <input {...getInputProps()} />
        <UploadText>
          {isDragActive
            ? 'Drop the images here...'
            : 'Drag & drop images here, or click to select files'
          }
        </UploadText>
        <div style={{ fontSize: '14px', color: '#999' }}>
          Supports: JPG, PNG, GIF, WebP (Max {maxFiles} files)
        </div>
      </UploadContainer>

      {files.length > 0 && (
        <FileList>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h4>Selected Files ({files.length})</h4>
            <button 
              onClick={clearAll}
              style={{
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '4px 8px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Clear All
            </button>
          </div>
          {files.map((file, index) => (
            <FileItem key={index} isValid={FileUtils.isValidImage(file)}>
              <FileInfo>
                <FileName>{file.name}</FileName>
                <FileSize>{FileUtils.formatFileSize(file.size)}</FileSize>
              </FileInfo>
              <RemoveButton onClick={() => removeFile(index)}>
                Remove
              </RemoveButton>
            </FileItem>
          ))}
        </FileList>
      )}

      {errors.length > 0 && (
        <div>
          <h4 style={{ color: '#dc3545', marginBottom: '10px' }}>Invalid Files:</h4>
          {errors.map((error, index) => (
            <ErrorMessage key={index}>
              {error.name}: {error.reason}
            </ErrorMessage>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
