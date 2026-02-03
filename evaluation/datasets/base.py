"""Dataset adapter interface for offline benchmarking."""

from __future__ import annotations

from typing import Dict, List
import numpy as np


class DatasetAdapter:
    """Abstract dataset adapter.

    Implementations must return images as numpy arrays (BGR or RGB) and
    annotations as a list of dicts with keys: x1, y1, x2, y2, label.
    """

    def __len__(self) -> int:
        raise NotImplementedError

    def get_image(self, idx: int) -> np.ndarray:
        raise NotImplementedError

    def get_annotations(self, idx: int) -> List[Dict]:
        raise NotImplementedError

    def image_id(self, idx: int) -> str:
        raise NotImplementedError
