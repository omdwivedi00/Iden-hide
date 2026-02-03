# evaluation/datasets/pp4av_coco.py

import json
from pathlib import Path
import cv2


class PP4AVCOCOAdapter:
    def __init__(self, coco_json: str, images_root: str, category: str):
        self.images_root = Path(images_root)
        self.category = category

        with open(coco_json, "r") as f:
            coco = json.load(f)

        # -------------------------
        # Category mapping
        # -------------------------
        self.cat_name_to_id = {
            c["name"]: c["id"] for c in coco["categories"]
        }

        assert category in self.cat_name_to_id, (
            f"Category '{category}' not found in COCO categories"
        )

        self.target_cat_id = self.cat_name_to_id[category]

        # -------------------------
        # Filter images (REMOVE fisheye)
        # -------------------------
        self.images = {}
        for img in coco["images"]:
            if self._is_fisheye(img["file_name"]):
                continue
            self.images[img["id"]] = img

        # -------------------------
        # Filter annotations
        # -------------------------
        self.ann_map = {}
        for ann in coco["annotations"]:
            if ann["category_id"] != self.target_cat_id:
                continue
            if ann["image_id"] not in self.images:
                continue
            self.ann_map.setdefault(ann["image_id"], []).append(ann)

        self.image_ids = list(self.images.keys())

        print(
            f"[PP4AV] Loaded {len(self.image_ids)} images "
            f"(fisheye excluded), category='{category}'"
        )

    # -------------------------
    # Helpers
    # -------------------------
    def _is_fisheye(self, file_name: str) -> bool:
        fname = file_name.lower()
        return (
            "fisheye" in fname
            or "front_fisheye" in fname
            or "rear_fisheye" in fname
        )

    # -------------------------
    # Dataset API
    # -------------------------
    def __len__(self):
        return len(self.image_ids)

    def image_id(self, idx):
        return self.image_ids[idx]

    def get_image(self, idx):
        img_info = self.images[self.image_ids[idx]]
        img_path = self.images_root / img_info["file_name"]
        img = cv2.imread(str(img_path))
        if img is None:
            raise RuntimeError(f"Failed to load image: {img_path}")
        return img

    def get_annotations(self, idx):
        anns = self.ann_map.get(self.image_ids[idx], [])
        gts = []
        for a in anns:
            x, y, w, h = a["bbox"]
            gts.append(
                {
                    "x1": x,
                    "y1": y,
                    "x2": x + w,
                    "y2": y + h,
                    "label": self.category,
                }
            )
        return gts