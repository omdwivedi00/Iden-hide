"""
Face Detection Module
"""

import os
import cv2
import numpy as np
import onnxruntime as ort
from ultralytics import YOLO

def expand_xyxy(box, scale, W, H, square=True):
    x1,y1,x2,y2 = [float(v) for v in box]
    cx, cy = (x1+x2)/2.0, (y1+y2)/2.0
    w, h = x2-x1, y2-y1
    if square:
        s = scale * max(w, h); w = h = s
    else:
        w, h = scale*w, scale*h
    nx1, ny1 = max(0.0, cx-w/2.0), max(0.0, cy-h/2.0)
    nx2, ny2 = min(W-1.0, cx+w/2.0), min(H-1.0, cy+h/2.0)
    return [nx1, ny1, nx2, ny2]

def nms_xyxy(boxes, scores, iou_thr=0.5):
    if not boxes:
        return []
    B = np.asarray(boxes, np.float32); S = np.asarray(scores, np.float32)
    order = S.argsort()[::-1]; keep=[]
    while order.size>0:
        i = order[0]; keep.append(i)
        rest = order[1:]
        xx1 = np.maximum(B[i,0], B[rest,0]); yy1 = np.maximum(B[i,1], B[rest,1])
        xx2 = np.minimum(B[i,2], B[rest,2]); yy2 = np.minimum(B[i,3], B[rest,3])
        w = np.maximum(0, xx2-xx1); h = np.maximum(0, yy2-yy1)
        inter = w*h
        area_i = (B[i,2]-B[i,0])*(B[i,3]-B[i,1])
        area_r = (B[rest,2]-B[rest,0])*(B[rest,3]-B[rest,1])
        iou = inter/(area_i+area_r-inter+1e-6)
        order = rest[iou<=iou_thr]
    return keep

class DetectFace:
    def __init__(self, yolo_model_path='models/yolo11n.pt', person_conf=0.20, face_det_size=1280, face_det_thresh=0.30, roi_scale=1.45):
        self.yolo_model_path = yolo_model_path
        self.person_conf = person_conf
        self.face_det_size = face_det_size
        self.face_det_thresh = face_det_thresh
        self.roi_scale = roi_scale
        
        # Load YOLO model
        self.yolo = YOLO(yolo_model_path)
        
        # Load InsightFace
        from insightface.app import FaceAnalysis
        self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], allowed_modules=['detection'])
        self.app.prepare(ctx_id=0, det_size=(face_det_size, face_det_size))
        
        det = self.app.models.get('detection', None)
        if det:
            det.det_thresh = face_det_thresh
            det.nms_thresh = 0.45

    def detect_faces(self, image):
        """Detect faces in image"""
        H, W = image.shape[:2]
        
        # YOLO person detection
        yres = self.yolo.predict(image, conf=self.person_conf, classes=[0], verbose=False)[0]
        persons = [b.xyxy[0].tolist() for b in yres.boxes]
        
        face_boxes, face_scores = [], []
        
        # Fallback: tiled whole-frame detection
        if not face_boxes:
            gh, gw, ov = 2, 2, 0.15
            stepx, stepy = int(W/gw), int(H/gh)
            ox, oy = int(ov*stepx), int(ov*stepy)
            for gy in range(gh):
                for gx in range(gw):
                    tx1 = max(0, gx*stepx - ox); ty1 = max(0, gy*stepy - oy)
                    tx2 = min(W, (gx+1)*stepx + ox); ty2 = min(H, (gy+1)*stepy + oy)
                    tile = image[ty1:ty2, tx1:tx2]
                    tr = cv2.resize(tile, (self.face_det_size, self.face_det_size), interpolation=cv2.INTER_CUBIC)
                    faces = self.app.get(tr)
                    sx = (tx2 - tx1) / float(self.face_det_size)
                    sy = (ty2 - ty1) / float(self.face_det_size)
                    for f in faces:
                        bx1,by1,bx2,by2 = f.bbox.astype(float)
                        face_boxes.append([tx1 + bx1*sx, ty1 + by1*sy, tx1 + bx2*sx, ty1 + by2*sy])
                        face_scores.append(float(getattr(f, "det_score", 1.0)))
        
        # Apply NMS
        keep = nms_xyxy(face_boxes, face_scores, iou_thr=0.5)
        
        # Return results
        results = []
        for i in keep:
            results.append({
                'bbox': [int(face_boxes[i][0]), int(face_boxes[i][1]), int(face_boxes[i][2]), int(face_boxes[i][3])],
                'confidence': float(face_scores[i])
            })
        
        return results
