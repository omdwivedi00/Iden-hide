# License Plate Detection Improvements

## Overview
Updated the license plate detection system to select the license plate with maximum confidence when multiple plates are detected within a single vehicle.

## Changes Made

### 1. Enhanced `process_image_plates_only()` Method
- **Before**: Returned all detected license plates from each vehicle
- **After**: Selects only the plate with highest confidence per vehicle

### 2. Added Confidence Filtering
- Filters out plates below the confidence threshold before selection
- Ensures only valid detections are considered

### 3. Added Debugging Support
- New `process_image_all_plates()` method for debugging
- Optional `return_all_plates` parameter in `detect_license_plates()`
- Detailed logging when multiple plates are found

### 4. Improved Logging
- Logs when multiple plates are detected and best one is selected
- Shows confidence scores for transparency
- Reports filtered plates due to low confidence

## Key Features

### Maximum Confidence Selection
```python
# Sort plates by confidence in descending order
plates_sorted = sorted(valid_plates, key=lambda x: x['confidence'], reverse=True)
best_plate = plates_sorted[0]  # Take the plate with highest confidence
```

### Confidence Filtering
```python
# Filter out plates with very low confidence
valid_plates = [p for p in plates if p['confidence'] >= self.plate_conf_threshold]
```

### Debugging Mode
```python
# Get all plates (for debugging)
all_plates = detector.detect_license_plates(image, return_all_plates=True)

# Get only best plate per vehicle (default)
best_plates = detector.detect_license_plates(image, return_all_plates=False)
```

## Benefits

1. **Reduced False Positives**: Eliminates duplicate detections from the same vehicle
2. **Higher Accuracy**: Selects the most confident detection
3. **Better Performance**: Reduces processing overhead by filtering low-confidence detections
4. **Debugging Support**: Easy to compare all detections vs. filtered results
5. **Transparency**: Clear logging of selection process

## Usage Examples

### Basic Usage (Default - Max Confidence)
```python
from detect_lp import DetectLP

detector = DetectLP()
plates = detector.detect_license_plates(image)  # Returns best plate per vehicle
```

### Debugging Mode (All Plates)
```python
detector = DetectLP()
all_plates = detector.detect_license_plates(image, return_all_plates=True)
```

### Testing
```bash
# Run the test script
python test_lp_max_confidence.py
```

## Configuration

### Confidence Thresholds
- `vehicle_conf_threshold = 0.3` - Minimum confidence for vehicle detection
- `plate_conf_threshold = 0.2` - Minimum confidence for license plate detection

### Vehicle Classes
- `vehicle_classes = [2, 3, 5, 7]` - car, motorcycle, bus, truck

## Logging Output

When multiple plates are detected in a vehicle:
```
Vehicle 1: Found 3 valid plates, selected best with confidence 0.856
Vehicle 2: Found 2 plates, 1 filtered out due to low confidence
```

## Testing

The `test_lp_max_confidence.py` script provides comprehensive testing:
- Tests both max confidence and all plates modes
- Compares results between modes
- Tests different confidence thresholds
- Creates test images for validation

## Backward Compatibility

- Default behavior remains the same (max confidence selection)
- Existing code will work without changes
- New optional parameters are backward compatible
