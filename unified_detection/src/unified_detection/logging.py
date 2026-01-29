"""Structured logging helpers."""

from __future__ import annotations

import logging
from typing import Optional


_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format=_DEFAULT_FORMAT)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
