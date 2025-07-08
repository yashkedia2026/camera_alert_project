# camera_alert/main.py

import os
import cv2
import time
from dotenv import load_dotenv
import face_recognition

# Load environment variables
load_dotenv()

# Suppress OpenCV logs
if hasattr(cv2, 'utils') and hasattr(cv2.utils, 'logging'):
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)

from camera_alert.face_recognizer import load_known_faces, recognize_faces
from camera_alert.motion_detector import MotionDetector
from camera_alert.logger import init_db, log_event
from camera_alert.notifier import send_alert
from camera_alert.utils import save_snapshot
from camera_alert.time_utils import get_timestamped_filename
# from camera_alert.time_utils import is_within_operating_hours

def main():
    init_db()
    os.makedirs("snapshots", exist_ok=True)

    rtsp_url = os.getenv("CAMERA_RTSP")
    if not rtsp_url:
        print("[ERROR] CAMERA_RTSP not set in .env file.")
        return

    ALERT_INTERVAL = float(os.getenv("ALERT_INTERVAL", "300"))
    CLUSTER_THRESHOLD = float(os.getenv("CLUSTER_THRESHOLD", "0.5"))

    known_encs, known_names = load_known_faces("camera_alert/known_faces")
    motion_detector = MotionDetector()

    unknown_memory = {}         # cluster_id -> encoding
    last_alert = {}             # cluster_id -> timestamp
    next_cluster_id = 1

    print(f"[INFO] Connecting to RTSP stream: {rtsp_url}")
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        "rtsp_transport;tcp|buffer_size;1024000|max_delay;500000|"
        "stimeout;10000000|fps;15|flags;low_delay|loglevel;quiet"
    )

    cam = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 0)

    if not cam.isOpened():
        print("[ERROR] Could not open RTSP stream.")
        return

    print("[INFO] Monitoring started... Press 'q' to quit.")
    while True:
        # Optional time restriction logic
        # if not is_within_operating_hours():
        #     time.sleep(60)
        #     continue

        ret, frame = cam.read()
        if not ret or frame is None or frame.sum() < 1000:
            print("[WARNING] Corrupted or black frame skipped.")
            time.sleep(1)
            continue

        display = frame.copy()

        if motion_detector.detect(frame):
            # Downscale for performance
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            enc_list, raw_ids, annotated = recognize_faces(
                small_frame, known_encs, known_names
            )

            # Resize annotated result back to original size
            annotated = cv2.resize(annotated, (frame.shape[1], frame.shape[0]))
            display = annotated

            now = time.time()

            for enc, raw_id in zip(enc_list, raw_ids):
                if raw_id in known_names:
                    continue

                # Cluster similar unknowns
                cluster_id = None
                for cid, centroid in unknown_memory.items():
                    if face_recognition.face_distance([centroid], enc)[0] < CLUSTER_THRESHOLD:
                        cluster_id = cid
                        break

                if cluster_id is None:
                    cluster_id = next_cluster_id
                    unknown_memory[cluster_id] = enc
                    next_cluster_id += 1

                # Alert throttling
                last = last_alert.get(cluster_id)
                if last is None or (now - last) >= ALERT_INTERVAL:
                    last_alert[cluster_id] = now
                    face_label = f"Unknown_{cluster_id}"

                    print(f"[ALERT] {face_label} detected! Saving snapshot...")
                    fname = get_timestamped_filename(prefix=face_label, ext="jpg")
                    path = save_snapshot(annotated, fname)

                    log_event(face_label, path)
                    send_alert(face_label, path)

        # Display feed
        cv2.imshow("Camera Feed", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
