"""Centralized configuration for unified detection."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Literal

from pydantic import (
    AliasChoices,
    Field,
    validator,
    computed_field,
)
from pydantic_settings import BaseSettings


def _env_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    # =========================
    # Runtime
    # =========================
    device: str = Field(
        "cpu",
        validation_alias=AliasChoices("DETECT_DEVICE", "FACE_DEVICE"),
    )
    batch_size: int = Field(8, env="DETECT_BATCH_SIZE")
    max_workers: int = Field(4, env="DETECT_MAX_WORKERS")

    # =========================
    # Paths
    # =========================
    model_dir: str = Field("models", env="MODEL_DIR")
    uploads_dir: str = Field("uploads", env="UPLOADS_DIR")
    output_dir: str = Field("output", env="OUTPUT_DIR")

    # =========================
    # Face Detection – MODE
    # =========================
    # cascade | yolo_face | scrfd
    face_mode: Literal["cascade", "yolo_face", "scrfd"] = Field(
        "cascade", env="FACE_MODE"
    )

    # =========================
    # Face Detection – YOLO (PERSON)
    # Used ONLY in cascade
    # =========================
    face_person_model: Optional[str] = Field(
        default=None, env="FACE_PERSON_MODEL"
    )
    face_person_conf: float = Field(0.25, env="FACE_PERSON_CONF")
    face_img_size: int = Field(832, env="FACE_IMG_SIZE")
    face_max_persons: int = Field(25, env="FACE_MAX_PERSONS")

    # =========================
    # Face Detection – YOLO (FACE)
    # Used ONLY in yolo_face
    # =========================
    face_yolo_model: Optional[str] = Field(
        default=None, env="FACE_YOLO_MODEL"
    )

    # =========================
    # Face Detection – SCRFD
    # Used in cascade + scrfd
    # =========================
    face_scrfd_model: str = Field(
        "buffalo_l", env="FACE_SCRFD_MODEL"
    )  # buffalo_l | scrfd_10g | scrfd_2.5g
    face_det_size: int = Field(640, env="FACE_DET_SIZE")
    face_det_thr: float = Field(0.5, env="FACE_DET_THR")
    face_flip_tta: bool = Field(False, env="FACE_FLIP_TTA")

    # =========================
    # Post-processing
    # =========================
    face_nms_iou: float = Field(0.55, env="FACE_NMS_IOU")

    # =========================
    # License Plate Detection
    # =========================
    lp_vehicle_model: Optional[str] = Field(None, env="LP_VEHICLE_MODEL")
    lp_plate_model: Optional[str] = Field(None, env="LP_PLATE_MODEL")
    lp_vehicle_conf: float = Field(0.30, env="LP_VEHICLE_CONF")
    lp_plate_conf: float = Field(0.20, env="LP_PLATE_CONF")
    lp_vehicle_classes: List[int] = Field(default_factory=lambda: [2, 3, 5, 7])

    # =========================
    # Blur Defaults
    # =========================
    face_blur_strength: int = Field(15, env="FACE_BLUR_STRENGTH")
    plate_blur_strength: int = Field(15, env="PLATE_BLUR_STRENGTH")

    # =========================
    # API
    # =========================
    api_title: str = Field("Unified Detection API", env="API_TITLE")
    api_version: str = Field("1.0.0", env="API_VERSION")
    cors_origins: List[str] = Field(default_factory=list, env="CORS_ORIGINS")

    # =========================
    # Logging
    # =========================
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "forbid"

    # =========================
    # Validators
    # =========================
    @validator("cors_origins", pre=True)
    def _parse_cors_origins(cls, v):
        if isinstance(v, str):
            return _env_list(v)
        return v

    # =========================
    # Model Resolvers
    # =========================
    @computed_field
    @property
    def resolved_face_person_model(self) -> str:
        """
        YOLO person model (cascade only)
        """
        if self.face_person_model:
            return self.face_person_model
        p = Path(self.model_dir) / "yolov8n.pt"
        return str(p) if p.exists() else "yolov8n.pt"

    @computed_field
    @property
    def resolved_face_yolo_model(self) -> str:
        """
        YOLO face model (yolo_face only)
        """
        if self.face_mode == "yolo_face" and not self.face_yolo_model:
            raise ValueError(
                "FACE_YOLO_MODEL must be set when FACE_MODE=yolo_face"
            )
        return self.face_yolo_model or ""

    @computed_field
    @property
    def resolved_face_scrfd_model(self) -> str:
        """
        SCRFD / InsightFace detector name
        """
        return self.face_scrfd_model

    @computed_field
    @property
    def resolved_lp_vehicle_model(self) -> str:
        """
        YOLO vehicle model (license plate pipeline)
        """
        if self.lp_vehicle_model:
            return self.lp_vehicle_model
        p = Path(self.model_dir) / "yolo11n.pt"
        return str(p) if p.exists() else "yolo11n.pt"

    @computed_field
    @property
    def resolved_lp_plate_model(self) -> str:
        """
        License plate detector model
        """
        if self.lp_plate_model:
            return self.lp_plate_model
        p = Path(self.model_dir) / "license_plate_detector.pt"
        return str(p) if p.exists() else "license_plate_detector.pt"
