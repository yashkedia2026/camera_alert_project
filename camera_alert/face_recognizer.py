# camera_alert/face_recognizer.py

import face_recognition
import os
import cv2
import numpy as np

def load_known_faces(directory):
    known_encodings = []
    known_names = []

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)

        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(filename)[0])
    
    return known_encodings, known_names

def recognize_faces(frame, known_encodings, known_names):
    """
    Detect faces in `frame`, compare to known_encodings, draw boxes & names.
    Returns:
      - unknown_detected (bool): True if any face was labeled "Unknown"
      - annotated_frame (ndarray): the BGR image with boxes & labels drawn
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)
    
    annotated = frame.copy()
    unknown_detected = False

    for (top, right, bottom, left), encoding in zip(locations, encodings):
        # Compare against known
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Unknown"
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
        else:
            unknown_detected = True

        # Draw box
        cv2.rectangle(annotated, (left, top), (right, bottom), (0, 255, 0), 2)
        # Draw label
        cv2.putText(
            annotated, name, (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )

    return unknown_detected, annotated
