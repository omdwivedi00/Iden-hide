/**
 * File Utilities Module
 * Handles file operations and validation
 */

import fileDownload from 'js-file-download';

export class FileUtils {
  /**
   * Validate if file is an image
   * @param {File} file - File to validate
   */
  static isValidImage(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    return validTypes.includes(file.type);
  }

  /**
   * Get file size in human readable format
   * @param {number} bytes - File size in bytes
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Create a preview URL for an image file
   * @param {File} file - Image file
   */
  static createPreviewUrl(file) {
    return URL.createObjectURL(file);
  }

  /**
   * Revoke preview URL to free memory
   * @param {string} url - Preview URL to revoke
   */
  static revokePreviewUrl(url) {
    URL.revokeObjectURL(url);
  }

  /**
   * Download a file
   * @param {Blob} blob - File blob
   * @param {string} filename - Filename for download
   */
  static downloadFile(blob, filename) {
    try {
      // Validate inputs
      if (!blob) {
        throw new Error('No blob data provided for download');
      }
      
      if (!filename) {
        throw new Error('No filename provided for download');
      }
      
      // Check if blob is valid
      if (!(blob instanceof Blob)) {
        throw new Error('Invalid blob data - expected Blob object');
      }
      
      if (blob.size === 0) {
        throw new Error('Cannot download empty file');
      }
      
      console.log(`Downloading file: ${filename} (${blob.size} bytes)`);
      
      // Use js-file-download library for reliable downloads
      fileDownload(blob, filename);
      
      console.log(`Download initiated: ${filename}`);
      
    } catch (error) {
      console.error('Download file error:', error);
      throw new Error(`Download failed: ${error.message}`);
    }
  }

  /**
   * Get file extension
   * @param {string} filename - Filename
   */
  static getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
  }

  /**
   * Check if file is supported image format
   * @param {string} filename - Filename to check
   */
  static isSupportedImage(filename) {
    const supportedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
    const extension = this.getFileExtension(filename);
    return supportedExtensions.includes(extension);
  }

  /**
   * Validate multiple files
   * @param {FileList} files - Files to validate
   */
  static validateFiles(files) {
    const validFiles = [];
    const invalidFiles = [];
    
    Array.from(files).forEach(file => {
      if (this.isValidImage(file)) {
        validFiles.push(file);
      } else {
        invalidFiles.push({
          name: file.name,
          reason: 'Invalid file type. Only images are supported.'
        });
      }
    });
    
    return { validFiles, invalidFiles };
  }

  /**
   * Create a canvas element for image manipulation
   * @param {number} width - Canvas width
   * @param {number} height - Canvas height
   */
  static createCanvas(width, height) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    return canvas;
  }

  /**
   * Convert canvas to blob
   * @param {HTMLCanvasElement} canvas - Canvas element
   * @param {string} type - MIME type
   * @param {number} quality - Image quality (0-1)
   */
  static canvasToBlob(canvas, type = 'image/jpeg', quality = 0.9) {
    return new Promise((resolve) => {
      canvas.toBlob(resolve, type, quality);
    });
  }
}
