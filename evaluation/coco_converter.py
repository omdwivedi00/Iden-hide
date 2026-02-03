import json
from pathlib import Path
import cv2
from tqdm import tqdm   # 👈 added

# ----------------------------
# COCO category definitions
# ----------------------------
CATEGORIES = [
    {"id": 1, "name": "face"},
    {"id": 2, "name": "license_plate"},
]

# YOLO class → COCO category
CLASS_MAP = {
    0: 1,  # face
    1: 2,  # license_plate
}


def convert_pp4av_to_coco(images_dir, annotations_dir, output_json):
    images = []
    annotations = []

    img_id = 1
    ann_id = 1

    images_dir = Path(images_dir)
    annotations_dir = Path(annotations_dir)

    # collect image paths once (important for tqdm)
    image_paths = [
        p for p in images_dir.rglob("*")
        if p.suffix.lower() in {".jpg", ".png", ".jpeg"}
    ]

    for img_path in tqdm(image_paths, desc="Converting PP4AV → COCO"):
        label_path = annotations_dir / img_path.relative_to(images_dir)
        label_path = label_path.with_suffix(".txt")

        if not label_path.exists():
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        h, w = img.shape[:2]

        images.append({
            "id": img_id,
            "file_name": str(img_path.relative_to(images_dir)),
            "width": w,
            "height": h
        })

        with open(label_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue

                cls_id = int(parts[0])
                if cls_id not in CLASS_MAP:
                    continue

                cx, cy, bw, bh = map(float, parts[1:])

                # YOLO → COCO bbox
                x = (cx - bw / 2) * w
                y = (cy - bh / 2) * h
                box_w = bw * w
                box_h = bh * h

                annotations.append({
                    "id": ann_id,
                    "image_id": img_id,
                    "category_id": CLASS_MAP[cls_id],
                    "bbox": [x, y, box_w, box_h],
                    "area": box_w * box_h,
                    "iscrowd": 0
                })
                ann_id += 1

        img_id += 1

    coco = {
        "images": images,
        "annotations": annotations,
        "categories": CATEGORIES
    }

    with open(output_json, "w") as f:
        json.dump(coco, f, indent=2)

    print("✅ COCO conversion complete")
    print(f"Images: {len(images)}")
    print(f"Annotations: {len(annotations)}")
    print(f"Saved to: {output_json}")


if __name__ == "__main__":
    convert_pp4av_to_coco(
        images_dir="evaluation/datasets/PP4AV/images",
        annotations_dir="evaluation/datasets/PP4AV/annotations",
        output_json="evaluation/datasets/pp4av_coco.json"
    )