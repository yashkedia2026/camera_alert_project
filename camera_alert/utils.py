# camera_alert/utils.py

import cv2
import os

def save_snapshot(frame, filename, folder="snapshots"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])  # High quality
    return path
