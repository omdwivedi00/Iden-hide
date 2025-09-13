/**
 * Detection Controls Component
 * Provides controls for detection and blur options
 */

import React from 'react';
import styled from 'styled-components';

const ControlsContainer = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
`;

const ControlGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  cursor: pointer;
  font-weight: 500;
  color: #555;
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
  background: #007bff;
  color: white;
  
  &:hover:not(:disabled) {
    background: #0056b3;
  }
`;

const SecondaryButton = styled(Button)`
  background: #6c757d;
  color: white;
  
  &:hover:not(:disabled) {
    background: #545b62;
  }
`;

const DangerButton = styled(Button)`
  background: #dc3545;
  color: white;
  
  &:hover:not(:disabled) {
    background: #c82333;
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
