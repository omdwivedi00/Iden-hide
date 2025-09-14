#!/usr/bin/env python3
# ADAS face detection (faces-only output):
# YOLO(person) -> expand ROI -> 2x2 letterboxed tiles -> SCRFD
# - head-band gating + relative size sanity + person de-dup
# - outputs ONLY faces [x1,y1,x2,y2,score]
# - writes <out>.json with faces and copies input image to --out (no drawings)

import os, json, cv2, argparse, numpy as np
from ultralytics import YOLO
from insightface.app import FaceAnalysis

# ---------------- utils ----------------
def ensure_dir_for(path: str):
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)

def expand_xyxy(box, scale, W, H, square=True):
    x1, y1, x2, y2 = map(float, box)
    cx, cy = (x1 + x2) * 0.5, (y1 + y2) * 0.5
    w, h = (x2 - x1), (y2 - y1)
    if square:
        s = scale * max(w, h); w = h = s
    else:
        w, h = scale * w, scale * h
    nx1, ny1 = max(0.0, cx - w * 0.5), max(0.0, cy - h * 0.5)
    nx2, ny2 = min(W - 1.0, cx + w * 0.5), min(H - 1.0, cy + h * 0.5)
    return [nx1, ny1, nx2, ny2]

def head_band_from_person(pb, frac=0.45):
    x1,y1,x2,y2 = map(float, pb)
    h = max(1.0, y2 - y1)
    return [x1, y1, x2, y1 + h * frac]

def center_in_band(face_xyxy, band_xyxy, margin=0.0):
    fx1, fy1, fx2, fy2 = map(float, face_xyxy)
    bx1, by1, bx2, by2 = map(float, band_xyxy)
    cx = 0.5 * (fx1 + fx2); cy = 0.5 * (fy1 + fy2)
    return (bx1 - margin) <= cx <= (bx2 + margin) and (by1 - margin) <= cy <= (by2 + margin)

def face_size_ok(face_xyxy, person_xyxy, min_rel=0.10, max_rel=0.55):
    x1,y1,x2,y2 = map(float, face_xyxy)
    px1,py1,px2,py2 = map(float, person_xyxy)
    fh = max(1.0, y2 - y1); ph = max(1.0, py2 - py1)
    r = fh / ph
    return (min_rel <= r <= max_rel)

def nms_xyxy(boxes, scores, iou_thr=0.5):
    if not boxes: return []
    B = np.asarray(boxes, np.float32); S = np.asarray(scores, np.float32)
    order = S.argsort()[::-1]; keep = []
    while order.size > 0:
        i = order[0]; keep.append(i)
        rest = order[1:]
        if rest.size == 0: break
        xx1 = np.maximum(B[i,0], B[rest,0]); yy1 = np.maximum(B[i,1], B[rest,1])
        xx2 = np.minimum(B[i,2], B[rest,2]); yy2 = np.minimum(B[i,3], B[rest,3])
        w = np.maximum(0, xx2 - xx1); h = np.maximum(0, yy2 - yy1)
        inter = w * h
        area_i = (B[i,2]-B[i,0])*(B[i,3]-B[i,1])
        area_r = (B[rest,2]-B[rest,0])*(B[rest,3]-B[rest,1])
        iou = inter / (area_i + area_r - inter + 1e-6)
        order = rest[iou <= iou_thr]
    return keep

def letterbox(img, new_size, color=(114,114,114)):
    h, w = img.shape[:2]
    r = min(new_size / w, new_size / h)
    nw, nh = int(round(w*r)), int(round(h*r))
    imr = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_CUBIC)
    dw, dh = (new_size - nw) * 0.5, (new_size - nh) * 0.5
    top, bottom = int(dh), new_size - nh - int(dh)
    left, right = int(dw), new_size - nw - int(dw)
    out = cv2.copyMakeBorder(imr, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return out, r, (left, top), (nw, nh)

def tiles_inside_roi(roi, W, H, grid=(2,2), overlap=0.25):
    rx1, ry1, rx2, ry2 = map(int, roi)
    rx1 = max(0, rx1); ry1 = max(0, ry1); rx2 = min(W, rx2); ry2 = min(H, ry2)
    if rx2 <= rx1 or ry2 <= ry1: return []
    gw, gh = grid
    rw, rh = (rx2 - rx1), (ry2 - ry1)
    stepx, stepy = max(1, rw // gw), max(1, rh // gh)
    ox, oy = int(overlap * stepx), int(overlap * stepy)
    out = []
    for gy in range(gh):
        for gx in range(gw):
            tx1 = max(0, rx1 + gx*stepx - ox)
            ty1 = max(0, ry1 + gy*stepy - oy)
            tx2 = min(W, rx1 + (gx+1)*stepx + ox)
            ty2 = min(H, ry1 + (gy+1)*stepy + oy)
            if tx2 > tx1 and ty2 > ty1:
                out.append([tx1, ty1, tx2, ty2])
    return out

def detect_faces_in_tile(face_app, img, xyxy, face_size, thr, flip_tta=False):
    x1,y1,x2,y2 = map(int, xyxy)
    tile = img[y1:y2, x1:x2]
    if tile.size == 0: return []
    rs, r, (dx,dy), (nw,nh) = letterbox(tile, face_size)
    faces = face_app.get(rs)
    if flip_tta:
        rsf = cv2.flip(rs, 1)
        ff = face_app.get(rsf)
        for f in ff:
            b = f.bbox.astype(float); b[[0,2]] = face_size - b[[2,0]]
            faces.append(type('obj',(object,),{'bbox':b,'det_score':getattr(f,'det_score',1.0)}))
    outs=[]
    for f in faces:
        bx1,by1,bx2,by2 = f.bbox.astype(float)
        sc = float(getattr(f, "det_score", 1.0))
        if sc < thr: continue
        tx1 = (bx1 - dx) / r; ty1 = (by1 - dy) / r
        tx2 = (bx2 - dx) / r; ty2 = (by2 - dy) / r
        tx1 = np.clip(tx1, 0, nw-1); tx2 = np.clip(tx2, 0, nw-1)
        ty1 = np.clip(ty1, 0, nh-1); ty2 = np.clip(ty2, 0, nh-1)
        outs.append([x1 + tx1, y1 + ty1, x1 + tx2, y1 + ty2, sc])
    return outs

# ---------------- main ----------------
def run(
    source, out_path,
    # YOLO (person)
    yolo_w='yolov8x.pt', pconf=0.25, imgsz=832, person_nms_iou=0.60,
    # SCRFD
    face_size=640, fthr=0.20, flip_tta=True,
    # person ROI + fixed tiling
    roi_scale=1.10, roi_square=False, grid="2x2", overlap=0.30,
    # gating
    head_frac=0.45, size_min_rel=0.10, size_max_rel=0.55
):
    img = cv2.imread(source); assert img is not None, f"bad path: {source}"
    H, W = img.shape[:2]

    # YOLO person (with extra de-dup NMS)
    yolo = YOLO(yolo_w)
    pred = yolo.predict(img, conf=pconf, classes=[0], imgsz=imgsz, verbose=False)[0]
    p_boxes = [b.xyxy[0].tolist() for b in pred.boxes]
    p_scores = [float(b.conf[0]) if hasattr(b, "conf") and b.conf is not None else 0.0 for b in pred.boxes]
    keep_p = nms_xyxy(p_boxes, p_scores, iou_thr=person_nms_iou)
    persons = [p_boxes[i] for i in keep_p]
    # print(f"[YOLO] persons_raw={len(p_boxes)} persons_kept={len(persons)}")

    # SCRFD
    app = FaceAnalysis(name="buffalo_l",
                       providers=["CPUExecutionProvider"],
                       allowed_modules=['detection'])
    app.prepare(ctx_id=0, det_size=(face_size, face_size))
    det = app.models.get('detection', None)
    if det:
        det.det_thresh = fthr
        det.nms_thresh = 0.45

    faces_all, scores_all = [], []

    # per-person: expand ROI -> tiles -> SCRFD -> gating -> pick BEST ONLY
    for pb in persons:
        roi  = expand_xyxy(pb, roi_scale, W, H, square=roi_square)
        band = head_band_from_person(pb, frac=head_frac)

        cand_boxes, cand_scores = [], []
        tiles = tiles_inside_roi(roi, W, H, grid=tuple(int(x) for x in grid.lower().split("x")), overlap=overlap)
        for t in tiles:
            outs = detect_faces_in_tile(app, img, t, face_size, fthr, flip_tta=flip_tta)
            for x1,y1,x2,y2,sc in outs:
                if center_in_band([x1,y1,x2,y2], band) and face_size_ok([x1,y1,x2,y2], pb, size_min_rel, size_max_rel):
                    cand_boxes.append([x1,y1,x2,y2]); cand_scores.append(sc)

        # keep best candidate per person
        if cand_boxes:
            j = int(np.argmax(cand_scores))
            faces_all.append(cand_boxes[j]); scores_all.append(cand_scores[j])

    # cross-person NMS (in case ROIs overlap)
    keep_f = nms_xyxy(faces_all, scores_all, iou_thr=0.55)
    faces_final = [[float(f"{v:.2f}") for v in faces_all[i]] + [float(f"{scores_all[i]:.4f}")] for i in keep_f]

    # --- outputs ---
    # 1) save sidecar JSON <out>.json
    json_path = os.path.splitext(out_path)[0] + ".json"
    ensure_dir_for(json_path)
    payload = {
        "image": os.path.basename(source),
        "size": {"H": H, "W": W},
        "faces": [{"bbox":[b[0],b[1],b[2],b[3]], "score": b[4]} for b in faces_final],
        "counts": {"faces": len(faces_final), "persons": len(persons)}
    }
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)

    # 2) copy input image to --out (no drawings), to preserve your I/O
    ensure_dir_for(out_path)
    cv2.imwrite(out_path, img)

    # 3) print faces to stdout
    print(json.dumps({"faces": faces_final}, indent=2))
    # Example element: [x1, y1, x2, y2, score]

# ---------------- cli ----------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="YOLO(person) -> tiled SCRFD (faces-only output)")
    ap.add_argument("--source", required=True, help="input image")
    ap.add_argument("--out", default="out.png", help="output path (image copy)")
    # YOLO
    ap.add_argument("--yolo", default="yolov8x.pt")
    ap.add_argument("--pconf", type=float, default=0.25)
    ap.add_argument("--imgsz", type=int, default=832, help="YOLO inference size")
    ap.add_argument("--person_nms_iou", type=float, default=0.60, help="extra NMS to dedupe YOLO persons")
    # SCRFD
    ap.add_argument("--fsize", type=int, default=1280, help="SCRFD canvas (square)")
    ap.add_argument("--fthr",  type=float, default=0.20, help="SCRFD detection threshold")
    ap.add_argument("--flip_tta", action="store_true", help="flip-TTA inside tiles")
    # ROI + tiling
    ap.add_argument("--scale", type=float, default=1.10, help="expand factor for person ROI")
    ap.add_argument("--square", action="store_true", help="use square expanded ROI")
    ap.set_defaults(square=False)
    ap.add_argument("--grid", default="2x2", help="tile grid (fixed)")
    ap.add_argument("--overlap", type=float, default=0.30, help="tile overlap (0..0.5)")
    # gating
    ap.add_argument("--head_frac", type=float, default=0.45, help="fraction of person height as head band")
    ap.add_argument("--size_min_rel", type=float, default=0.10, help="min face height / person height")
    ap.add_argument("--size_max_rel", type=float, default=0.55, help="max face height / person height")

    a = ap.parse_args()
    run(
        source=a.source, out_path=a.out,
        yolo_w=a.yolo, pconf=a.pconf, imgsz=a.imgsz, person_nms_iou=a.person_nms_iou,
        face_size=a.fsize, fthr=a.fthr, flip_tta=a.flip_tta,
        roi_scale=a.scale, roi_square=a.square, grid=a.grid, overlap=a.overlap,
        head_frac=a.head_frac, size_min_rel=a.size_min_rel, size_max_rel=a.size_max_rel
    )
