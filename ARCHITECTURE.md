# Unified Detection - Architecture

## Security Notice
This system ships without authentication/authorization enabled. Add security controls (authn/z, input validation, rate limiting, secrets management, logging/monitoring) before production use.

## Overview
Unified Detection is a CPU‑first (GPU‑switchable) AI service for face and license plate detection, optional blur/anonymization, and batch workflows (local + S3). The UI is a React 18 app that calls a FastAPI backend.

## Current Architecture (refactored)

```
├── detection-app/                  # React 18 frontend
├── unified_detection/              # Backend package
│   └── src/unified_detection/
│       ├── config.py               # Central config (env + defaults)
│       ├── logging.py              # Structured logging
│       ├── core/                   # Pure CV logic
│       │   ├── detector.py
│       │   ├── face_base.py
│       │   ├── face_cascade.py
│       │   ├── face_yolo.py
│       │   ├── face_scrfd.py
│       │   ├── license_plate.py
│       │   └── blur.py
│       ├── api/                    # FastAPI app + routes
│       │   ├── app.py
│       │   └── routes.py
│       ├── services/               # S3 integration
│       │   ├── s3_processor.py
│       │   └── s3_service.py
│       └── cli/                    # Batch CLI
│           └── run_dataset.py
├── evaluation/                     # Offline benchmarking
│   ├── datasets/
│   ├── metrics.py
│   ├── visualize.py
│   └── run_benchmark.py
├── models/                          # Model weights (ignored by git)
├── output/                          # Local outputs (ignored by git)
├── uploads/                         # Temp uploads (ignored by git)
└── tests/                           # Sample data + tests
```

## Runtime Flow

### Single Image (local)
1. Frontend uploads image to `/detect` or `/blur` (multipart/form-data).
2. API validates input, writes temp upload, runs `UnifiedDetector`.
3. Blur uses `DetectionVisualizer` to write output.
4. Results are returned (detections + output path).

### Batch (local files)
1. Frontend posts multiple files to `/process-parallel`.
2. Backend processes with shared detector/visualizer instances.
3. Results streamed back as a single payload.

### Batch (S3)
1. Frontend provides S3 credentials and paths.
2. `S3ProcessingService` uses `S3ImageProcessor` to download, run detection/blur, upload results.

## Key Design Decisions
- **Single source of truth**: all detection logic lives in `core/`.
- **No API logic in core**: API and CLI call the same `UnifiedDetector` instance.
- **Config centralization**: env overrides in `config.py` only.
- **CPU‑first**: switch device with `DETECT_DEVICE` env var.
- **Pluggable face detectors**: `FACE_MODE` switches between cascade, YOLO face, and SCRFD.

## Config (high‑impact)
- `DETECT_DEVICE` (cpu | cuda:0)
- `MODEL_DIR` (default: models)
- `OUTPUT_DIR` (default: output)
- `UPLOADS_DIR` (default: uploads)
- `FACE_MODE` (cascade | yolo_face | scrfd)
- `FACE_YOLO_MODEL` (required when FACE_MODE=yolo_face)
- `FACE_PERSON_CONF` (YOLO confidence threshold)

## Environment Configuration
All runtime settings are loaded from `.env` (repo root) via `Settings`, with `.env.example` as a template. Per‑run overrides are supported via standard environment variables.

## Observability
- Structured logging via `unified_detection/logging.py`.

## Frontend UX Model
- **Sidebar**: workflow selection only
- **Main canvas**: visualization/results
- **Inspector panel**: detection + blur configuration
- **Toolbar**: view‑only toggles

## Deployment Notes
- Run API via:
  ```bash
  pip install -e .
  uvicorn unified_detection.api.app:create_app --factory --host 0.0.0.0 --port 8000
  ```
- Frontend uses `REACT_APP_API_URL` or `package.json` proxy.
