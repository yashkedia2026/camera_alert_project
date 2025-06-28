# camera_alert/time_utils.py
from datetime import datetime

def get_timestamped_filename(prefix="unknown", ext="jpg"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{ext}"
