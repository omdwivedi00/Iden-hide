/**
 * Status Bar Component
 * Shows processing status and progress
 */

import React from 'react';
import styled, { keyframes } from 'styled-components';

const pulse = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
`;

const StatusContainer = styled.div`
  background: ${props => {
    switch (props.status) {
      case 'success': return '#d4edda';
      case 'error': return '#f8d7da';
      case 'warning': return '#fff3cd';
      case 'processing': return '#cce7ff';
      default: return '#f8f9fa';
    }
  }};
  border: 1px solid ${props => {
    switch (props.status) {
      case 'success': return '#c3e6cb';
      case 'error': return '#f5c6cb';
      case 'warning': return '#ffeaa7';
      case 'processing': return '#99d6ff';
      default: return '#dee2e6';
    }
  }};
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const StatusContent = styled.div`
  display: flex;
  align-items: center;
  flex: 1;
`;

const StatusIcon = styled.div`
  font-size: 20px;
  margin-right: 10px;
  animation: ${props => props.animate ? pulse : 'none'} 1.5s infinite;
`;

const StatusText = styled.div`
  flex: 1;
`;

const StatusTitle = styled.div`
  font-weight: 600;
  color: ${props => {
    switch (props.status) {
      case 'success': return '#155724';
      case 'error': return '#721c24';
      case 'warning': return '#856404';
      case 'processing': return '#004085';
      default: return '#495057';
    }
  }};
  margin-bottom: 5px;
`;

const StatusMessage = styled.div`
  font-size: 14px;
  color: ${props => {
    switch (props.status) {
      case 'success': return '#155724';
      case 'error': return '#721c24';
      case 'warning': return '#856404';
      case 'processing': return '#004085';
      default: return '#6c757d';
    }
  }};
`;

const ProgressBar = styled.div`
  width: 200px;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-left: 20px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => {
    switch (props.status) {
      case 'success': return '#28a745';
      case 'error': return '#dc3545';
      case 'warning': return '#ffc107';
      case 'processing': return '#007bff';
      default: return '#6c757d';
    }
  }};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #6c757d;
  margin-left: 10px;
  
  &:hover {
    color: #495057;
  }
`;

const StatusBar = ({ 
  status = 'idle', 
  title = '', 
  message = '', 
  progress = 0, 
  onClose,
  show = false 
}) => {
  if (!show) return null;

  const getStatusIcon = () => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'processing': return '🔄';
      default: return 'ℹ️';
    }
  };

  const getStatusTitle = () => {
    if (title) return title;
    
    switch (status) {
      case 'success': return 'Success';
      case 'error': return 'Error';
      case 'warning': return 'Warning';
      case 'processing': return 'Processing';
      default: return 'Info';
    }
  };

  return (
    <StatusContainer status={status}>
      <StatusContent>
        <StatusIcon animate={status === 'processing'}>
          {getStatusIcon()}
        </StatusIcon>
        
        <StatusText>
          <StatusTitle status={status}>
            {getStatusTitle()}
          </StatusTitle>
          {message && (
            <StatusMessage status={status}>
              {message}
            </StatusMessage>
          )}
        </StatusText>
      </StatusContent>
      
      {status === 'processing' && (
        <ProgressBar>
          <ProgressFill 
            status={status} 
            progress={progress}
          />
        </ProgressBar>
      )}
      
      {onClose && (
        <CloseButton onClick={onClose}>
          ×
        </CloseButton>
      )}
    </StatusContainer>
  );
};

export default StatusBar;
