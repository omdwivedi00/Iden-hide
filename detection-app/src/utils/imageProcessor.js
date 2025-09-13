/**
 * Image Processing Utilities
 * Handles image manipulation and visualization
 */

export class ImageProcessor {
  /**
   * Draw bounding boxes on an image
   * @param {HTMLImageElement} image - Source image
   * @param {Array} detections - Array of detection objects
   * @param {Object} options - Drawing options
   */
  static drawBoundingBoxes(image, detections, options = {}) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match image
    canvas.width = image.width;
    canvas.height = image.height;
    
    // Draw the original image
    ctx.drawImage(image, 0, 0);
    
    // Configure drawing options
    const config = {
      faceColor: options.faceColor || '#00FF00',
      plateColor: options.plateColor || '#FF0000',
      lineWidth: options.lineWidth || 3,
      fontSize: options.fontSize || 16,
      fontFamily: options.fontFamily || 'Arial',
      showConfidence: options.showConfidence !== false,
      ...options
    };
    
    // Draw each detection
    detections.forEach((detection, index) => {
      const { x1, y1, x2, y2, label, confidence } = detection;
      
      // Choose color based on label
      const color = label === 'face' ? config.faceColor : config.plateColor;
      
      // Draw bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = config.lineWidth;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      
      // Draw label with confidence
      if (config.showConfidence) {
        const labelText = `${label}: ${confidence.toFixed(3)}`;
        const textMetrics = ctx.measureText(labelText);
        const textWidth = textMetrics.width;
        const textHeight = config.fontSize;
        
        // Draw background rectangle for text
        ctx.fillStyle = color;
        ctx.fillRect(x1, y1 - textHeight - 5, textWidth + 10, textHeight + 5);
        
        // Draw text
        ctx.fillStyle = '#FFFFFF';
        ctx.font = `${config.fontSize}px ${config.fontFamily}`;
        ctx.fillText(labelText, x1 + 5, y1 - 5);
      }
    });
    
    return canvas;
  }

  /**
   * Create a comparison view of original and processed images
   * @param {HTMLImageElement} originalImage - Original image
   * @param {HTMLImageElement} processedImage - Processed image
   * @param {string} title - Comparison title
   */
  static createComparison(originalImage, processedImage, title = 'Comparison') {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Calculate dimensions
    const maxWidth = 800;
    const maxHeight = 600;
    const imageWidth = Math.min(originalImage.width, maxWidth / 2);
    const imageHeight = Math.min(originalImage.height, maxHeight / 2);
    
    // Set canvas size
    canvas.width = imageWidth * 2 + 20; // 20px gap between images
    canvas.height = imageHeight + 60; // Extra space for title
    
    // Draw title
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, canvas.width / 2, 30);
    
    // Draw original image
    ctx.drawImage(originalImage, 0, 50, imageWidth, imageHeight);
    
    // Draw "Original" label
    ctx.fillStyle = '#666666';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Original', imageWidth / 2, imageHeight + 45);
    
    // Draw processed image
    ctx.drawImage(processedImage, imageWidth + 20, 50, imageWidth, imageHeight);
    
    // Draw "Processed" label
    ctx.fillText('Processed', imageWidth + 20 + imageWidth / 2, imageHeight + 45);
    
    return canvas;
  }

  /**
   * Resize image while maintaining aspect ratio
   * @param {HTMLImageElement} image - Source image
   * @param {number} maxWidth - Maximum width
   * @param {number} maxHeight - Maximum height
   */
  static resizeImage(image, maxWidth, maxHeight) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Calculate new dimensions
    let { width, height } = image;
    const aspectRatio = width / height;
    
    if (width > maxWidth) {
      width = maxWidth;
      height = width / aspectRatio;
    }
    
    if (height > maxHeight) {
      height = maxHeight;
      width = height * aspectRatio;
    }
    
    // Set canvas size and draw resized image
    canvas.width = width;
    canvas.height = height;
    ctx.drawImage(image, 0, 0, width, height);
    
    return canvas;
  }

  /**
   * Create a thumbnail of an image
   * @param {HTMLImageElement} image - Source image
   * @param {number} size - Thumbnail size (square)
   */
  static createThumbnail(image, size = 150) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = size;
    canvas.height = size;
    
    // Calculate crop dimensions to maintain aspect ratio
    const aspectRatio = image.width / image.height;
    let sourceX = 0;
    let sourceY = 0;
    let sourceWidth = image.width;
    let sourceHeight = image.height;
    
    if (aspectRatio > 1) {
      // Image is wider than tall
      sourceWidth = image.height;
      sourceX = (image.width - sourceWidth) / 2;
    } else {
      // Image is taller than wide
      sourceHeight = image.width;
      sourceY = (image.height - sourceHeight) / 2;
    }
    
    // Draw cropped and resized image
    ctx.drawImage(
      image,
      sourceX, sourceY, sourceWidth, sourceHeight,
      0, 0, size, size
    );
    
    return canvas;
  }

  /**
   * Load image from file
   * @param {File} file - Image file
   */
  static loadImage(file) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  }

  /**
   * Load image from URL
   * @param {string} url - Image URL
   */
  static loadImageFromUrl(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
  }

  /**
   * Convert canvas to image file
   * @param {HTMLCanvasElement} canvas - Canvas element
   * @param {string} filename - Output filename
   * @param {string} type - MIME type
   * @param {number} quality - Image quality (0-1)
   */
  static canvasToFile(canvas, filename, type = 'image/jpeg', quality = 0.9) {
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        const file = new File([blob], filename, { type });
        resolve(file);
      }, type, quality);
    });
  }
}
