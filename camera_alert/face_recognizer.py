# camera_alert/face_recognizer.py

import os
import hashlib
import numpy as np
import cv2
import face_recognition
from datetime import datetime, date
import sqlite3
from camera_alert.logger import update_employee_log
# Configurable matching tolerance (distance threshold)
TOLERANCE = float(os.getenv("FACE_TOLERANCE", "0.6"))

def load_known_faces(directory: str):
    """
    Load and encode known faces from the specified directory.
    Returns two lists: encodings and corresponding names.
    """
    known_encs = []
    known_names = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(directory, filename)
            image = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(image)
            if encs:
                known_encs.append(encs[0])
                known_names.append(os.path.splitext(filename)[0])
    return known_encs, known_names

def recognize_faces(frame: np.ndarray, known_encodings, known_names):
    """
    Detects faces and returns:
      - enc_list: list of face encoding arrays
      - face_ids: list of strings (known name or Unknown_<hash>)
      - annotated_frame: BGR image with drawn boxes and labels
    """
    rgb       = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    enc_list  = face_recognition.face_encodings(rgb, locations)

    annotated = frame.copy()
    face_ids  = []

    for loc, enc in zip(locations, enc_list):
        # match against known encodings
        if known_encodings:
            dists    = face_recognition.face_distance(known_encodings, enc)
            best_idx = int(np.argmin(dists))
            if dists[best_idx] < TOLERANCE:
                fid = known_names[best_idx]
                from camera_alert.logger import update_employee_log
                update_employee_log(fid)

            else:
                h = hashlib.sha256(enc.tobytes()).hexdigest()[:8]
                fid = f"Unknown_{h}"
        else:
            h = hashlib.sha256(enc.tobytes()).hexdigest()[:8]
            fid = f"Unknown_{h}"

        face_ids.append(fid)

        # draw box & label
        top, right, bottom, left = loc
        cv2.rectangle(annotated, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(
            annotated, fid, (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
        )

    return enc_list, face_ids, annotated