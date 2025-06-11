#!/usr/bin/env python3
"""
sparse_optical_flow.py: Live sparse optical flow (Lucas-Kanade) on Basler camera feed.
"""
import os
# Fallback für Qt (Wayland/XCB)
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

import cv2
import numpy as np
import time
from pypylon import pylon
from capture_camera import Camera


def run_sparse_optical_flow(
    cam: Camera,
    max_corners: int = 100,
    quality_level: float = 0.3,
    min_distance: int = 7,
    block_size: int = 7
):
    """
    Zeigt Sparse Optical Flow (Lucas-Kanade) in einem OpenCV-Fenster.
    Beendet mit 'q' oder Ctrl+C.
    """
    # Frame-Größe aus Kamera-Params
    w = cam.params.get('width')
    h = cam.params.get('height')
    if w is None or h is None:
        raise ValueError("Camera must have width and height configured.")

    # Fenster vorbereiten
    cv2.namedWindow('OpticalFlow', cv2.WINDOW_NORMAL)
    color = np.random.randint(0, 255, (max_corners, 3))

    # Start Grabbing und erstes Frame holen
    cam.cam.StartGrabbing(pylon.GrabStrategy_OneByOne)
    grab = cam.cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
    if not grab.GrabSucceeded():
        grab.Release()
        raise RuntimeError("Initial frame grab failed.")
    frame = grab.Array
    grab.Release()

    # Graustufen und Typ sicherstellen (uint8)
    if frame.ndim == 2:
        prev_gray = frame
    else:
        prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if prev_gray.dtype != np.uint8:
        prev_gray = cv2.convertScaleAbs(prev_gray)

    # Initiale Eckpunkte
    p0 = cv2.goodFeaturesToTrack(
        prev_gray, maxCorners=max_corners,
        qualityLevel=quality_level,
        minDistance=min_distance,
        blockSize=block_size
    )
    # Maske für Zeichnung
    mask = np.zeros((h, w, 3), dtype=np.uint8)

    try:
        while True:
            grab = cam.cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            if not grab.GrabSucceeded():
                grab.Release()
                break
            frame = grab.Array
            grab.Release()

            # RGB und Graustufen
            if frame.ndim == 2:
                gray = frame
                vis = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                vis = frame.copy()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if gray.dtype != np.uint8:
                gray = cv2.convertScaleAbs(gray)

            # Wenn keine Punkte: neu detektieren
            if p0 is None or len(p0) == 0:
                p0 = cv2.goodFeaturesToTrack(
                    gray, maxCorners=max_corners,
                    qualityLevel=quality_level,
                    minDistance=min_distance,
                    blockSize=block_size
                )
                mask = np.zeros_like(vis)
                prev_gray = gray
            else:
                # Optical Flow berechnen
                p1, st, err = cv2.calcOpticalFlowPyrLK(
                    prev_gray, gray, p0, None,
                    winSize=(15, 15), maxLevel=2,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
                )
                # Nur gültige Punkte
                if p1 is not None and st is not None:
                    good_new = p1[st.flatten() == 1]
                    good_old = p0[st.flatten() == 1]

                    for i, (new, old) in enumerate(zip(good_new, good_old)):
                        a, b = new.ravel()
                        c, d = old.ravel()
                        mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), color[i % len(color)].tolist(), 2)
                        vis = cv2.circle(vis, (int(a), int(b)), 5, color[i % len(color)].tolist(), -1)

                    # Update für nächsten Loop
                    p0 = good_new.reshape(-1, 1, 2).astype(np.float32)
                    prev_gray = gray
                else:
                    # Keine validen Punkte mehr
                    p0 = None

            output = cv2.add(vis, mask)
            cv2.imshow('OpticalFlow', output)
            # Abbruch mit 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        if cam.cam.IsGrabbing():
            cam.cam.StopGrabbing()
        cv2.destroyAllWindows()
        cam.close()


if __name__ == '__main__':
    import yaml

    def load_config(path='config.yaml'):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    cfg = load_config()
    vcfg = cfg.get('video', {})
    cam = (
        Camera()
        .open()
        .set_auto_exposure(vcfg.get('auto_exposure', 'Continuous'))
        .set_exposure_time(vcfg.get('exposure', 25000))
        .set_gain(vcfg.get('gain', 1.0))
        .set_image_size(vcfg.get('width', 1280), vcfg.get('height', 720))
        .set_frame_rate(vcfg.get('fps', 60))
        .set_contrast_mode(vcfg.get('contrast_mode'))
        .set_contrast(vcfg.get('contrast'))
    )
    run_sparse_optical_flow(cam)