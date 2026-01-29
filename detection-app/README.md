# 🔍 Unified Detection System - React Frontend

A modern React.js application for face and license plate detection with privacy protection features.

## 🚀 Features

- **Drag & Drop Upload**: Easy file selection with drag and drop support
- **Real-time Detection**: Face and license plate detection using AI
- **Privacy Protection**: Blur detected objects with customizable strength
- **Image Gallery**: View and manage processed images
- **Download Results**: Download original and processed images
- **Responsive Design**: Works on desktop and mobile devices
- **Modular Architecture**: Clean, maintainable code structure

## 📁 Project Structure

```
detection-app/
├── public/
│   └── index.html
├── src/
│   ├── components/          # React components
│   │   ├── FileUpload.js    # File upload component
│   │   ├── DetectionControls.js  # Detection settings
│   │   ├── ImageGallery.js  # Image display and management
│   │   └── StatusBar.js     # Status and progress display
│   ├── services/            # API services
│   │   └── apiService.js    # Backend API integration
│   ├── utils/               # Utility functions
│   │   └── fileUtils.js     # File operations
│   ├── App.js              # Main application component
│   └── index.js            # Application entry point
├── package.json
└── README.md
```

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   cd detection-app
   npm install
   ```

2. **Start the Backend Server**:
   ```bash
   # In another terminal, start the detection API server
   cd ..
   uvicorn unified_detection.api.app:create_app --factory --host 0.0.0.0 --port 8000
   ```

3. **Start the React App**:
   ```bash
   npm start
   ```

4. **Open in Browser**:
   Navigate to `http://localhost:3000`

## 🎯 Usage

### 1. Upload Images
- Drag and drop images onto the upload area
- Or click to select files from your computer
- Supports JPG, PNG, GIF, and WebP formats

### 2. Configure Detection
- **Detect Faces**: Toggle face detection on/off
- **Detect License Plates**: Toggle license plate detection on/off
- **Enable Privacy Blur**: Apply blur to detected objects
- **Blur Strength**: Adjust blur intensity (1-100)

### 3. Process Images
- **Detect Objects**: Run detection without blur
- **Blur Objects**: Run detection with privacy blur
- **Clear All**: Remove all files and results

### 4. View Results
- **Image Gallery**: See all processed images
- **Detection Stats**: View face and license plate counts
- **Confidence Scores**: See detection confidence levels
- **Download**: Download original or blurred images

## 🔧 Configuration

### API Configuration
Set the API URL in your environment:

```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### Customization
- **Colors**: Modify styled-components in each component
- **API Endpoints**: Update `apiService.js`
- **File Types**: Modify `fileUtils.js`

## 📱 Components

### FileUpload
- Drag and drop file selection
- File validation and preview
- Multiple file support
- Error handling

### DetectionControls
- Detection option toggles
- Blur strength sliders
- Action buttons
- Processing state management

### ImageGallery
- Grid layout display
- Image preview and modal
- Download and delete actions
- Detection statistics

### StatusBar
- Processing status display
- Progress indicators
- Success/error messages
- Auto-dismiss functionality

## 🔌 API Integration

The app integrates with the Unified Detection Production System:

- **Detection API**: `/detect` - Detect objects in images
- **Blur API**: `/blur` - Apply privacy blur
- **Health Check**: `/health` - Server status
- **File Management**: `/outputs`, `/download` - File operations

## 🎨 Styling

Built with styled-components for:
- Component-scoped styling
- Dynamic theming
- Responsive design
- Clean, maintainable CSS

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
```bash
# Build the app
npm run build

# Deploy the 'build' folder to your hosting service
# Examples: Netlify, Vercel, GitHub Pages, AWS S3
```

### Environment Variables
```bash
# Production API URL
REACT_APP_API_URL=https://your-api-domain.com
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the detection server is running
   - Check the API URL in `.env`
   - Verify CORS settings

2. **File Upload Issues**
   - Check file format (JPG, PNG, GIF, WebP)
   - Ensure file size is reasonable
   - Check browser console for errors

3. **Image Processing Errors**
   - Verify server is running
   - Check network connection
   - Review server logs

### Debug Mode
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
```

## 📚 Development

### Adding New Features
1. Create component in `src/components/`
2. Add utility functions in `src/utils/`
3. Update API service if needed
4. Integrate into main App component

### Code Style
- Use functional components with hooks
- Follow React best practices
- Use styled-components for styling
- Maintain modular architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the TELUS Hackathon.

---

**Happy Detecting!** 🔍👤🚗
