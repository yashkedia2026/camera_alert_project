# camera_alert/main.py

import os
import cv2
import time
from dotenv import load_dotenv

load_dotenv()

from camera_alert.face_recognizer import load_known_faces, recognize_faces
from camera_alert.motion_detector import MotionDetector
from camera_alert.notifier import send_alert
from camera_alert.logger import init_db, log_event
from camera_alert.utils import save_snapshot
from camera_alert.time_utils import get_timestamped_filename

def main():
    # ─── Setup ───────────────────────────────────────────
    init_db()
    os.makedirs("snapshots", exist_ok=True)

    # RTSP URL from .env
    rtsp_url = os.getenv("CAMERA_RTSP")
    if not rtsp_url:
        print("[ERROR] CAMERA_RTSP not found in environment.")
        return

    # how often to alert on unknown (seconds; default 300s = 5m)
    ALERT_INTERVAL = float(os.getenv("ALERT_INTERVAL", "300"))
    last_alert_time = 0.0

    print(f"[INFO] Connecting to RTSP stream: {rtsp_url}")
    # quiet ffmpeg and set a 5s timeout
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        "rtsp_transport;tcp"
        "|stimeout;5000000"
        "|loglevel;quiet"
    )
    camera = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not camera.isOpened():
        print("[ERROR] Could not open RTSP stream with FFMPEG backend.")
        return

    known_encodings, known_names = load_known_faces("camera_alert/known_faces")
    motion_detector = MotionDetector()

    print("[INFO] Monitoring started... Press 'q' to quit.")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("[WARNING] Frame grab failed; retrying in 3s…")
            time.sleep(3)
            camera.release()
            camera = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            continue

        display_frame = frame

        if motion_detector.detect(frame):
            now = time.time()
            # only check faces & possibly alert if interval has passed
            if now - last_alert_time >= ALERT_INTERVAL:
                unknown, annotated = recognize_faces(frame, known_encodings, known_names)
                display_frame = annotated

                if unknown:
                    # reset the timer **only when** we alert
                    last_alert_time = now

                    print("[ALERT] Unknown person detected! 📸 Saving snapshot…")  
                    fname = get_timestamped_filename(prefix="unknown", ext="jpg")
                    path = save_snapshot(annotated, fname)

                    # log & notify
                    log_event("Unknown person detected", path)
                    send_alert(f"🚨 Unknown person detected! Snapshot saved to {path}")

        cv2.imshow("Camera Feed", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
