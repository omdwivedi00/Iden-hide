/**
 * Navigation Bar Component
 * Provides navigation between different processing modes
 */

import React from 'react';
import styled from 'styled-components';

const NavbarContainer = styled.nav`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const NavContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
`;

const Logo = styled.div`
  color: white;
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const NavItems = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
`;

const NavButton = styled.button`
  background: ${props => props.active ? 'rgba(255,255,255,0.2)' : 'transparent'};
  color: white;
  border: 2px solid ${props => props.active ? 'white' : 'transparent'};
  padding: 8px 16px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.5);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-size: 14px;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    if (props.status === 'processing') return '#ffa726';
    if (props.status === 'success') return '#4caf50';
    if (props.status === 'error') return '#f44336';
    return '#9e9e9e';
  }};
  animation: ${props => props.status === 'processing' ? 'pulse 1.5s infinite' : 'none'};
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const Navbar = ({ 
  currentMode, 
  onModeChange, 
  isProcessing, 
  processingStatus,
  processedCount,
  totalCount 
}) => {
  return (
    <NavbarContainer>
      <NavContent>
        <Logo>
          🎯 Detection Studio
        </Logo>
        
        <NavItems>
          <NavButton
            active={currentMode === 'single'}
            onClick={() => onModeChange('single')}
            disabled={isProcessing}
          >
            📁 Single Images
          </NavButton>
          
          <NavButton
            active={currentMode === 'folder'}
            onClick={() => onModeChange('folder')}
            disabled={isProcessing}
          >
            📂 Process Folder
          </NavButton>
          
          <NavButton
            active={currentMode === 's3'}
            onClick={() => onModeChange('s3')}
            disabled={isProcessing}
          >
            ☁️ S3 Processing
          </NavButton>
        </NavItems>
        
        <StatusIndicator>
          <StatusDot status={processingStatus} />
          <span>
            {isProcessing 
              ? `Processing: ${processedCount}/${totalCount}`
              : processingStatus === 'success' 
                ? `Completed: ${totalCount} images`
                : 'Ready'
            }
          </span>
        </StatusIndicator>
      </NavContent>
    </NavbarContainer>
  );
};

export default Navbar;
