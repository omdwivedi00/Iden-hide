/**
 * Detection Controls Component
 * Provides controls for detection and blur options
 */

import React from 'react';
import styled from 'styled-components';
import { mediaQueries } from '../styles/mediaKit';

const ControlsContainer = styled.div`
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
`;

const SectionTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 0.875rem;
  font-weight: 600;
  
  ${mediaQueries.sm} {
    font-size: 1rem;
  }
  
  ${mediaQueries.md} {
    font-size: 1.125rem;
  }
`;

const ControlGroup = styled.div`
  margin-bottom: 12px;
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  cursor: pointer;
  font-weight: 500;
  color: #555;
  font-size: 0.75rem;
  
  ${mediaQueries.sm} {
    font-size: 0.8rem;
  }
  
  ${mediaQueries.md} {
    font-size: 0.875rem;
  }
`;

const Checkbox = styled.input`
  margin-right: 8px;
  transform: scale(1.2);
`;

const SliderContainer = styled.div`
  margin-left: 20px;
`;

const SliderLabel = styled.label`
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
`;

const Slider = styled.input`
  width: 100%;
  margin-bottom: 5px;
`;

const SliderValue = styled.span`
  font-size: 12px;
  color: #999;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 20px;
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
`;

const SecondaryButton = styled(Button)`
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
  }
`;

const DangerButton = styled(Button)`
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
  }
`;

const DetectionControls = ({
  detectFace,
  detectLicensePlate,
  enableBlur,
  faceBlurStrength,
  plateBlurStrength,
  showBoundingBoxes,
  showLabels,
  showBlurred,
  onDetectFaceChange,
  onDetectLicensePlateChange,
  onEnableBlurChange,
  onFaceBlurStrengthChange,
  onPlateBlurStrengthChange,
  onShowBoundingBoxesChange,
  onShowLabelsChange,
  onShowBlurredChange,
  onDetect,
  onBlur,
  onClear,
  isProcessing,
  hasFiles
}) => {
  return (
    <ControlsContainer>
      <SectionTitle>Detection Options</SectionTitle>
      
      <ControlGroup>
        <Label>
          <Checkbox
            type="checkbox"
            checked={detectFace}
            onChange={onDetectFaceChange}
            disabled={isProcessing}
          />
          Detect Faces
        </Label>
        
        <Label>
          <Checkbox
            type="checkbox"
            checked={detectLicensePlate}
            onChange={onDetectLicensePlateChange}
            disabled={isProcessing}
          />
          Detect License Plates
        </Label>
      </ControlGroup>

      <ControlGroup>
        <Label>
          <Checkbox
            type="checkbox"
            checked={enableBlur}
            onChange={onEnableBlurChange}
            disabled={isProcessing}
          />
          Enable Privacy Blur
        </Label>
        
        {enableBlur && (
          <SliderContainer>
            <SliderLabel>
              Face Blur Strength: {faceBlurStrength}
            </SliderLabel>
            <Slider
              type="range"
              min="1"
              max="100"
              value={faceBlurStrength}
              onChange={(e) => onFaceBlurStrengthChange(parseInt(e.target.value))}
              disabled={isProcessing}
            />
            <SliderValue>1 (Light) - 100 (Strong)</SliderValue>
            
            <SliderLabel>
              License Plate Blur Strength: {plateBlurStrength}
            </SliderLabel>
            <Slider
              type="range"
              min="1"
              max="100"
              value={plateBlurStrength}
              onChange={(e) => onPlateBlurStrengthChange(parseInt(e.target.value))}
              disabled={isProcessing}
            />
            <SliderValue>1 (Light) - 100 (Strong)</SliderValue>
          </SliderContainer>
        )}
      </ControlGroup>

      <ControlGroup>
        <SectionTitle style={{ fontSize: '16px', marginBottom: '10px' }}>Display Options</SectionTitle>
        
        <Label>
          <Checkbox
            type="checkbox"
            checked={showBoundingBoxes}
            onChange={onShowBoundingBoxesChange}
            disabled={isProcessing}
          />
          Show Bounding Boxes
        </Label>
        
        <Label>
          <Checkbox
            type="checkbox"
            checked={showLabels}
            onChange={onShowLabelsChange}
            disabled={isProcessing || !showBoundingBoxes}
          />
          Show Labels & Confidence
        </Label>
        
        <Label>
          <Checkbox
            type="checkbox"
            checked={showBlurred}
            onChange={onShowBlurredChange}
            disabled={isProcessing}
          />
          Show Blurred Images
        </Label>
      </ControlGroup>

      <ButtonGroup>
        <PrimaryButton
          onClick={onDetect}
          disabled={!hasFiles || isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Detect Objects'}
        </PrimaryButton>
        
        {enableBlur && (
          <SecondaryButton
            onClick={onBlur}
            disabled={!hasFiles || isProcessing}
          >
            {isProcessing ? 'Blurring...' : 'Blur Objects'}
          </SecondaryButton>
        )}
        
        <DangerButton
          onClick={onClear}
          disabled={isProcessing}
        >
          Clear All
        </DangerButton>
      </ButtonGroup>
    </ControlsContainer>
  );
};

export default DetectionControls;
