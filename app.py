# app.py
import os
import cv2
import sqlite3
import pandas as pd
import io
import csv

from io import BytesIO
from flask import (
    Flask, Response, jsonify, send_from_directory,
    request, send_file
)
from camera_alert.logger import init_db

# ── Flask setup ─────────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)

# Ensure our tables exist
init_db()


# ── Dashboard HTML ─────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    return app.send_static_file("index.html")


# ── MJPEG Stream via OpenCV (no FFmpeg) ─────────────────────────────────────────
def gen_mjpeg():
    rtsp = os.getenv("CAMERA_RTSP")
    cap  = cv2.VideoCapture(rtsp)
    if not cap.isOpened():
        raise RuntimeError("Cannot open RTSP stream")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ok, buf = cv2.imencode(
            ".jpg", frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        )
        if not ok:
            continue
        jpg = buf.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpg +
            b"\r\n"
        )
    cap.release()


@app.route("/api/stream")
def mjpeg_stream():
    return Response(
        gen_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ── Unknown-Face Events API ─────────────────────────────────────────────────────
@app.route("/api/events")
def get_events():
    start = request.args.get("start")
    end   = request.args.get("end")
    fmt   = request.args.get("format", "").lower()

    conn = sqlite3.connect("alerts.db")
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()

    if start and end:
        cur.execute("""
            SELECT id, name, timestamp, snapshot_path
              FROM unknown_faces
             WHERE date(timestamp) BETWEEN ? AND ?
             ORDER BY timestamp DESC
        """, (start, end))
    else:
        cur.execute("""
            SELECT id, name, timestamp, snapshot_path
              FROM unknown_faces
             ORDER BY timestamp DESC
             LIMIT 50
        """)

    rows = cur.fetchall()
    conn.close()

    # Build a simple list of dicts, *defining fname* for each row*
    events = []
    for r in rows:
        fname = os.path.basename(r["snapshot_path"])
        events.append({
            "id":            r["id"],
            "name":          r["name"] or "",
            "timestamp":     r["timestamp"],
            "snapshot_path": f"/snapshots/{fname}"
        })

    # If ?format=csv, stream a CSV
    if fmt == "csv":
        si     = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(["ID", "Name", "Timestamp", "Snapshot"])
        for e in events:
            # use the same key names as above
            writer.writerow([
                e["id"],
                e["name"],
                e["timestamp"],
                os.path.basename(e["snapshot_path"])
            ])
        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=unknown_events.csv"}
        )

    # Otherwise return JSON
    return jsonify(events)


@app.route("/api/delete_event/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    conn = sqlite3.connect("alerts.db")
    cur  = conn.cursor()
    cur.execute(
        "DELETE FROM unknown_faces WHERE id=?",
        (event_id,)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/api/clear_events", methods=["DELETE"])
def clear_events():
    conn = sqlite3.connect("alerts.db")
    cur  = conn.cursor()
    cur.execute("DELETE FROM unknown_faces")
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/snapshots/<path:filename>")
def serve_snapshots(filename):
    return send_from_directory(
        os.path.join(os.getcwd(), "snapshots"),
        filename
    )


# ── Employee Attendance API ────────────────────────────────────────────────────
@app.route("/api/employee_log")
def employee_log():
    start = request.args.get("start")
    end   = request.args.get("end")

    conn = sqlite3.connect("alerts.db")
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()

    if start and end:
        cur.execute("""
            SELECT employee_name AS name,
                   date            AS date,
                   first_seen,
                   last_seen
              FROM employee_log
             WHERE date BETWEEN ? AND ?
             ORDER BY date DESC, employee_name
        """, (start, end))
    else:
        cur.execute("""
            SELECT employee_name AS name,
                   date            AS date,
                   first_seen,
                   last_seen
              FROM employee_log
             ORDER BY date DESC, employee_name
        """)

    rows = cur.fetchall()
    conn.close()

    # Return list of dicts
    return jsonify([
        {
            "name":       r["name"] or "",
            "date":       r["date"],
            "first_seen": r["first_seen"],
            "last_seen":  r["last_seen"],
        }
        for r in rows
    ])


@app.route("/api/delete_employee_log", methods=["DELETE"])
def delete_employee_log():
    data  = request.get_json()
    name  = data.get("employee_name")
    date_ = data.get("date")

    conn = sqlite3.connect("alerts.db")
    cur  = conn.cursor()
    cur.execute(
        "DELETE FROM employee_log WHERE employee_name=? AND date=?",
        (name, date_)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


# ── Export Attendance as Excel ─────────────────────────────────────────────────
@app.route("/api/export_attendance")
def export_attendance():
    start = request.args.get("start")
    end   = request.args.get("end")

    conn = sqlite3.connect("alerts.db")
    df   = pd.read_sql_query(
        f"""
        SELECT employee_name as Employee,
               date          as Date,
               first_seen    as FirstSeen,
               last_seen     as LastSeen
          FROM employee_log
         {"WHERE date BETWEEN ? AND ?" if start and end else ""}
         ORDER BY date, employee_name
        """,
        conn,
        params=(start, end) if start and end else None
    )
    conn.close()

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Attendance"
        )
    buf.seek(0)

    return send_file(
        buf,
        mimetype=(
            "application/vnd.openxmlformats"
            "-officedocument.spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name=(
            f"attendance_{start or 'all'}_"
            f"{end or ''}.xlsx"
        )
    )


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
