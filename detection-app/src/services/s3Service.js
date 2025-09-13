/**
 * S3 Service
 * Handles S3 image processing API calls
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const s3ApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for S3 operations
  headers: {
    'Content-Type': 'application/json',
  },
});

export const s3Service = {
  /**
   * Test S3 credentials
   * @param {Object} credentials - AWS credentials
   * @returns {Promise<Object>} Test result
   */
  async testCredentials(credentials) {
    try {
      const params = new URLSearchParams({
        aws_access_key_id: credentials.aws_access_key_id,
        aws_secret_access_key: credentials.aws_secret_access_key,
      });
      
      if (credentials.aws_session_token) {
        params.append('aws_session_token', credentials.aws_session_token);
      }

      const response = await s3ApiClient.get(`/s3/test-credentials?${params}`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('S3 credentials test error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message 
      };
    }
  },

  /**
   * Process a single image from S3
   * @param {Object} requestData - S3 processing request
   * @returns {Promise<Object>} Processing result
   */
  async processSingleImage(requestData) {
    try {
      const response = await s3ApiClient.post('/s3/process-single', requestData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('S3 single image processing error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message 
      };
    }
  },

  /**
   * Process all images in an S3 folder
   * @param {Object} requestData - S3 folder processing request
   * @returns {Promise<Object>} Processing result
   */
  async processFolder(requestData) {
    try {
      const response = await s3ApiClient.post('/s3/process-folder', requestData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('S3 folder processing error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message 
      };
    }
  },

  /**
   * Get S3 folder contents (custom endpoint for listing files)
   * @param {Object} credentials - AWS credentials
   * @param {string} s3FolderPath - S3 folder path
   * @returns {Promise<Object>} Folder contents
   */
  async listS3Folder(credentials, s3FolderPath) {
    try {
      const response = await s3ApiClient.post('/s3/list-folder', {
        credentials,
        s3_folder_path: s3FolderPath
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('S3 folder listing error:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || error.message 
      };
    }
  },

  /**
   * Get presigned URL for viewing S3 image
   * @param {Object} credentials - AWS credentials
   * @param {string} s3Uri - S3 URI of the image
   * @param {number} expiration - URL expiration time in seconds (default: 300)
   * @returns {Promise<Object>} Presigned URL result
   */
  async viewS3Image(credentials, s3Uri, expiration = 300) {
    try {
      const response = await s3ApiClient.post('/s3/view-image', {
        credentials,
        s3_uri: s3Uri,
        expiration
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('S3 image view error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || error.message 
      };
    }
  }
};

export default s3Service;
