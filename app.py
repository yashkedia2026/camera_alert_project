import os
import sqlite3
import cv2
from flask import Flask, Response, jsonify, send_from_directory
from camera_alert.logger import init_db

# ─── Flask setup: serve static/ at the web root ───────────────────────────────
app = Flask(
    __name__,
    static_folder="static",   # on-disk folder for index.html, styles.css, script.js
    static_url_path=""        # serve them at e.g. /index.html, /styles.css, /script.js
)

# Ensure our SQLite table exists
init_db()

# ─── Serve dashboard (index.html) ─────────────────────────────────────────────
@app.route("/")
def dashboard():
    return app.send_static_file("index.html")


# ─── MJPEG RTSP stream endpoint ────────────────────────────────────────────────
def gen_mjpeg():
    rtsp = os.getenv("CAMERA_RTSP")
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        "rtsp_transport;tcp|stimeout;5000000|loglevel;quiet"
    )
    cap = cv2.VideoCapture(rtsp, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        ret, buf = cv2.imencode(".jpg", frame)
        if not ret:
            continue
        jpg = buf.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        )
    cap.release()

@app.route("/api/stream")
def mjpeg_stream():
    return Response(
        gen_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ─── Event log JSON endpoint ──────────────────────────────────────────────────
@app.route("/api/events")
def get_events():
    conn = sqlite3.connect("alerts.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
      SELECT id, name, timestamp, snapshot_path
        FROM unknown_faces
       ORDER BY id DESC
       LIMIT 50
    """)
    rows = cur.fetchall()
    conn.close()

    events = []
    for r in rows:
        fname = os.path.basename(r["snapshot_path"])
        events.append({
            "id":            r["id"],
            "name":          r["name"],
            "timestamp":     r["timestamp"],
            # load directly from the root-level snapshots/ folder:
            "snapshot_path": f"/snapshots/{fname}"
        })

    return jsonify(events)


# ─── Serve snapshots from the project root ────────────────────────────────────
@app.route("/snapshots/<path:filename>")
def serve_snapshots(filename):
    # snapshots/ lives alongside app.py
    return send_from_directory(os.path.join(os.getcwd(), "snapshots"), filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
