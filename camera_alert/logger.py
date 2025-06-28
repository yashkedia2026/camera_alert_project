# camera_alert/logger.py

import sqlite3
from datetime import datetime

def init_db(db_path="alerts.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unknown_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            snapshot_path TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_event(name, snapshot_path, db_path="alerts.db"):
    """
    Records one unknown-face event into the SQLite table,
    storing the given name, current timestamp, and path.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO unknown_faces (name, timestamp, snapshot_path)
        VALUES (?, ?, ?)
    """, (name, timestamp, snapshot_path))
    conn.commit()
    conn.close()
