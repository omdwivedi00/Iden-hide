"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import Settings
from ..logging import configure_logging, get_logger
from ..core.detector import UnifiedDetector
from ..core.blur import DetectionVisualizer
from ..services.s3_service import S3ProcessingService
from .routes import router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    configure_logging(settings.log_level)

    detector = UnifiedDetector(settings=settings)
    visualizer = DetectionVisualizer()
    s3_service = S3ProcessingService(detector=detector, visualizer=visualizer, settings=settings)

    app.state.detector = detector
    app.state.visualizer = visualizer
    app.state.s3_service = s3_service

    logger.info("Unified detection API initialized")
    yield
    logger.info("Unified detection API shutdown")


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title=settings.api_title,
        description="API for face and license plate detection with blur functionality",
        version=settings.api_version,
        lifespan=lifespan,
    )
    app.state.settings = settings

    allow_origins = settings.cors_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app
