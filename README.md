**Camera Alert System**

A real-time surveillance application that monitors an RTSP camera stream, detects motion, recognizes known faces, logs unknown face events, and sends alerts via Telegram and automated calls.

---

## Features

* **Motion Detection**: Triggers processing only when significant movement occurs.
* **Face Recognition**: Compares detected faces against a directory of known individuals.
* **Alerting**: Sends unknown-face alerts after a configurable delay via:

  * Telegram Bot message
  * Automated phone call (Twilio)
* **Database Logging**: Records each alert event with timestamp, snapshot, and status in SQLite.
* **Configurable**: All settings (RTSP URL, tokens, thresholds) are managed via environment variables.
* **Modular Design**: Clear separation of concerns for easy maintenance and extensibility.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Environment Variables](#environment-variables)
7. [Logging](#logging)
8. [Testing](#testing)
9. [Contributing](#contributing)
10. [License](#license)

---

## Prerequisites

* Python 3.8 or higher
* ffmpeg (for RTSP support, optional)
* A Telegram Bot token and Chat ID
* A Twilio account (for call alerts)

---

## Installation
  
1. Clone the repository:
   ```
   https://github.com/yashkedia2026/camera_alert_project/edit/main/README.md
   cd camera_alert_project
   ```
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. Copy the example environment file and fill in your credentials:

   ```bash
   cp .env.example .env
   ```
2. Open `.env` and set each variable (see [Environment Variables](#environment-variables) below).

---

## Usage

Run the main monitoring script on Linux/macOS:

```bash
python -m camera_alert.main
```

Run on Windows (PowerShell):

````powershell
cd /d C:/Users/msi/Desktop/camera_alert_project
.\venv\Scripts\activate.bat
python -m camera_alert.main

```bash
python -m camera_alert.main
````

* Press `q` to quit the application gracefully.
* On disconnects, the script will attempt to reconnect automatically.

---

## Project Structure

```
camera_alert/
├── __init__.py
├── known_faces/
├── face_recognizer.py
├── logger.py
├── main.py
├── motion_detector.py
├── notifier.py
├── time_utils.py
├── utils.py
├── snapshots/
├── venv/
├── .gitignore
├── .env
├── alerts.db
├── README.md
└── requirements.txt

```

---

## Environment Variables

| Variable              | Description                                | Example                       |
| --------------------- | ------------------------------------------ | ----------------------------- |
| CAMERA\_RTSP\_URL     | RTSP stream URL                            | `rtsp://user:pass@ip:554/...` |
| TELEGRAM\_BOT\_TOKEN  | Telegram API token                         | `123456:ABC-DEF...`           |
| TELEGRAM\_CHAT\_ID    | Chat ID to send alerts to                  | `-1001234567890`              |
| TWILIO\_ACCOUNT\_SID  | Twilio Account SID                         | `ACXXXXXXXXXXXXXXXXXXXX`      |
| TWILIO\_AUTH\_TOKEN   | Twilio Auth Token                          | `your_auth_token`             |
| TWILIO\_FROM\_NUMBER  | Twilio phone number (E.164 format)         | `+12345678901`                |
| ALERT\_DELAY\_SECONDS | Seconds to wait before alerting on unknown | `300`                         |
| MOTION\_THRESHOLD     | Minimum pixel-difference count to trigger  | `5000`                        |
| LOG\_DB\_PATH         | Path to SQLite database file               | `alerts.db`                   |

---

## Logging

* All application logs are emitted via Python’s `logging` module.
* By default, logs are written to `logs/app.log` with rotation.
* You can configure log level via the `LOG_LEVEL` env var (e.g., `DEBUG`, `INFO`).

---

## Testing

1. Install dev dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```
2. Run unit tests:

   ```bash
   pytest
   ```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add some feature"`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request.

Please follow the existing code style (`black`, `flake8`, `mypy`).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
