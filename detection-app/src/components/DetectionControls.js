/**
 * Detection Controls Component
 * Provides controls for detection and blur options
 */

import React from 'react';
import styled from 'styled-components';
import { mediaQueries } from '../styles/mediaKit';

const ControlsContainer = styled.div`
  background: rgba(12, 16, 26, 0.6);
  border-radius: 14px;
  padding: 16px;
  margin: 12px 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
`;

const SectionTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #e9eefc;
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
  color: rgba(233, 238, 252, 0.75);
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
  color: rgba(233, 238, 252, 0.65);
`;

const Slider = styled.input`
  width: 100%;
  margin-bottom: 5px;
`;

const SliderValue = styled.span`
  font-size: 12px;
  color: rgba(233, 238, 252, 0.5);
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
  background: linear-gradient(135deg, #627eff 0%, #8f6bff 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(98, 126, 255, 0.3);
`;

const SecondaryButton = styled(Button)`
  background: linear-gradient(135deg, #27c97c 0%, #2fa5ff 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(39, 201, 124, 0.3);
`;

const DangerButton = styled(Button)`
  background: linear-gradient(135deg, #ff6b6b 0%, #c81d3a 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
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
  hasFiles,
  showDisplayOptions = true
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

      {showDisplayOptions && (
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
      )}

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
