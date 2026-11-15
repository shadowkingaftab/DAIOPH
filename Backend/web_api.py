"""HTTP API for the React web application."""

from __future__ import annotations

import os
import platform
import re
import time
import uuid
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from privacy import redact_sensitive_text
except ImportError:
    from Backend.privacy import redact_sensitive_text

load_dotenv()
app = FastAPI(title="DAIOPH API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
STARTED_AT = time.time()
HISTORY: list[dict] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    route: Literal["ODA", "Hybrid", "Cloud"] = "Hybrid"


_HYBRID_TRANSLATION = re.compile(
    r"\b(?:(?:and\s+)?then\s+|and\s+)?translate\b.{0,120}?"
    r"\b(?:into|to)\s+"
    r"(?P<language>[A-Za-z]+(?:[- ][A-Za-z]+)*?)"
    r"(?=\s+(?:and|then|for|while|but|please)\b|[.,!?;:]|$)",
    re.IGNORECASE | re.DOTALL,
)


def _run_hybrid_translation(prompt: str) -> tuple[str, int] | None:
    match = _HYBRID_TRANSLATION.search(prompt)
    if match is None:
        return None

    language = match.group("language").strip()
    writing_request = prompt[:match.start()].strip(" \t\r\n,;:")
    if not writing_request:
        writing_request = prompt

    from qwen_oda import run_qwen

    draft_prompt = (
        "Complete only the source-language writing part of this request. "
        "Do not translate or explain it. Return only the requested text.\n\n"
        f"Writing request: {writing_request}"
    )
    draft = run_qwen(draft_prompt).strip()
    if not draft or draft.startswith(("⚠", "❌", "Qwen inference error:")):
        raise HTTPException(
            status_code=503,
            detail=f"Hybrid local ODA drafting failed: {draft or 'empty response'}",
        )

    translation_prompt = (
        f"Translate the following text into {language}. Preserve its meaning, "
        "tone, and placeholders. Return only the translation.\n\n"
        f"{draft}"
    )
    translation_prompt, redactions = redact_sensitive_text(translation_prompt)

    from grok_cloud import run_grok

    translation = run_grok(translation_prompt).strip()
    if not translation or translation.startswith(("⚠", "❌", "Grok API Error")):
        failure = classify_grok_failure(translation)
        raise HTTPException(
            status_code=503,
            detail=(
                "Hybrid cloud translation failed after the local draft was "
                f"created. {failure}"
            ),
        )

    return f"{draft}\n\n{language} translation:\n{translation}", redactions


@app.get("/api/health")

def classify_grok_failure(translation: str) -> str:
    """Return a user-facing Grok failure message without raw provider details.

    The raw error text from Grok (model names, HTTP status codes, error
    codes, credit/spending-limit reasons, etc.) must never reach the UI.
    """
    lowered = translation.casefold()

    # Explicit credit/spending-limit signal from the provider.
    if "credit" in lowered or "spending limit" in lowered:
        return "The Grok account has no available credits or has reached its spending limit."

    # Auth / unauthorized means credentials or account permissions are wrong.
    if "401" in lowered or "403" in lowered or "permission" in lowered:
        return "Grok authentication failed. Verify your Grok API key and account permissions."

    # Rate limiting / capacity signals.
    if "429" in lowered or "rate limit" in lowered or "capacity" in lowered:
        return "Grok is currently unavailable due to rate limiting or insufficient capacity."

    # Connection/timeouts should be surfaced as a clear infrastructure problem.
    if "timeout" in lowered or "connection" in lowered or "network" in lowered:
        return "Grok could not be reached. Check your network connection and Grok service status."

    # Catch-all: keep the message helpful but generic.
    return "Grok translation failed. Retry the request or check your Grok API configuration."
def health() -> dict:
    return {"status": "ok", "version": app.version, "uptime": int(time.time() - STARTED_AT)}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    original = request.message.strip()
    if not original:
        raise HTTPException(status_code=422, detail="Message cannot be blank")

    route = request.route
    prompt = original
    redactions = 0
    if route in ("Cloud", "Hybrid"):
        prompt, redactions = redact_sensitive_text(prompt)

    if route == "ODA":
        from qwen_oda import run_qwen
        answer = run_qwen(prompt)
        source = "ODA"
    elif route == "Cloud":
        from grok_cloud import run_grok
        answer = run_grok(prompt)
        source = "Cloud"
        if answer.startswith(("⚠", "❌")):
            raise HTTPException(status_code=503, detail=answer)
    else:
        hybrid_result = _run_hybrid_translation(prompt)
        if hybrid_result is not None:
            answer, translation_redactions = hybrid_result
            redactions += translation_redactions
            source = "Hybrid"
        else:
            from grok_cloud import run_grok
            answer = run_grok(prompt) if os.getenv("GROK_API_KEY", "").strip() else ""
            source = "Cloud" if answer and not answer.startswith(("⚠", "❌")) else "ODA"
            if source == "ODA":
                from qwen_oda import run_qwen
                answer = run_qwen(prompt)

    response = {
        "id": str(uuid.uuid4()), "role": "assistant", "content": answer,
        "timestamp": int(time.time() * 1000), "route": source,
        "redacted_count": redactions,
    }
    HISTORY.extend([
        {"id": str(uuid.uuid4()), "role": "user", "content": original,
         "timestamp": int(time.time() * 1000), "route": route},
        response,
    ])
    del HISTORY[:-200]
    return response


@app.get("/api/chat/history")
def chat_history() -> list[dict]:
    return HISTORY[-100:]


@app.get("/api/device/status")
def device_status() -> dict:
    try:
        import psutil
        memory = psutil.virtual_memory()
        total, used = round(memory.total / 1024**2, 1), round(memory.used / 1024**2, 1)
        cores = psutil.cpu_count() or os.cpu_count() or 1
        cpu = platform.processor() or platform.machine()
    except ImportError:
        total = used = 0
        cores = os.cpu_count() or 1
        cpu = platform.processor() or platform.machine()
    return {
        "status": "ok", "version": app.version,
        "uptime": int(time.time() - STARTED_AT), "models": [],
        "device": {"cpu": cpu, "cores": cores,
                   "ram": {"total": total, "used": used, "free": max(0, total-used)},
                   "platform": platform.platform(), "python": platform.python_version(),
                   "uptime": int(time.time() - STARTED_AT)},
    }


@app.get("/api/models")
def models() -> list[dict]:
    try:
        from qwen_oda import is_model_downloaded, is_model_loaded
        downloaded = is_model_downloaded()
        loaded = is_model_loaded()
    except Exception:
        downloaded = loaded = False
    return [
        {"id": "qwen-local", "name": "Qwen local model", "type": "local",
         "status": "loaded" if loaded else ("unloaded" if downloaded else "error"), "size": "GGUF"},
        {"id": "grok-cloud", "name": "Grok cloud", "type": "remote",
         "status": "loaded" if bool(os.getenv("GROK_API_KEY", "").strip()) else "unloaded"},
    ]


@app.post("/api/models/{model_id}/load")
def load_model(model_id: str) -> dict:
    if model_id != "qwen-local":
        raise HTTPException(status_code=400, detail="Only the local Qwen model can be loaded here")
    from qwen_oda import is_model_downloaded, run_qwen
    if not is_model_downloaded():
        raise HTTPException(status_code=409, detail="Download the Qwen GGUF model before loading it")
    result = run_qwen("Reply with ready.", max_new_tokens=1, temperature=0)
    if result.startswith("Qwen inference error:"):
        raise HTTPException(status_code=503, detail=result)
    return {"status": "loaded", "model": model_id}


@app.post("/api/models/{model_id}/unload")
def unload_model(model_id: str) -> dict:
    if model_id != "qwen-local":
        raise HTTPException(status_code=400, detail="Only the local Qwen model can be unloaded here")
    from qwen_oda import reload_model
    reload_model()
    return {"status": "unloaded", "model": model_id}


@app.get("/api/memory")
def memory() -> list:
    return []


@app.get("/api/settings")
def settings() -> dict:
    return {"cloud_redaction": True, "cloud_key_configured": bool(os.getenv("GROK_API_KEY", "").strip())}
