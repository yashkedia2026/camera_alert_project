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
        # Table for known employee entry/exit logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            date TEXT NOT NULL,
            first_seen TEXT,
            last_seen TEXT
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

def update_employee_log(name, db_path="alerts.db"):
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M:%S")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM employee_log
            WHERE employee_name = ? AND date = ?
        """, (name, date))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE employee_log
                SET last_seen = ?
                WHERE id = ?
            """, (time_now, row[0]))
        else:
            cursor.execute("""
                INSERT INTO employee_log (employee_name, date, first_seen, last_seen)
                VALUES (?, ?, ?, ?)
            """, (name, date, time_now, time_now))

        conn.commit()
        conn.close()
