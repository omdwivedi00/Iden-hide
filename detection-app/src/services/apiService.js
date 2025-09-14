/**
 * API Service Module
 * Handles all API calls to the detection backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for image processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

class ApiService {
  /**
   * Check if the API server is healthy
   */
  async checkHealth() {
    try {
      const response = await apiClient.get('/health');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get API information
   */
  async getApiInfo() {
    try {
      const response = await apiClient.get('/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Detect objects in an image
   * @param {File} imageFile - The image file to process
   * @param {boolean} detectFace - Whether to detect faces
   * @param {boolean} detectLicensePlate - Whether to detect license plates
   */
  async detectObjects(imageFile, detectFace = true, detectLicensePlate = true) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('detect_face', detectFace);
      formData.append('detect_license_plate', detectLicensePlate);

      const response = await apiClient.post('/detect', formData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  }

  /**
   * Blur objects in an image
   * @param {File} imageFile - The image file to process
   * @param {boolean} detectFace - Whether to detect and blur faces
   * @param {boolean} detectLicensePlate - Whether to detect and blur license plates
   * @param {number} faceBlurStrength - Blur strength for faces (1-100)
   * @param {number} plateBlurStrength - Blur strength for license plates (1-100)
   */
  async blurObjects(imageFile, detectFace = true, detectLicensePlate = true, 
                   faceBlurStrength = 25, plateBlurStrength = 20) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('detect_face', detectFace);
      formData.append('detect_license_plate', detectLicensePlate);
      formData.append('face_blur_strength', faceBlurStrength);
      formData.append('plate_blur_strength', plateBlurStrength);

      const response = await apiClient.post('/blur', formData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  }

  /**
   * Get list of output files
   */
  async getOutputFiles() {
    try {
      const response = await apiClient.get('/outputs');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Download a processed image directly using js-file-download
   * @param {string} filename - The filename to download
   */
  async downloadImage(filename) {
    try {
      console.log(`Attempting to download: ${filename}`);
      
      const response = await apiClient.get(`/download/${filename}`, {
        responseType: 'blob'
      });
      
      // Check if response is successful
      if (!response || !response.data) {
        throw new Error('No data received from server');
      }
      
      // Validate that we have blob data
      if (!(response.data instanceof Blob)) {
        console.error('Response data is not a Blob:', response.data);
        throw new Error('Invalid response format - expected blob data');
      }
      
      // Check if blob has content
      if (response.data.size === 0) {
        throw new Error('Received empty file from server');
      }
      
      console.log(`Download successful: ${response.data.size} bytes`);
      
      // Return the blob directly for js-file-download
      return { success: true, data: { blob: response.data, filename, size: response.data.size } };
    } catch (error) {
      console.error('Download error:', error);
      
      // Provide more specific error messages
      let errorMessage = error.message;
      if (error.response) {
        if (error.response.status === 404) {
          errorMessage = `File '${filename}' not found on server`;
        } else if (error.response.status === 500) {
          errorMessage = 'Server error while downloading file';
        } else {
          errorMessage = `Server error: ${error.response.status} - ${error.response.statusText}`;
        }
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = 'Network error - cannot connect to server';
      }
      
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Process multiple images from a folder
   * @param {FileList} files - List of image files
   * @param {Object} options - Processing options
   */
  async processBatch(files, options = {}) {
    const results = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        // Detect objects
        const detectionResult = await this.detectObjects(
          file, 
          options.detectFace, 
          options.detectLicensePlate
        );
        
        if (detectionResult.success) {
          // Blur objects if requested
          let blurResult = null;
          if (options.enableBlur) {
            blurResult = await this.blurObjects(
              file,
              options.detectFace,
              options.detectLicensePlate,
              options.faceBlurStrength,
              options.plateBlurStrength
            );
          }
          
          results.push({
            filename: file.name,
            detection: detectionResult.data,
            blur: blurResult?.data || null,
            success: true
          });
        } else {
          results.push({
            filename: file.name,
            error: detectionResult.error,
            success: false
          });
        }
      } catch (error) {
        results.push({
          filename: file.name,
          error: error.message,
          success: false
        });
      }
    }
    
    return { success: true, data: results };
  }

  /**
   * Process multiple images in parallel for faster processing
   * @param {FileList} files - List of image files
   * @param {Object} options - Processing options
   */
  async processBatchParallel(files, options = {}) {
    try {
      const formData = new FormData();
      
      // Add all files
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
      
      // Add processing options
      formData.append('detect_face', options.detectFace !== false);
      formData.append('detect_license_plate', options.detectLicensePlate !== false);
      formData.append('enable_blur', options.enableBlur || false);
      formData.append('face_blur_strength', options.faceBlurStrength || 25);
      formData.append('plate_blur_strength', options.plateBlurStrength || 20);
      formData.append('max_workers', options.maxWorkers || 4);

      // Set longer timeout for parallel processing
      const response = await apiClient.post('/process-parallel', formData, {
        timeout: 300000, // 5 minutes timeout
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Parallel processing error:', error);
      
      let errorMessage = 'Parallel processing failed';
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout - parallel processing took too long';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;
