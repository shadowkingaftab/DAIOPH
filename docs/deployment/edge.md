# Edge Deployment

## Overview

DAIOPH Edge runs on resource-constrained devices: Raspberry Pi, Jetson, NUCs, and similar hardware. It prioritizes energy efficiency and offline operation.

## Supported Devices

| Device | RAM | Notes |
|--------|-----|-------|
| Raspberry Pi 4/5 | 4–8GB | CPU-only, int8 quantization |
| NVIDIA Jetson Nano/Orin | 4–8GB | GPU acceleration available |
| Intel NUC | 8–16GB | Full local model support |
| Android (Termux) | 4GB+ | Experimental |

## Installation

### Automated Install

```bash
curl -sSL https://raw.githubusercontent.com/shadowkingaftab/DAIOPH/main/deployment/edge/install.sh | sudo bash
```

Or manually:
```bash
git clone https://github.com/shadowkingaftab/DAIOPH.git /opt/daioph
cd /opt/daioph
pip install -r requirements.txt
sudo cp deployment/edge/daioph.service /etc/systemd/system/
sudo systemctl enable --now daioph
```

### Docker (Edge Image)

```bash
docker build -f deployment/docker/Dockerfile.edge -t daioph-edge .
docker run -d --name daioph-edge \
  --device /dev/dri \
  -v daioph-data:/app/data \
  -p 8000:8000 \
  daioph-edge
```

## Configuration

Edge-specific configuration in `configs/edge/config.yaml`:

- **Power saving**: Enabled by default; defers heavy tasks
- **Model limits**: Max model size 1GB
- **Memory caps**: Reduced memory store sizes
- **Multimodal**: Disabled by default (enable selectively)

Hardware profiles in `configs/edge/hardware.yaml` match device classes to appropriate models.

## Energy Management

The energy manager (`hardware/energy_manager.py`):
- Monitors battery level (if applicable)
- Pauses federated learning below 20% battery
- Reduces inference frequency in power saving mode
- Schedules heavy tasks during charging/idle periods

## Systemd Service

```ini
[Unit]
Description=DAIOPH Edge Service
After=network.target

[Service]
Type=simple
User=daioph
WorkingDirectory=/opt/daioph
ExecStart=/usr/bin/python3 deployment/edge/service.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Performance Expectations

| Device | Model | Latency (first token) |
|--------|-------|----------------------|
| Pi 4 | Qwen 0.5B int8 | ~2–4s |
| Jetson Nano | Qwen 0.5B int8 | ~1–2s |
| NUC i7 | Qwen 1.5B int8 | ~0.5–1s |

## Monitoring

```bash
# Service status
systemctl status daioph

# Logs
journalctl -u daioph -f

# Health check
curl http://localhost:8000/health
```

## Updating

```bash
cd /opt/daioph
git pull
pip install -r requirements.txt
sudo systemctl restart daioph