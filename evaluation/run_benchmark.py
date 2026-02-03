"""CLI for offline benchmarking of UnifiedDetector."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
from tqdm import tqdm

from unified_detection.core.detector import UnifiedDetector

from evaluation.datasets.widerface import WiderFaceAdapter
from evaluation.datasets.ufpr_alpr import UFPRALPRAdapter
from evaluation.datasets.pp4av_coco import PP4AVCOCOAdapter
from evaluation.metrics import compute_metrics, small_face_recall
from evaluation.visualize import save_error_visual


def parse_args():
    parser = argparse.ArgumentParser("Unified Detection Benchmark")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["widerface", "ufpr_alpr", "pp4av"],
    )
    parser.add_argument("--dataset_root", required=True)
    parser.add_argument("--task", required=True, choices=["face", "plate"])
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--save_visuals", type=str, default="false")
    parser.add_argument("--max_images", type=int, default=0)
    return parser.parse_args()


def normalize_preds(preds: List[Dict], label: str) -> List[Dict]:
    """Normalize detector outputs to x1,y1,x2,y2 format."""
    out = []
    for p in preds:
        if "bbox" in p:
            x1, y1, x2, y2 = p["bbox"]
        elif all(k in p for k in ("x1", "y1", "x2", "y2")):
            x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
        else:
            continue

        out.append({
            "x1": float(x1),
            "y1": float(y1),
            "x2": float(x2),
            "y2": float(y2),
            "label": label,
        })
    return out


def main():
    args = parse_args()
    save_visuals = args.save_visuals.lower() in ("1", "true", "yes")

    # -------------------------
    # Dataset selection
    # -------------------------
    if args.dataset == "widerface":
        dataset = WiderFaceAdapter(args.dataset_root)
    elif args.dataset == "ufpr_alpr":
        dataset = UFPRALPRAdapter(args.dataset_root)
    elif args.dataset == "pp4av":
        dataset = PP4AVCOCOAdapter(
            coco_json=f"{args.dataset_root}/pp4av_coco.json",
            images_root=f"{args.dataset_root}/PP4AV/images",
            category="face" if args.task == "face" else "license_plate",
        )

    detector = UnifiedDetector(device=args.device)

    total_images = len(dataset)
    if args.max_images > 0:
        total_images = min(total_images, args.max_images)

    aggregated = {
        "precision": [],
        "recall": [],
        "fn_rate": [],
        "small_face_recall": [],
        "total_images": total_images,
    }

    total_time = 0.0

    # -------------------------
    # Benchmark loop (with progress bar)
    # -------------------------
    pbar = tqdm(
        range(total_images),
        desc=f"Benchmarking {args.dataset} ({args.task})",
        unit="img",
    )

    for idx in pbar:
        image = dataset.get_image(idx)
        gts = dataset.get_annotations(idx)
        image_id = dataset.image_id(idx)

        t0 = time.time()
        results = detector.detect_objects(
            image,
            detect_face=args.task == "face",
            detect_lp=args.task == "plate",
        )
        t1 = time.time()
        total_time += (t1 - t0)

        if args.task == "face":
            preds = normalize_preds(results.get("faces", []), "face")
        else:
            preds = normalize_preds(results.get("license_plates", []), "license_plate")

        metrics = compute_metrics(preds, gts, args.iou)
        aggregated["precision"].append(metrics["precision"])
        aggregated["recall"].append(metrics["recall"])
        aggregated["fn_rate"].append(metrics["fn_rate"])

        if args.task == "face":
            aggregated["small_face_recall"].append(
                small_face_recall(preds, gts, args.iou)
            )

        if save_visuals and (metrics["unmatched_preds"] or metrics["unmatched_gts"]):
            fps = [preds[i] for i in metrics["unmatched_preds"]]
            fns = [gts[i] for i in metrics["unmatched_gts"]]
            out_path = Path("evaluation/results/error_gallery") / f"{image_id}.jpg"
            save_error_visual(image, gts, fps, fns, out_path)

        avg_latency_ms = (total_time / (idx + 1)) * 1000
        pbar.set_postfix(avg_latency_ms=f"{avg_latency_ms:.1f}")

    # -------------------------
    # Final summary
    # -------------------------
    summary = {
        "task": args.task,
        "dataset": args.dataset,
        "iou": args.iou,
        "precision": float(np.mean(aggregated["precision"])) if aggregated["precision"] else 0.0,
        "recall": float(np.mean(aggregated["recall"])) if aggregated["recall"] else 0.0,
        "fn_rate": float(np.mean(aggregated["fn_rate"])) if aggregated["fn_rate"] else 0.0,
        "small_face_recall": (
            float(np.mean(aggregated["small_face_recall"]))
            if args.task == "face" and aggregated["small_face_recall"]
            else None
        ),
        "avg_latency_ms": (total_time / total_images) * 1000 if total_images > 0 else 0.0,
        "total_images": total_images,
    }

    Path("evaluation/results").mkdir(parents=True, exist_ok=True)
    with open("evaluation/results/metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Benchmark Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()