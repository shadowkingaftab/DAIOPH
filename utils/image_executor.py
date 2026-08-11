"""
utils/image_executor.py
-----------------------
Memory-safe image & diagram generation — ZERO local model weight.

Two modes:
  1. Graphviz diagrams  — offline, 0 MB, uses the graphviz binary already
                          bundled in your environment.
  2. Replicate API      — cloud-only, 0 MB local, requires REPLICATE_API_TOKEN
                          in Streamlit secrets or environment variables.

Graphviz is already in requirements.txt (used for DAG display), so this adds
NO new dependencies and NO extra memory.
"""

from __future__ import annotations
import os
import re
import time
import base64
import requests
from typing import Optional

# ── Graphviz (already in requirements) ───────────────────────────────────────
try:
    import graphviz as gv
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

# ── Keyword sets for task routing ─────────────────────────────────────────────
DIAGRAM_KEYWORDS = {
    "flowchart", "diagram", "workflow", "process flow", "steps",
    "sequence", "class diagram", "state diagram", "er diagram",
    "mind map", "tree structure", "dependency graph", "architecture",
    "visualize flow", "draw flow", "show flow", "->", "-->",
    "mermaid", "graphviz", "dot graph",
}

IMAGE_KEYWORDS = {
    "generate image", "create image", "draw a", "draw an",
    "realistic", "photorealistic", "photo of", "render",
    "illustration of", "picture of", "paint", "portrait",
    "high detail", "detailed image", "make an image", "make a picture",
    "generate a photo", "generate picture",
}

# ─────────────────────────────────────────────────────────────────────────────

def requires_diagram(text: str) -> bool:
    """Return True if the prompt is asking for a diagram/flowchart."""
    low = text.lower()
    return any(kw in low for kw in DIAGRAM_KEYWORDS)


def requires_image(text: str) -> bool:
    """Return True if the prompt is asking for a photorealistic image."""
    low = text.lower()
    return any(kw in low for kw in IMAGE_KEYWORDS)


# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM GENERATOR  (Graphviz — fully offline)
# ─────────────────────────────────────────────────────────────────────────────

def generate_diagram(prompt: str) -> "gv.Digraph | None":
    """
    Convert a natural-language prompt into a Graphviz Digraph.

    Supports three input styles:
      - Arrow syntax  : "A -> B -> C"
      - Dot language  : raw Graphviz dot code inside the prompt
      - Plain prose   : falls back to a single labelled node

    Returns a graphviz.Digraph object (renderable with st.graphviz_chart),
    or None if graphviz is not installed.
    """
    if not HAS_GRAPHVIZ:
        return None

    dot = gv.Digraph(
        graph_attr={
            "rankdir": "LR",
            "bgcolor": "transparent",
            "splines": "curved",
            "fontname": "Inter",
        },
        node_attr={"style": "filled,rounded", "fontname": "Inter", "fontsize": "11"},
        edge_attr={"color": "#888", "arrowsize": "0.7"},
    )

    # ── Style palette (cycles through colours) ──────────────────────────────
    PALETTE = ["#4CC9F0", "#7B2FBE", "#F72585", "#4CAF50", "#FF9800", "#00BCD4"]

    # ── 1. Raw dot/digraph code block ───────────────────────────────────────
    dot_match = re.search(r"(?:digraph|graph)\s+\w*\s*\{(.+?)\}", prompt,
                           re.IGNORECASE | re.DOTALL)
    if dot_match:
        try:
            return gv.Source(prompt.strip())  # trust user-provided dot code
        except Exception:
            pass  # fall through to other parsers

    # ── 2. Arrow syntax: "A -> B -> C" or "A --> B --> C" ───────────────────
    arrow_pat = re.compile(r"--?>")
    if arrow_pat.search(prompt):
        # Split on comma or newline to get multiple chains
        chains = re.split(r"[,\n]+", prompt)
        added_nodes: set[str] = set()

        for chain in chains:
            steps = [s.strip() for s in arrow_pat.split(chain) if s.strip()]
            # Remove trailing punctuation / numbers / keywords
            steps = [re.sub(r"^[\d\.\-\*]+\s*", "", s).strip(" \"'") for s in steps]
            steps = [s for s in steps if s and len(s) < 60]
            if not steps:
                continue
            for idx, step in enumerate(steps):
                if step not in added_nodes:
                    color = PALETTE[len(added_nodes) % len(PALETTE)]
                    dot.node(step, fillcolor=color, fontcolor="white")
                    added_nodes.add(step)
                if idx > 0:
                    dot.edge(steps[idx - 1], step)
        if added_nodes:
            return dot

    # ── 3. Numbered/bulleted list → linear chain ─────────────────────────────
    lines = [re.sub(r"^[\d\.\-\*]+\s*", "", ln).strip()
             for ln in prompt.split("\n") if ln.strip()]
    lines = [ln for ln in lines if ln and len(ln) < 80]
    if len(lines) >= 2:
        for idx, ln in enumerate(lines):
            color = PALETTE[idx % len(PALETTE)]
            dot.node(ln, fillcolor=color, fontcolor="white")
            if idx > 0:
                dot.edge(lines[idx - 1], ln)
        return dot

    # ── 4. Fallback: single box with truncated prompt ────────────────────────
    label = prompt[:50] + ("…" if len(prompt) > 50 else "")
    dot.node("Task", label=label, fillcolor=PALETTE[0], fontcolor="white")
    return dot


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE GENERATOR  (Replicate API — cloud only, 0 MB local)
# ─────────────────────────────────────────────────────────────────────────────

REPLICATE_MODELS = [
    # Ordered by availability/speed; first working model wins
    "stability-ai/sdxl:7762fd07",
    "stability-ai/stable-diffusion:db21e45d",
]

REPLICATE_PREDICT_URL = "https://api.replicate.com/v1/predictions"


def _get_replicate_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("REPLICATE_API_TOKEN", "") or ""
    except Exception:
        return os.environ.get("REPLICATE_API_TOKEN", "") or ""


def generate_image_via_api(
    prompt: str,
    width: int = 512,
    height: int = 512,
    max_wait: int = 60,
) -> Optional[bytes]:
    """
    Call the Replicate API to generate a photorealistic image.

    Returns raw PNG bytes on success, or None on failure.
    Uses zero local memory — the model runs in Replicate's cloud.
    """
    api_key = _get_replicate_key()
    if not api_key:
        return None

    session = requests.Session()
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    # Try each model in order until one succeeds
    for model_version in REPLICATE_MODELS:
        try:
            # Start prediction
            resp = session.post(
                REPLICATE_PREDICT_URL,
                headers=headers,
                json={
                    "version": model_version.split(":")[1] if ":" in model_version else model_version,
                    "input": {
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5,
                    },
                },
                timeout=15,
            )
            if resp.status_code not in (200, 201):
                continue

            prediction = resp.json()
            poll_url = prediction.get("urls", {}).get("get", "")
            if not poll_url:
                continue

            # Poll until complete (max_wait seconds)
            deadline = time.time() + max_wait
            while time.time() < deadline:
                time.sleep(3)
                poll = session.get(poll_url, headers=headers, timeout=10)
                if poll.status_code != 200:
                    break
                data = poll.json()
                status = data.get("status", "")
                if status == "succeeded":
                    output_urls = data.get("output", [])
                    if output_urls:
                        img_resp = session.get(output_urls[0], timeout=20)
                        if img_resp.status_code == 200:
                            return img_resp.content
                    break
                elif status in ("failed", "canceled"):
                    break

        except Exception as e:
            print(f"[image_executor] Replicate model {model_version} failed: {e}")
            continue

    return None


def image_bytes_to_base64(img_bytes: bytes) -> str:
    """Convert raw image bytes to a base64 data URI for Markdown display."""
    return base64.b64encode(img_bytes).decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# HIGH-LEVEL INTERFACE (used by the orchestrator)
# ─────────────────────────────────────────────────────────────────────────────

class ImageExecutor:
    """
    Unified image/diagram executor — zero local model memory.

    Returns a dict with:
      type  : "diagram" | "image" | "error"
      data  : graphviz.Digraph | base64_str | error_message
    """

    def execute(self, prompt: str, route: str = "Hybrid") -> dict:
        if requires_diagram(prompt):
            return self._exec_diagram(prompt)
        elif requires_image(prompt):
            return self._exec_image(prompt, route)
        return {"type": "error", "data": "Not an image/diagram task."}

    def _exec_diagram(self, prompt: str) -> dict:
        if not HAS_GRAPHVIZ:
            return {"type": "error",
                    "data": "⚠️ graphviz not installed. Run: pip install graphviz"}
        dot = generate_diagram(prompt)
        if dot:
            return {"type": "diagram", "data": dot}
        return {"type": "error", "data": "⚠️ Could not parse diagram from prompt."}

    def _exec_image(self, prompt: str, route: str) -> dict:
        if route not in ("Cloud", "Hybrid"):
            return {
                "type": "error",
                "data": (
                    "⚠️ Photorealistic image generation requires **Hybrid** or **Cloud** route.\n"
                    "Switch the route in the sidebar and try again."
                ),
            }
        if not _get_replicate_key():
            return {
                "type": "error",
                "data": (
                    "⚠️ No **REPLICATE_API_TOKEN** found.\n"
                    "Add it in Streamlit Cloud → Settings → Secrets, or in your `.env` file.\n"
                    "Get a free token at https://replicate.com"
                ),
            }
        img_bytes = generate_image_via_api(prompt)
        if img_bytes:
            b64 = image_bytes_to_base64(img_bytes)
            return {"type": "image", "data": b64}
        return {
            "type": "error",
            "data": "⚠️ Replicate API did not return an image. Check your token and try again.",
        }
