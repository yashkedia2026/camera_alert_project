# camera_alert/notifier.py

import os
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Telegram settings ─────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# ── SMTP / Email settings ────────────────────────────────────────────────────
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER   = os.getenv("SMTP_USER")
SMTP_PASS   = os.getenv("SMTP_PASS")
EMAIL_FROM  = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_TO    = os.getenv("EMAIL_TO")  # comma-separated list

# ── Alert throttling ──────────────────────────────────────────────────────────
ALERT_INTERVAL   = float(os.getenv("ALERT_INTERVAL", "300"))  # seconds
_last_alert_time = {}


def send_alert(face_id: str, snapshot_path: str):
    """
    Sends a notification message via Telegram and/or email for the given face.
    """
    global _last_alert_time

    now = time.time()
    last = _last_alert_time.get(face_id)
    if last is not None and (now - last) < ALERT_INTERVAL:
        return
    _last_alert_time[face_id] = now

    message = f"🚨 {face_id} detected. Snapshot saved: {snapshot_path}"

    # 1) Telegram alert
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            resp = requests.post(url, data=data, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Telegram alert failed: {e}")

    # 2) Email alert
    if SMTP_SERVER and SMTP_USER and SMTP_PASS and EMAIL_TO:
        try:
            msg = MIMEMultipart()
            msg["From"]    = EMAIL_FROM
            msg["To"]      = EMAIL_TO
            msg["Subject"] = f"Camera Alert: {face_id} Detected"
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(EMAIL_FROM, EMAIL_TO.split(","), msg.as_string())
        except Exception as e:
            print(f"[ERROR] Email alert failed: {e}")
