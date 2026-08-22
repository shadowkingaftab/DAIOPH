# Desktop Deployment

## Overview

DAIOPH runs as a native desktop application with a system tray, local API server, and optional web UI.

## Installation

### From Source

```bash
git clone https://github.com/shadowkingaftab/DAIOPH.git
cd DAIOPH
pip install -r requirements.txt
python apps/desktop/src/main.py
```

### Requirements

- Windows 10/11, macOS 12+, or Linux (X11/Wayland)
- Python 3.11+
- 4GB RAM minimum (8GB recommended)

## Application Structure

```
apps/desktop/
├── src/
│   ├── main.py          # Entry point
│   ├── application.py   # App lifecycle
│   ├── tray.py          # System tray integration
│   ├── windows.py       # Window management
│   └── updater.py       # Auto-update
└── assets/
    ├── icon.svg
    └── manifest.json
```

## Features

### System Tray
- Quick access to DAIOPH status
- Start/stop the local server
- Model management shortcuts
- Settings access

### Local Server
The desktop app runs the API server on `localhost:8000`:
- Chat interface at the bundled web UI
- REST API for integrations
- WebSocket for real-time updates

### Auto-Updates (`updater.py`)
- Checks for new releases
- Downloads and verifies updates
- Applies updates on restart

## Configuration

Desktop-specific settings in the app config:
- Start on login (OS-dependent)
- Server port
- Model preferences
- Privacy settings

## First Run

1. Launch the application
2. Grant necessary permissions (filesystem, notifications)
3. Wait for initial model download (or skip for API-only mode)
4. Start chatting via the tray menu or web UI

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in settings |
| Tray icon missing | Check platform tray support |
| Models won't download | Check disk space and network |
| High CPU usage | Enable power saving in settings |

## Uninstallation

1. Quit from tray menu
2. Remove application directory
3. Optionally remove `data/` directory (contains memories)