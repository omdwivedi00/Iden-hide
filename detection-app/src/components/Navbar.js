/**
 * Navigation Bar Component
 * Provides navigation between different processing modes
 */

import React from 'react';
import styled from 'styled-components';
import { mediaQueries, layoutHelpers } from '../styles/mediaKit';

const NavbarContainer = styled.nav`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  overflow: hidden;
  width: 100%;
  max-width: 100vw;
  box-sizing: border-box;
  border-radius: 0 0 12px 12px;
  margin-bottom: 3px;
`;

const NavContent = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  min-height: 50px;
  gap: 6px;
  width: 100%;
  max-width: 100%;
  padding: 0 12px;
  box-sizing: border-box;
  overflow: hidden;
  
  ${mediaQueries.sm} {
    height: 55px;
    min-height: 55px;
    gap: 8px;
    padding: 0 16px;
  }
  
  ${mediaQueries.md} {
    gap: 10px;
    padding: 0 20px;
  }
  
  ${mediaQueries.lg} {
    height: 60px;
    min-height: 60px;
    gap: 12px;
    padding: 0 24px;
  }
  
  ${mediaQueries.xl} {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 32px;
  }
`;

const Logo = styled.div`
  color: white;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(45deg, #ffffff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  flex-shrink: 0;
  
  ${mediaQueries.sm} {
    font-size: 18px;
  }
  
  ${mediaQueries.md} {
    font-size: 20px;
  }
  
  ${mediaQueries.lg} {
    font-size: 22px;
  }
  
  ${mediaQueries.xl} {
    font-size: 24px;
  }
`;

const NavItems = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: nowrap;
  flex-shrink: 1;
  min-width: 0;
  
  ${mediaQueries.sm} {
    gap: 6px;
  }
  
  ${mediaQueries.md} {
    gap: 8px;
  }
  
  ${mediaQueries.lg} {
    gap: 10px;
  }
`;

const NavButton = styled.button`
  background: ${props => props.active ? 'rgba(255,255,255,0.2)' : 'transparent'};
  color: white;
  border: 1px solid ${props => props.active ? 'white' : 'transparent'};
  padding: 3px 6px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 0;
  
  ${mediaQueries.sm} {
    padding: 4px 8px;
    font-size: 11px;
    gap: 4px;
  }
  
  ${mediaQueries.md} {
    padding: 5px 10px;
    font-size: 12px;
    gap: 4px;
  }
  
  ${mediaQueries.lg} {
    padding: 6px 12px;
    font-size: 13px;
    gap: 5px;
  }
  
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
  gap: 4px;
  color: white;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 3px 6px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 0;
  flex-shrink: 1;
  max-width: 100px;
  height: 24px;
  overflow: hidden;
  
  ${mediaQueries.sm} {
    max-width: 120px;
    padding: 4px 8px;
    font-size: 11px;
    height: 26px;
  }
  
  ${mediaQueries.md} {
    max-width: 140px;
    padding: 5px 10px;
    font-size: 12px;
    height: 28px;
  }
  
  ${mediaQueries.lg} {
    max-width: 160px;
    padding: 6px 12px;
    font-size: 13px;
    height: 30px;
  }
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
          🛡️ Iden-Hide
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
          <span style={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
            fontWeight: '500',
            flex: 1
          }}>
            {isProcessing 
              ? `🔄 ${processedCount}/${totalCount}`
              : processingStatus === 'success' 
                ? `✅ ${totalCount} image${totalCount !== 1 ? 's' : ''}`
                : '🚀 Ready'
            }
          </span>
        </StatusIndicator>
      </NavContent>
    </NavbarContainer>
  );
};

export default Navbar;
