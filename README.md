# Unknown Person Alert System

Monitors live camera feed. If an unknown face is detected:
1. Sends you an instant notification (Telegram/SMS)
2. If still present after 5 minutes, calls you

## Requirements
- Python 3.8+
- EZVIZ camera with RTSP enabled
-  directory with subfolders per person

## Run
```bash
source venv/bin/activate
python -m camera_alert.main
```
