"""Metric computation for Unified Detection benchmarking."""

from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np


def iou_xyxy(a: List[float], b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    if denom <= 0:
        return 0.0
    return inter / denom


def match_detections(
    preds: List[Dict],
    gts: List[Dict],
    iou_thresh: float,
) -> Tuple[List[Tuple[int, int, float]], List[int], List[int]]:
    """Greedy one-to-one matching by IoU.

    Returns: matches, unmatched_pred_indices, unmatched_gt_indices
    """
    if not preds or not gts:
        return [], list(range(len(preds))), list(range(len(gts)))

    iou_matrix = np.zeros((len(preds), len(gts)), dtype=np.float32)
    for i, p in enumerate(preds):
        for j, g in enumerate(gts):
            iou_matrix[i, j] = iou_xyxy([p["x1"], p["y1"], p["x2"], p["y2"]], [g["x1"], g["y1"], g["x2"], g["y2"]])

    matches = []
    used_preds = set()
    used_gts = set()

    while True:
        max_iou = iou_thresh
        max_i, max_j = -1, -1
        for i in range(len(preds)):
            if i in used_preds:
                continue
            for j in range(len(gts)):
                if j in used_gts:
                    continue
                iou = iou_matrix[i, j]
                if iou >= max_iou:
                    max_iou = iou
                    max_i, max_j = i, j
        if max_i == -1:
            break
        used_preds.add(max_i)
        used_gts.add(max_j)
        matches.append((max_i, max_j, float(max_iou)))

    unmatched_preds = [i for i in range(len(preds)) if i not in used_preds]
    unmatched_gts = [j for j in range(len(gts)) if j not in used_gts]
    return matches, unmatched_preds, unmatched_gts


def precision_recall(matches: List[Tuple[int, int, float]], total_preds: int, total_gts: int) -> Tuple[float, float]:
    tp = len(matches)
    precision = tp / total_preds if total_preds > 0 else 0.0
    recall = tp / total_gts if total_gts > 0 else 0.0
    return precision, recall


def compute_metrics(
    preds: List[Dict],
    gts: List[Dict],
    iou_thresh: float,
) -> Dict:
    matches, unmatched_preds, unmatched_gts = match_detections(preds, gts, iou_thresh)
    precision, recall = precision_recall(matches, len(preds), len(gts))
    fn_rate = len(unmatched_gts) / len(gts) if gts else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "fn_rate": fn_rate,
        "matches": matches,
        "unmatched_preds": unmatched_preds,
        "unmatched_gts": unmatched_gts,
    }


def small_face_recall(preds: List[Dict], gts: List[Dict], iou_thresh: float, area_thresh: float = 32 * 32) -> float:
    small_gts = []
    for g in gts:
        area = max(0.0, (g["x2"] - g["x1"])) * max(0.0, (g["y2"] - g["y1"]))
        if area <= area_thresh:
            small_gts.append(g)
    if not small_gts:
        return 0.0
    matches, _, unmatched_gts = match_detections(preds, small_gts, iou_thresh)
    recall = len(matches) / len(small_gts)
    return recall
