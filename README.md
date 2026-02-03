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
│       │   ├── face_base.py
│       │   ├── face_cascade.py
│       │   ├── face_yolo.py
│       │   ├── face_scrfd.py
│       │   ├── license_plate.py
│       │   └── blur.py
│       ├── api/
│       │   ├── app.py
│       │   └── routes.py
│       └── cli/
│           └── run_dataset.py
evaluation/
├── datasets/
├── metrics.py
├── visualize.py
└── run_benchmark.py
detection-app/
models/
output/
uploads/
tests/
├── models/
├── tests/
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

## Environment Setup

Recommended (conda):
```
conda create -n unified-detection python=3.10 -y
conda activate unified-detection
```

Install dependencies:
```
pip install -e .
```

If you use the frontend:
```
cd detection-app
npm install
```

## Configuration (.env)

Runtime config is read from `.env` (repo root). Common overrides:

- `DETECT_DEVICE` (cpu | cuda)
- `FACE_MODE` (cascade | yolo_face | scrfd)
- `FACE_YOLO_MODEL` (required for yolo_face)
- `LP_PLATE_MODEL` / `LP_VEHICLE_MODEL`

You can also override any value inline per command.

## Run API

```
uvicorn unified_detection.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Run Frontend

```
cd detection-app
npm start
```

## Run Batch CLI

```
python -m unified_detection.cli.run_dataset \
  --input_dir tests/data \
  --out_dir artifacts/output_batch \
  --batch 4
```

## Run Benchmarks

Face (PP4AV):
```
python -m evaluation.run_benchmark \
  --dataset pp4av \
  --dataset_root evaluation/datasets \
  --task face \
  --iou 0.3 \
  --device cpu \
  --save_visuals true \
  --max_images 500
```

License plate (PP4AV):
```
python -m evaluation.run_benchmark \
  --dataset pp4av \
  --dataset_root evaluation/datasets \
  --task plate \
  --iou 0.5 \
  --device cpu \
  --save_visuals true \
  --max_images 500
```

## Frontend

The React frontend is in `detection-app/` and talks to the API at `http://localhost:8000` by default.
