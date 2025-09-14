# Iden-Hide AI Anonymization Engine - System Architecture

## ⚠️ Security Notice

**This is a rapid development prototype built in 24 hours for a hackathon. Security has not been implemented as the primary focus was on core functionality and AI detection capabilities. The next critical step is implementing comprehensive security measures including:**

- Authentication and authorization
- Input validation and sanitization
- Rate limiting and DDoS protection
- Data encryption at rest and in transit
- Secure credential management
- API key validation
- Request logging and monitoring

**Do not use this in production without implementing proper security measures.**

## Overview

Iden-Hide is a comprehensive AI-powered anonymization engine that detects and blurs faces and license plates in images while preserving image context. The system is built with a modern microservices architecture supporting multiple processing modes.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Frontend<br/>React.js + Styled Components]
        MOBILE[Mobile App<br/>Future Support]
    end

    subgraph "API Gateway Layer"
        NGINX[Nginx<br/>Load Balancer & SSL]
        CORS[CORS Handler]
    end

    subgraph "Application Layer"
        API[FastAPI Server<br/>main.py]
        S3_PROC[S3 Processor<br/>s3_processor.py]
        FOLDER_PROC[Folder Processor<br/>Batch Processing]
    end

    subgraph "AI/ML Layer"
        FACE_DET[Face Detection<br/>YOLOv8 + InsightFace]
        LP_DET[License Plate Detection<br/>Custom YOLO Model]
        BLUR[Privacy Blur Engine<br/>Gaussian + Motion Blur]
    end

    subgraph "Storage Layer"
        S3[AWS S3<br/>Image Storage]
        LOCAL[Local Storage<br/>Temporary Files]
        CACHE[Redis Cache<br/>Future Implementation]
    end

    subgraph "External Services"
        AWS[AWS Services<br/>S3, IAM, STS]
        CDN[CloudFront CDN<br/>Future Implementation]
    end

    %% Client to API Gateway
    WEB --> NGINX
    MOBILE --> NGINX

    %% API Gateway to Application
    NGINX --> CORS
    CORS --> API

    %% Application Layer Connections
    API --> S3_PROC
    API --> FOLDER_PROC
    API --> FACE_DET
    API --> LP_DET
    API --> BLUR

    %% AI/ML Layer Connections
    FACE_DET --> BLUR
    LP_DET --> BLUR

    %% Storage Connections
    API --> LOCAL
    S3_PROC --> S3
    FOLDER_PROC --> LOCAL
    BLUR --> LOCAL
    BLUR --> S3

    %% External Service Connections
    S3_PROC --> AWS
    API --> AWS

    %% Future Connections
    LOCAL -.-> CACHE
    S3 -.-> CDN

    %% Styling
    classDef clientLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef aiLayer fill:#fff3e0
    classDef storageLayer fill:#e8f5e8
    classDef externalLayer fill:#fce4ec

    class WEB,MOBILE clientLayer
    class NGINX,CORS,API,S3_PROC,FOLDER_PROC apiLayer
    class FACE_DET,LP_DET,BLUR aiLayer
    class S3,LOCAL,CACHE storageLayer
    class AWS,CDN externalLayer
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        APP[App.js<br/>Main Container]
        NAV[Navbar<br/>Navigation]
        UPLOAD[FileUpload<br/>Drag & Drop]
        CONTROLS[DetectionControls<br/>Settings]
        GALLERY[ImageGallery<br/>Results Display]
        VIEWER[ImageViewer<br/>Image Display]
        FOLDER[FolderProcessor<br/>Batch Mode]
        S3[S3Processor<br/>Cloud Mode]
    end

    subgraph "Backend Services"
        MAIN[main.py<br/>FastAPI Server]
        DETECT_FACE[detect_face.py<br/>Face Detection]
        DETECT_LP[detect_lp.py<br/>License Plate Detection]
        S3_SVC[s3_service.py<br/>S3 Operations]
        UNIFIED[unified_detector.py<br/>Orchestration]
    end

    subgraph "Data Flow"
        REQ[HTTP Request]
        PROC[Image Processing]
        RES[Response]
    end

    %% Frontend Flow
    APP --> NAV
    APP --> UPLOAD
    APP --> CONTROLS
    APP --> GALLERY
    APP --> FOLDER
    APP --> S3

    %% Backend Flow
    REQ --> MAIN
    MAIN --> DETECT_FACE
    MAIN --> DETECT_LP
    MAIN --> S3_SVC
    MAIN --> UNIFIED

    %% Processing Flow
    DETECT_FACE --> PROC
    DETECT_LP --> PROC
    PROC --> RES

    %% Styling
    classDef frontend fill:#e3f2fd
    classDef backend fill:#f1f8e9
    classDef data fill:#fff8e1

    class APP,NAV,UPLOAD,CONTROLS,GALLERY,VIEWER,FOLDER,S3 frontend
    class MAIN,DETECT_FACE,DETECT_LP,S3_SVC,UNIFIED backend
    class REQ,PROC,RES data
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Server
    participant FD as Face Detector
    participant LD as License Plate Detector
    participant B as Blur Engine
    participant S as S3 Storage

    U->>F: Upload Image
    F->>A: POST /detect
    A->>FD: Detect Faces
    FD-->>A: Face Coordinates
    A->>LD: Detect License Plates
    LD-->>A: Plate Coordinates
    A->>B: Apply Privacy Blur
    B-->>A: Blurred Image
    A->>S: Store Results
    S-->>A: Storage URLs
    A-->>F: Detection Results
    F-->>U: Display Results

    Note over U,S: Single Image Processing Flow

    U->>F: Select Folder/S3
    F->>A: POST /process-folder
    A->>FD: Batch Face Detection
    A->>LD: Batch Plate Detection
    A->>B: Batch Blur Processing
    A->>S: Batch Storage
    A-->>F: Batch Results
    F-->>U: Display Gallery

    Note over U,S: Batch Processing Flow
```

## Technology Stack

### Frontend
- **Framework**: React.js 18.2.0
- **Styling**: Styled Components 6.1.0
- **File Handling**: React Dropzone 14.2.3
- **HTTP Client**: Axios 1.6.0
- **Notifications**: React Toastify 9.1.3
- **Build Tool**: Create React App

### Backend
- **Framework**: FastAPI (Python 3.13)
- **AI/ML**: 
  - YOLOv8 for object detection
  - InsightFace for face recognition
  - Custom license plate detection model
- **Image Processing**: OpenCV, PIL
- **Cloud Storage**: AWS S3 (boto3)
- **Async Processing**: asyncio, multiprocessing

### Infrastructure
- **Containerization**: Docker (planned)
- **Cloud Platform**: AWS
- **Storage**: AWS S3
- **CDN**: CloudFront (planned)
- **Monitoring**: CloudWatch (planned)

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        SSL[SSL/TLS Encryption]
        CORS[CORS Protection]
        AUTH[Authentication<br/>Future: JWT]
        RBAC[Role-Based Access<br/>Future Implementation]
    end

    subgraph "Data Protection"
        ENCRYPT[Data Encryption<br/>At Rest & In Transit]
        PRIVACY[Privacy Blur<br/>AI-Powered]
        AUDIT[Audit Logging<br/>Future Implementation]
    end

    subgraph "API Security"
        RATE[Rate Limiting<br/>Future Implementation]
        VALID[Input Validation]
        SANITIZE[Data Sanitization]
    end

    SSL --> CORS
    CORS --> AUTH
    AUTH --> RBAC

    ENCRYPT --> PRIVACY
    PRIVACY --> AUDIT

    RATE --> VALID
    VALID --> SANITIZE

    classDef security fill:#ffebee
    classDef data fill:#e8f5e8
    classDef api fill:#e3f2fd

    class SSL,CORS,AUTH,RBAC security
    class ENCRYPT,PRIVACY,AUDIT data
    class RATE,VALID,SANITIZE api
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer<br/>AWS ALB]
        EC2[EC2 Instances<br/>Auto Scaling Group]
        RDS[RDS Database<br/>Future Implementation]
        S3_BUCKET[S3 Bucket<br/>Image Storage]
    end

    subgraph "Development Environment"
        DEV_SERVER[Development Server<br/>Local/EC2]
        DEV_S3[Dev S3 Bucket]
    end

    subgraph "CI/CD Pipeline"
        GIT[Git Repository]
        BUILD[Build Process]
        TEST[Automated Testing]
        DEPLOY[Deployment]
    end

    LB --> EC2
    EC2 --> RDS
    EC2 --> S3_BUCKET

    GIT --> BUILD
    BUILD --> TEST
    TEST --> DEPLOY
    DEPLOY --> EC2

    classDef prod fill:#e8f5e8
    classDef dev fill:#fff3e0
    classDef cicd fill:#e3f2fd

    class LB,EC2,RDS,S3_BUCKET prod
    class DEV_SERVER,DEV_S3 dev
    class GIT,BUILD,TEST,DEPLOY cicd
```

## Performance Characteristics

### Scalability
- **Horizontal Scaling**: Auto-scaling EC2 instances
- **Async Processing**: Non-blocking I/O for file operations
- **Batch Processing**: Efficient multi-image processing
- **Caching**: Redis for frequently accessed data (planned)

### Performance Metrics
- **Image Processing**: ~2-5 seconds per image
- **Batch Processing**: Parallel processing with configurable workers
- **API Response Time**: <200ms for metadata, <5s for processing
- **Throughput**: 10-50 images/minute (depending on complexity)

### Resource Requirements
- **CPU**: 2-4 cores minimum for AI processing
- **RAM**: 8-16GB for model loading and processing
- **Storage**: 100GB+ for models and temporary files
- **GPU**: Optional, for faster AI processing

## Security Implementation Roadmap

### Phase 1: Critical Security (Next Priority)
- **Authentication**: JWT-based authentication system
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive request validation and sanitization
- **Rate Limiting**: API rate limiting and DDoS protection
- **HTTPS**: SSL/TLS encryption for all communications

### Phase 2: Data Security
- **Data Encryption**: Encrypt data at rest and in transit
- **Secure Storage**: Encrypted S3 buckets with proper IAM policies
- **Credential Management**: AWS Secrets Manager or HashiCorp Vault
- **API Keys**: Secure API key generation and validation
- **Audit Logging**: Comprehensive security event logging

### Phase 3: Advanced Security
- **Multi-factor Authentication**: 2FA/MFA support
- **Security Headers**: CORS, CSP, HSTS implementation
- **Vulnerability Scanning**: Regular security assessments
- **Penetration Testing**: Third-party security testing
- **Compliance**: SOC 2, ISO 27001 compliance features

## Future Enhancements

### Planned Features
- **Real-time Processing**: WebSocket support for live video
- **Advanced AI Models**: More sophisticated detection algorithms
- **Multi-tenant Support**: User authentication and data isolation
- **API Rate Limiting**: Protection against abuse
- **Monitoring Dashboard**: Real-time system metrics
- **Mobile App**: Native iOS/Android applications

### Technical Debt
- **Error Handling**: More comprehensive error management
- **Logging**: Structured logging with correlation IDs
- **Testing**: Increased test coverage (unit, integration, e2e)
- **Documentation**: API documentation with OpenAPI/Swagger
- **Security**: Enhanced authentication and authorization

---

*This architecture document is maintained alongside the codebase and reflects the current state of the Iden-Hide AI Anonymization Engine.*
