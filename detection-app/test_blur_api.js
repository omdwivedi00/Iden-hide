#!/usr/bin/env node

/**
 * Test script to debug blur API issue
 * Mimics what the React app does
 */

const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

async function testBlurAPI() {
  console.log('🧪 Testing Blur API...\n');

  try {
    // Test 1: Check if server is running
    console.log('1️⃣ Checking server health...');
    const healthResponse = await axios.get(`${API_BASE_URL}/health`);
    console.log('✅ Server is running:', healthResponse.data);

    // Test 2: Test detection API first
    console.log('\n2️⃣ Testing detection API...');
    const testImagePath = '../unified_detection_production/test_images/frame_000000.png';
    
    if (!fs.existsSync(testImagePath)) {
      console.log('❌ Test image not found:', testImagePath);
      return;
    }

    const formData = new FormData();
    formData.append('file', fs.createReadStream(testImagePath));
    formData.append('detect_face', 'true');
    formData.append('detect_license_plate', 'true');

    const detectionResponse = await axios.post(`${API_BASE_URL}/detect`, formData, {
      headers: {
        ...formData.getHeaders()
      }
    });

    console.log('✅ Detection successful:', {
      faces: detectionResponse.data.total_faces,
      plates: detectionResponse.data.total_license_plates,
      processing_time: detectionResponse.data.processing_time_ms
    });

    // Test 3: Test blur API
    console.log('\n3️⃣ Testing blur API...');
    const blurFormData = new FormData();
    blurFormData.append('file', fs.createReadStream(testImagePath));
    blurFormData.append('detect_face', 'true');
    blurFormData.append('detect_license_plate', 'true');
    blurFormData.append('face_blur_strength', '25');
    blurFormData.append('plate_blur_strength', '20');

    const blurResponse = await axios.post(`${API_BASE_URL}/blur`, blurFormData, {
      headers: {
        ...blurFormData.getHeaders()
      }
    });

    console.log('✅ Blur successful:', {
      success: blurResponse.data.success,
      message: blurResponse.data.message,
      blurred_image_path: blurResponse.data.blurred_image_path,
      detections_applied: blurResponse.data.detections_applied,
      processing_time: blurResponse.data.processing_time_ms
    });

    // Test 4: Check if blurred image exists
    console.log('\n4️⃣ Checking blurred image...');
    const blurredPath = `../unified_detection_production/${blurResponse.data.blurred_image_path}`;
    if (fs.existsSync(blurredPath)) {
      const stats = fs.statSync(blurredPath);
      console.log('✅ Blurred image exists:', {
        path: blurredPath,
        size: stats.size,
        created: stats.birthtime
      });
    } else {
      console.log('❌ Blurred image not found:', blurredPath);
    }

    // Test 5: Test download endpoint
    console.log('\n5️⃣ Testing download endpoint...');
    const filename = blurResponse.data.blurred_image_path.split('/').pop();
    try {
      const downloadResponse = await axios.get(`${API_BASE_URL}/download/${filename}`, {
        responseType: 'arraybuffer'
      });
      console.log('✅ Download successful:', {
        filename: filename,
        size: downloadResponse.data.length,
        content_type: downloadResponse.headers['content-type']
      });
    } catch (downloadError) {
      console.log('❌ Download failed:', downloadError.response?.data || downloadError.message);
    }

    console.log('\n🎉 All tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

// Run the test
testBlurAPI();
