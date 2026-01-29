"""Centralized configuration for unified detection."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


def _env_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    # Runtime
    device: str = Field(default_factory=lambda: os.getenv("DETECT_DEVICE") or os.getenv("FACE_DEVICE") or "cpu")
    batch_size: int = Field(8, env="DETECT_BATCH_SIZE")
    max_workers: int = Field(4, env="DETECT_MAX_WORKERS")

    # Paths
    model_dir: str = Field("models", env="MODEL_DIR")
    uploads_dir: str = Field("uploads", env="UPLOADS_DIR")
    output_dir: str = Field("output", env="OUTPUT_DIR")

    # Face detection
    face_yolo_model: Optional[str] = Field(default=None, env="FACE_YOLO_MODEL")
    face_person_conf: float = Field(0.25, env="FACE_PERSON_CONF")
    face_img_size: int = Field(832, env="FACE_IMG_SIZE")
    face_det_size: int = Field(640, env="FACE_DET_SIZE")
    face_det_thr: float = Field(0.20, env="FACE_DET_THR")
    face_flip_tta: bool = Field(False, env="FACE_FLIP_TTA")
    face_max_persons: int = Field(25, env="FACE_MAX_PERSONS")

    # License plate detection
    lp_vehicle_model: Optional[str] = Field(default=None, env="LP_VEHICLE_MODEL")
    lp_plate_model: Optional[str] = Field(default=None, env="LP_PLATE_MODEL")
    lp_vehicle_conf: float = Field(0.30, env="LP_VEHICLE_CONF")
    lp_plate_conf: float = Field(0.20, env="LP_PLATE_CONF")
    lp_vehicle_classes: List[int] = Field(default_factory=lambda: [2, 3, 5, 7])

    # Blur defaults
    face_blur_strength: int = Field(15, env="FACE_BLUR_STRENGTH")
    plate_blur_strength: int = Field(15, env="PLATE_BLUR_STRENGTH")

    # API
    api_title: str = Field("Unified Detection API", env="API_TITLE")
    api_version: str = Field("1.0.0", env="API_VERSION")
    cors_origins: List[str] = Field(default_factory=list, env="CORS_ORIGINS")

    # S3
    s3_region: str = Field("ap-south-1", env="S3_REGION")
    s3_presign_expiration: int = Field(300, env="S3_PRESIGN_EXPIRATION")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def _parse_cors_origins(cls, v):
        if isinstance(v, str):
            return _env_list(v)
        return v

    @property
    def resolved_face_yolo_model(self) -> str:
        if self.face_yolo_model:
            return self.face_yolo_model
        candidate = Path(self.model_dir) / "yolov8n.pt"
        if candidate.exists():
            return str(candidate)
        return "yolov8n.pt"

    @property
    def resolved_lp_vehicle_model(self) -> str:
        if self.lp_vehicle_model:
            return self.lp_vehicle_model
        candidate = Path(self.model_dir) / "yolo11n.pt"
        return str(candidate) if candidate.exists() else "yolo11n.pt"

    @property
    def resolved_lp_plate_model(self) -> str:
        if self.lp_plate_model:
            return self.lp_plate_model
        candidate = Path(self.model_dir) / "license_plate_detector.pt"
        return str(candidate) if candidate.exists() else "license_plate_detector.pt"

