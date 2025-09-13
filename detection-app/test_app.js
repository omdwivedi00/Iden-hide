#!/usr/bin/env node

/**
 * Test script for React Detection App
 * Verifies the app structure and dependencies
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testing React Detection App Structure...\n');

// Check if required files exist
const requiredFiles = [
  'package.json',
  'public/index.html',
  'src/App.js',
  'src/index.js',
  'src/services/apiService.js',
  'src/utils/fileUtils.js',
  'src/utils/imageProcessor.js',
  'src/components/FileUpload.js',
  'src/components/DetectionControls.js',
  'src/components/ImageGallery.js',
  'src/components/ImageViewer.js',
  'src/components/StatusBar.js'
];

let allFilesExist = true;

console.log('📁 Checking required files:');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - MISSING`);
    allFilesExist = false;
  }
});

console.log('\n📦 Checking package.json:');
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  
  const requiredDeps = [
    'react',
    'react-dom',
    'react-scripts',
    'axios',
    'react-dropzone',
    'react-toastify',
    'styled-components',
    'lucide-react'
  ];
  
  console.log('  Dependencies:');
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`    ✅ ${dep}: ${packageJson.dependencies[dep]}`);
    } else {
      console.log(`    ❌ ${dep} - MISSING`);
      allFilesExist = false;
    }
  });
  
  console.log('  Scripts:');
  const requiredScripts = ['start', 'build', 'test'];
  requiredScripts.forEach(script => {
    if (packageJson.scripts && packageJson.scripts[script]) {
      console.log(`    ✅ ${script}: ${packageJson.scripts[script]}`);
    } else {
      console.log(`    ❌ ${script} - MISSING`);
      allFilesExist = false;
    }
  });
  
} catch (error) {
  console.log(`  ❌ Error reading package.json: ${error.message}`);
  allFilesExist = false;
}

console.log('\n🔍 Checking component structure:');
const componentFiles = [
  'src/components/FileUpload.js',
  'src/components/DetectionControls.js', 
  'src/components/ImageGallery.js',
  'src/components/ImageViewer.js',
  'src/components/StatusBar.js'
];

componentFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    if (content.includes('export default')) {
      console.log(`  ✅ ${file} - Has default export`);
    } else {
      console.log(`  ⚠️  ${file} - Missing default export`);
    }
  }
});

console.log('\n🎯 Summary:');
if (allFilesExist) {
  console.log('✅ All required files and dependencies are present!');
  console.log('\n🚀 Next steps:');
  console.log('1. Install dependencies: npm install');
  console.log('2. Start the detection API server: cd ../unified_detection_production && python main.py');
  console.log('3. Start the React app: npm start');
  console.log('4. Open http://localhost:3000 in your browser');
} else {
  console.log('❌ Some files or dependencies are missing!');
  console.log('Please check the errors above and fix them.');
  process.exit(1);
}

console.log('\n🎉 React Detection App is ready!');
