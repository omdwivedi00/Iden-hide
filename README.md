# Unified Detection

Production-ready refactor of the unified face + license plate detection system.

## Structure

```
unified_detection/
├── src/
│   └── unified_detection/
│       ├── config.py
│       ├── logging.py
│       ├── types.py
│       ├── core/
│       │   ├── detector.py
│       │   ├── face.py
│       │   ├── license_plate.py
│       │   └── blur.py
│       ├── api/
│       │   ├── app.py
│       │   └── routes.py
│       └── cli/
│           └── run_dataset.py
├── models/
├── tests/
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

## Run API

```
pip install -e .
uvicorn unified_detection.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Run Batch CLI

```
python -m unified_detection.cli.run_dataset --input_dir tests/data --out_dir artifacts/output_batch --batch 4
```

## Configuration

All config is centralized in `unified_detection/src/unified_detection/config.py` and controlled via env vars.

Common overrides:

- `DETECT_DEVICE` (cpu | cuda:0)
- `MODEL_DIR` (default: models)
- `OUTPUT_DIR` (default: output)
- `UPLOADS_DIR` (default: uploads)

## Frontend

The React frontend is in `detection-app/` and talks to the API at `http://localhost:8000` by default.
