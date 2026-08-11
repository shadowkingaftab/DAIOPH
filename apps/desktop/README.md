# DAIOPH Desktop Application

Native desktop client for the DAIOPH Edge AI platform.

## Overview

The desktop application provides a system-tray based interface for running
DAIOPH's edge AI orchestration locally, with support for:
- Background edge inference (Qwen2-0.5B via GGUF)
- System tray integration
- Automatic model management
- Desktop notifications

## Structure

```
apps/desktop/
├── assets/           # Icons, manifests, and branding
├── src/
│   ├── main.py       # Entry point
│   ├── application.py # Application lifecycle
│   ├── tray.py       # System tray integration
│   ├── windows.py    # Window management
│   └── updater.py    # Self-update logic
└── README.md
```

## Running

```bash
python apps/desktop/src/main.py
```

## Requirements

- Python 3.10+
- DAIOPH core packages installed (`pip install -r requirements.txt`)

## Roadmap

- [ ] Native GUI window (Qt/Tkinter)
- [ ] Model download manager
- [ ] GPU acceleration detection
- [ ] Auto-start on boot
- [ ] Update channel selection (stable/beta)