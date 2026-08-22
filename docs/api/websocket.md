# WebSocket API

## Overview

DAIOPH provides a WebSocket endpoint for real-time, bidirectional communication: streaming chat responses, live status updates, and event push.

## Connection

```
ws://localhost:8000/ws
```

Optional authentication via query parameter:
```
ws://localhost:8000/ws?token=<bearer-token>
```

## Message Format

All messages are JSON with a `type` field:

```json
{
  "type": "message_type",
  "payload": { ... },
  "id": "optional-correlation-id"
}
```

## Client → Server Messages

### Chat Request
```json
{
  "type": "chat.request",
  "payload": {
    "message": "Hello!",
    "session_id": "abc123",
    "stream": true
  },
  "id": "req-1"
}
```

### Cancel Request
```json
{
  "type": "chat.cancel",
  "payload": { "request_id": "req-1" }
}
```

### Ping
```json
{ "type": "ping" }
```

## Server → Client Messages

### Stream Chunk
```json
{
  "type": "chat.chunk",
  "payload": {
    "request_id": "req-1",
    "delta": "Hel",
    "index": 0
  }
}
```

### Stream Complete
```json
{
  "type": "chat.complete",
  "payload": {
    "request_id": "req-1",
    "confidence": 0.95,
    "intent": "greeting",
    "latency_ms": 210
  }
}
```

### Error
```json
{
  "type": "error",
  "payload": {
    "code": "MODEL_ERROR",
    "message": "Inference failed"
  }
}
```

### Status Update
```json
{
  "type": "status.update",
  "payload": {
    "state": "ready",
    "models_loaded": ["qwen-0.5b"],
    "cpu_percent": 34
  }
}
```

### Pong
```json
{ "type": "pong" }
```

## Streaming Flow

```
Client                    Server
  │── chat.request ────────→│
  │                         │ (process)
  │←── chat.chunk (0) ──────│
  │←── chat.chunk (1) ──────│
  │←── chat.chunk (n) ──────│
  │←── chat.complete ───────│
```

## Reconnection

Clients should implement exponential backoff reconnection (1s → 30s max). Missed events can be recovered via the REST API or event replay.

## Heartbeat

Send `ping` every 30s. If no `pong` within 10s, reconnect.