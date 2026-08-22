# REST API

## Overview

DAIOPH exposes a REST API via FastAPI (`APIs/rest/app.py`). The default endpoint is `http://localhost:8000`.

## Authentication

Local access requires no authentication by default. Remote access uses bearer tokens:

```
Authorization: Bearer <token>
```

## Endpoints

### Health & Status

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check |
| GET | `/status` | Full system status |

### Chat (`/api/chat`)

**POST** `/api/chat`

```json
{
  "message": "What's the weather like?",
  "session_id": "optional-session-id",
  "stream": false
}
```

Response:
```json
{
  "response": "I can help with that...",
  "session_id": "abc123",
  "confidence": 0.92,
  "intent": "weather.query",
  "latency_ms": 340
}
```

### Memory (`/api/memory`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/memory/episodes` | List episodic memories |
| GET | `/api/memory/search?q=` | Semantic search |
| DELETE | `/api/memory/{id}` | Delete a memory |

### Device (`/api/device`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/device/info` | Hardware information |
| GET | `/api/device/profile` | Current hardware profile |
| GET | `/api/device/battery` | Battery status |

### Models (`/api/models`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/models` | List available models |
| POST | `/api/models/load` | Load a model |
| POST | `/api/models/unload` | Unload a model |

## Error Format

```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model 'llama-3b' is not installed",
    "details": {}
  }
}
```

Error codes align with `core/errors/`.

## Rate Limiting

Production mode enforces rate limits (default: 100 req/min). Exceeded requests receive `429 Too Many Requests`.

## OpenAPI

Interactive docs at `/docs`, schema at `/openapi.json`.