# DAIOPH Streamlit Application

Modular Streamlit UI for the DAIOPH Edge AI platform.

## Overview

This is a modular, production-grade Streamlit implementation, structured for maintainability:

- `streamlit_app.py` — Entry point
- `state.py` — Session state management
- `session.py` — Session/telemetry tracking
- `components.py` — Reusable UI components

## Running

```bash
streamlit run apps/streamlit/streamlit_app.py
```

Or from the project root:

```bash
streamlit run apps/streamlit/streamlit_app.py --server.port 8501
```

## Features

- 💬 Chat with route selection (ODA / Hybrid / Cloud)
- 📊 Execution analytics and metrics
- 📜 Execution logs
- 🧠 Model status panel
- 🔑 Grok API key input (optional)

## Architecture

The Streamlit app is split into focused modules to avoid the monolithic pattern
of a single `streamlit_app.py` file:

| Module | Responsibility |
|--------|---------------|
| `streamlit_app.py` | App bootstrap, page config, tab layout |
| `state.py` | Session state defaults + helpers |
| `session.py` | Execution tracking and telemetry |
| `components.py` | Sidebar, chat, analytics, logs, models UI |