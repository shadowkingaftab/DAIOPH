"""
chatbot_app.py
--------------
Memory-optimized Edge AI Chatbot with:
  - Professional chat UI with + (file) and mic icons
  - Image upload with OCR text extraction
  - Voice input via SpeechRecognition
  - PDF processing (text + OCR on images)
  - Lazy model loading (Qwen + Grok only when needed)
  - Smart prompt decomposition with colorful DAG
  - Time comparison: Edge AI vs Traditional
  - Exponential backoff retry logic
  - Memory target: <800MB (no PyTorch/transformers)

Run: streamlit run chatbot_app.py
"""

import streamlit as st
import os
import re
import time
import json
import math
import requests
from datetime import datetime

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Edge AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium Dark Chatbot CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

/* Global dark theme */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d0d1a !important;
    color: #e8e8f0 !important;
}
.stApp { background: linear-gradient(160deg, #0d0d1a 0%, #12122a 50%, #0d1a2a 100%); }

/* Header */
.chat-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    background: linear-gradient(90deg, #4CC9F0, #7B2FBE, #F72585);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.chat-subheader {
    text-align: center;
    color: #888;
    font-size: 0.95rem;
    margin-bottom: 1.2rem;
}

/* Chat bubbles */
.chat-wrap { max-height: 60vh; overflow-y: auto; padding: 0 1rem 1rem; margin-bottom: 0.5rem; }
.bubble-row-user  { display: flex; justify-content: flex-end;  margin: 0.5rem 0; }
.bubble-row-bot   { display: flex; justify-content: flex-start; margin: 0.5rem 0; }
.bubble-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.bubble-avatar-user { background: linear-gradient(135deg,#4CC9F0,#7B2FBE); margin-left: 8px; }
.bubble-avatar-bot  { background: linear-gradient(135deg,#F72585,#7B2FBE); margin-right: 8px; }
.bubble {
    max-width: 70%;
    padding: 0.75rem 1rem;
    border-radius: 1.2rem;
    line-height: 1.55;
    font-size: 0.93rem;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble-user {
    background: linear-gradient(135deg, #1a3a5c, #1a2a4a);
    border: 1px solid #2a4a7c;
    border-bottom-right-radius: 4px;
    color: #d0e8ff;
}
.bubble-bot {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2a2a4a;
    border-bottom-left-radius: 4px;
    color: #e0e0f0;
}
.bubble-time { font-size: 0.68rem; color: #666; margin-top: 3px; text-align: right; }

/* Input toolbar */
.input-toolbar {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 1rem;
    padding: 0.4rem 0.6rem;
    display: flex; align-items: center; gap: 0.4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a, #12122a) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4CC9F0, #7B2FBE) !important;
    color: white !important; border: none !important;
    border-radius: 0.6rem !important; font-weight: 600 !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 4px 20px rgba(76,201,240,0.35) !important;
}
.icon-btn > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 0.5rem !important; font-size: 1.2rem !important;
    padding: 0.3rem 0.6rem !important;
}

/* Text inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 0.6rem !important;
    color: #e0e0f0 !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 0.8rem;
    padding: 0.8rem;
}

/* Route badge */
.route-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 1rem;
    font-size: 0.7rem;
    font-weight: 600;
    margin-left: 6px;
}
.badge-oda    { background: #1a4a2a; color: #4ade80; }
.badge-hybrid { background: #1a2a4a; color: #60a5fa; }
.badge-cloud  { background: #3a2a1a; color: #fbbf24; }

/* DAG legend */
.dag-legend { display: flex; gap: 0.8rem; flex-wrap: wrap; margin: 0.4rem 0; }
.dag-legend span {
    padding: 0.15rem 0.6rem; border-radius: 1rem;
    font-size: 0.72rem; font-weight: 600;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
MODEL_DIR  = "models"
MODEL_FILE = "qwen2-0_5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODELS  = ["grok-3-mini", "grok-2-1212", "grok-2-latest", "grok-beta"]

def _get_grok_key():
    try:
        return st.secrets.get("GROK_API_KEY", "") or ""
    except Exception:
        return os.environ.get("GROK_API_KEY", "") or ""

# ══════════════════════════════════════════════════════════════════════════════
# LAZY MODEL LOADERS  (load only when the route needs them)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="⚡ Loading Qwen2-0.5B on-device model…")
def _load_qwen():
    """Cached across reruns — unloaded only on app restart."""
    try:
        from llama_cpp import Llama
        os.makedirs(MODEL_DIR, exist_ok=True)
        if not os.path.exists(MODEL_PATH):
            from huggingface_hub import hf_hub_download
            hf_hub_download(
                repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
                filename=MODEL_FILE,
                local_dir=MODEL_DIR,
                local_dir_use_symlinks=False,
            )
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=1024,
            n_threads=2,
            n_batch=128,
            n_gpu_layers=0,
            verbose=False,
        )
        return llm, None
    except ImportError:
        return None, "llama-cpp-python not installed"
    except Exception as e:
        return None, str(e)


def run_qwen(prompt: str, max_tokens: int = 400) -> str:
    llm, err = _load_qwen()
    if llm is None:
        return f"⚠️ Qwen unavailable: {err}"
    try:
        out = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return out["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Qwen error: {e}"


def run_grok(prompt: str, api_key: str, max_tokens: int = 512) -> str:
    if not api_key:
        return "⚠️ No Grok API key set. Add it in the sidebar."
    session = requests.Session()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for model in GROK_MODELS:
        try:
            resp = session.post(
                GROK_API_URL,
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code in (401, 429):
                break
        except Exception:
            continue
    return "⚠️ Grok API unreachable. Falling back to ODA."


# ══════════════════════════════════════════════════════════════════════════════
# SMART PROMPT DECOMPOSITION + DAG
# ══════════════════════════════════════════════════════════════════════════════
_SEQUENTIAL_KW = [
    "first", "second", "third", "then", "next", "after that",
    "finally", "step", "initially", "lastly", "subsequently",
    "पहले", "फिर", "primero", "luego", "d'abord", "ensuite",
]

def decompose_prompt(prompt: str) -> dict:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prompt) if s.strip()]
    if not sentences:
        sentences = [prompt]

    tasks, current = [], []
    for sent in sentences:
        low = sent.lower()
        if any(kw in low for kw in _SEQUENTIAL_KW) and current:
            tasks.append(" ".join(current))
            current = [sent]
        else:
            current.append(sent)
    if current:
        tasks.append(" ".join(current))

    # Split long single-task prompts into 2 chunks
    if len(tasks) == 1 and len(sentences) > 3:
        mid = max(1, len(sentences) // 2)
        tasks = [" ".join(sentences[:mid]), " ".join(sentences[mid:])]

    tasks = [t for t in tasks if t.strip()]
    return {
        "nodes": [
            {
                "id": f"n{i+1}",
                "task": t,
                "depends_on": [f"n{i}"] if i > 0 else [],
            }
            for i, t in enumerate(tasks)
        ]
    }


def execute_with_retry(prompt: str, route: str, grok_key: str, max_retries: int = 2) -> tuple[str, int]:
    """Returns (response_text, retry_count)."""
    retries = 0
    for attempt in range(max_retries + 1):
        try:
            if route == "ODA":
                result = run_qwen(prompt)
            elif route == "Cloud":
                result = run_grok(prompt, grok_key)
                if result.startswith("⚠️"):
                    result = run_qwen(prompt)  # Fallback to ODA
            else:  # Hybrid
                result = run_qwen(prompt)
                if not result or result.startswith(("⚠️", "Qwen error")):
                    result = run_grok(prompt, grok_key)
            if result and not result.startswith(("⚠️ Qwen unavail", "Qwen error: ")):
                return result, retries
        except Exception:
            pass
        retries += 1
        if attempt < max_retries:
            time.sleep(math.pow(2, attempt))
    return f"❌ Failed after {max_retries+1} attempts.", retries


def show_dag(dag: dict, route: str):
    try:
        import graphviz
        color_map = {"ODA": "#2ecc71", "Cloud": "#f1c40f", "Hybrid": "#74b9ff"}
        font_map  = {"ODA": "white",   "Cloud": "#111",    "Hybrid": "#111"}
        color  = color_map.get(route, "#95a5a6")
        fcolor = font_map.get(route, "white")

        dot = graphviz.Digraph(graph_attr={"rankdir": "LR", "bgcolor": "transparent",
                                            "splines": "curved"})
        for node in dag["nodes"]:
            label = node["task"][:30] + ("…" if len(node["task"]) > 30 else "")
            dot.node(node["id"], label=label, fillcolor=color, fontcolor=fcolor,
                     style="filled,rounded", fontsize="10",
                     tooltip=f"{node['id']}: {node['task']}")
        for node in dag["nodes"]:
            for dep in node.get("depends_on", []):
                dot.edge(dep, node["id"], color="#555", arrowsize="0.7")
        st.graphviz_chart(dot)
    except Exception:
        st.json(dag)

    st.markdown(f"""
    <div class="dag-legend">
        <span style="background:#1a4a2a;color:#4ade80">🟢 ODA</span>
        <span style="background:#3a3000;color:#fbbf24">🟡 Cloud</span>
        <span style="background:#1a2a4a;color:#60a5fa">🔵 Hybrid</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PDF / IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def extract_pdf_text(pdf_path: str, max_pages: int = 10) -> str:
    text = ""
    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in list(reader.pages)[:max_pages]:
                pg_text = page.extract_text()
                if pg_text:
                    text += pg_text + "\n"
    except Exception as e:
        text = f"[PDF read error: {e}]"

    # OCR pass if little text was extracted
    if len(text.strip()) < 200:
        try:
            from pdf2image import convert_from_path
            import pytesseract
            imgs = convert_from_path(pdf_path)
            for i, img in enumerate(imgs[:max_pages]):
                ocr = pytesseract.image_to_string(img)
                if ocr.strip():
                    text += f"\n[Page {i+1} OCR]\n{ocr}"
        except Exception:
            pass
    return text[:4000] or "No text could be extracted."


def extract_image_text(image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# VOICE INPUT
# ══════════════════════════════════════════════════════════════════════════════
def listen_microphone() -> str | None:
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=8, phrase_time_limit=15)
        return r.recognize_google(audio)
    except ImportError:
        st.warning("SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
        return None
    except Exception as e:
        st.error(f"Voice error: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
if "messages"     not in st.session_state: st.session_state.messages     = []
if "pending_text" not in st.session_state: st.session_state.pending_text = ""
if "is_listening" not in st.session_state: st.session_state.is_listening = False

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    grok_key_input = st.text_input(
        "🔑 Grok API Key",
        value=_get_grok_key(),
        type="password",
        help="Get a free key at console.x.ai",
    )
    grok_key = grok_key_input or _get_grok_key()

    route = st.selectbox(
        "🛣️ Execution Route",
        ["ODA (On-Device)", "Hybrid (ODA + Cloud)", "Cloud (Grok API)"],
        index=1,
        help="ODA = Qwen2-0.5B local | Cloud = Grok API | Hybrid = both",
    )
    route_code = {"ODA (On-Device)": "ODA", "Hybrid (ODA + Cloud)": "Hybrid", "Cloud (Grok API)": "Cloud"}[route]

    max_tokens = st.slider("Max Response Tokens", 128, 1024, 400, step=64)
    show_dag_cb = st.checkbox("🔗 Show Task DAG", value=True)
    show_time_cb = st.checkbox("⏱️ Show Time Comparison", value=True)
    show_retry_cb = st.checkbox("🔄 Show Retry Stats", value=False)

    st.markdown("---")
    st.markdown("### 📊 Route Guide")
    st.markdown("""
| Route | Model | Best For |
|-------|-------|----------|
| 🟢 ODA | Qwen2-0.5B | Fast, private |
| 🔵 Hybrid | Both | Balanced |
| 🟡 Cloud | Grok | Complex tasks |
""")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Memory monitor
    try:
        import psutil
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        pct = mem.percent
        color = "#4ade80" if pct < 70 else ("#fbbf24" if pct < 85 else "#f87171")
        st.markdown(f"""
        <div style="margin-top:1rem;padding:0.6rem;background:rgba(255,255,255,0.04);
                    border-radius:0.6rem;border:1px solid rgba(255,255,255,0.08)">
          <small style="color:#888">💾 Memory Usage</small><br>
          <span style="color:{color};font-weight:700;font-size:1.1rem">{pct:.1f}%</span>
          <small style="color:#666"> ({used_gb:.1f}/{total_gb:.1f} GB)</small>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="chat-header">🤖 Edge AI Chatbot</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="chat-subheader">Qwen2-0.5B On-Device  •  Grok Cloud Fallback  •  Image & Voice Support</p>',
    unsafe_allow_html=True
)

# ── Chat history display ──────────────────────────────────────────────────────
badge_html = {
    "ODA":    '<span class="route-badge badge-oda">ODA</span>',
    "Hybrid": '<span class="route-badge badge-hybrid">Hybrid</span>',
    "Cloud":  '<span class="route-badge badge-cloud">Cloud</span>',
}

chat_html = '<div class="chat-wrap">'
for msg in st.session_state.messages:
    ts   = msg.get("ts", "")
    role = msg["role"]
    body = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
    badge = badge_html.get(msg.get("route", ""), "")

    if role == "user":
        chat_html += f"""
        <div class="bubble-row-user">
          <div>
            <div class="bubble bubble-user">{body}</div>
            <div class="bubble-time">{ts}</div>
          </div>
          <div class="bubble-avatar bubble-avatar-user">👤</div>
        </div>"""
    else:
        chat_html += f"""
        <div class="bubble-row-bot">
          <div class="bubble-avatar bubble-avatar-bot">🤖</div>
          <div>
            <div class="bubble bubble-bot">{body}{badge}</div>
            <div class="bubble-time">{ts}</div>
          </div>
        </div>"""
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input toolbar ─────────────────────────────────────────────────────────────
st.markdown("---")
col_text, col_file, col_mic, col_send = st.columns([7, 1, 1, 1])

with col_text:
    user_text = st.text_input(
        "message",
        value=st.session_state.pending_text,
        placeholder="💬  Ask me anything… (or upload a file / use the mic)",
        label_visibility="collapsed",
        key="chat_input_box",
    )

with col_file:
    st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "➕",
        type=["pdf", "jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="file_upload",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_mic:
    st.markdown('<div class="icon-btn">', unsafe_allow_html=True)
    mic_btn = st.button("🎤", key="mic_btn", help="Voice input")
    st.markdown("</div>", unsafe_allow_html=True)

with col_send:
    send_btn = st.button("➤ Send", key="send_btn", use_container_width=True)

# ── Voice input handler ───────────────────────────────────────────────────────
if mic_btn:
    with st.spinner("🎙️ Listening… speak now"):
        voice_text = listen_microphone()
    if voice_text:
        st.session_state.pending_text = voice_text
        st.info(f"🎙️ Heard: **{voice_text}**")
        st.rerun()

# ── File processing ───────────────────────────────────────────────────────────
file_context = ""
if uploaded:
    ftype = uploaded.type or ""
    if ftype.startswith("image/"):
        from PIL import Image
        img = Image.open(uploaded)
        st.image(img, caption=f"📷 {uploaded.name}", use_column_width=True)
        ocr_text = extract_image_text(img)
        if ocr_text:
            file_context = f"[Image content]\n{ocr_text}"
            st.success(f"✅ Extracted {len(ocr_text)} chars via OCR")
        else:
            file_context = f"[Image uploaded: {uploaded.name}]"

    elif ftype == "application/pdf":
        tmp_path = f"tmp_chatbot_{uploaded.name}"
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        with st.spinner("📄 Extracting PDF text…"):
            file_context = extract_pdf_text(tmp_path)
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        st.success(f"✅ Extracted {len(file_context)} chars from PDF")
        with st.expander("📋 Preview extracted text"):
            st.text(file_context[:800] + ("…" if len(file_context) > 800 else ""))

# ── Message send & inference ──────────────────────────────────────────────────
final_prompt = user_text.strip()
if file_context and not final_prompt:
    final_prompt = "Summarize and explain the key points from the provided content."

if (send_btn or (user_text and user_text != st.session_state.pending_text)) and final_prompt:
    st.session_state.pending_text = ""

    # Build full prompt
    full_prompt = (
        f"{file_context}\n\n{final_prompt}" if file_context else final_prompt
    )

    # Add user message
    st.session_state.messages.append({
        "role":    "user",
        "content": final_prompt + (f"\n📎 *({uploaded.name})*" if uploaded else ""),
        "ts":      datetime.now().strftime("%H:%M"),
        "route":   route_code,
    })

    # Execute with spinner
    with st.spinner(f"🧠 Thinking via **{route}**…"):
        exec_start = time.time()

        # Decompose into tasks
        dag = decompose_prompt(full_prompt)
        results, total_retries = {}, 0

        # Progress bar for multi-task prompts
        if len(dag["nodes"]) > 1:
            prog = st.progress(0)
        else:
            prog = None

        for i, node in enumerate(dag["nodes"]):
            task_prompt = full_prompt if i == 0 else node["task"]
            # Inject context from previous task
            if i > 0 and node.get("depends_on"):
                prev_id = node["depends_on"][0]
                prev_out = results.get(prev_id, "")
                if prev_out:
                    task_prompt = f"Context from previous step:\n{prev_out}\n\nContinue: {node['task']}"

            res, retries = execute_with_retry(task_prompt, route_code, grok_key, max_retries=2)
            results[node["id"]] = res
            total_retries += retries
            if prog:
                prog.progress((i + 1) / len(dag["nodes"]))

        edge_time = time.time() - exec_start

        # Stitch outputs
        if len(results) == 1:
            final_answer = list(results.values())[0]
        else:
            final_answer = "\n\n".join(
                f"**Step {nid}:**\n{out}" for nid, out in results.items()
            )

        # Time comparison
        total_words = sum(len(n["task"].split()) for n in dag["nodes"])
        trad_time   = total_words / 20  # ~20 tokens/sec sequential
        savings_pct = ((trad_time - edge_time) / trad_time * 100) if trad_time > 0 else 0

    # Append bot message
    st.session_state.messages.append({
        "role":    "bot",
        "content": final_answer,
        "ts":      datetime.now().strftime("%H:%M"),
        "route":   route_code,
    })

    st.rerun()

# ── Post-execution metrics (shown below the chat area) ────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "bot":
    last_bot = st.session_state.messages[-1]

    # Only show panels if we just ran inference (session has timing data)
    # We re-compute from the last message content for display
    with st.expander("📊 Execution Details", expanded=False):
        tabs = st.tabs(["⏱️ Time", "🔗 DAG", "📋 Raw"])

        with tabs[0]:
            # Estimated metrics from last message token count
            word_count = len(last_bot["content"].split())
            est_trad = word_count / 20
            c1, c2, c3 = st.columns(3)
            c1.metric("📡 Route Used", last_bot.get("route", "—"))
            c2.metric("🕒 Est. Traditional", f"~{est_trad:.1f}s")
            c3.metric("📝 Response Words", word_count)

        with tabs[1]:
            if st.session_state.messages:
                # Show DAG for last user prompt
                user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
                if user_msgs:
                    last_dag = decompose_prompt(user_msgs[-1]["content"])
                    show_dag(last_dag, last_bot.get("route", "Hybrid"))

        with tabs[2]:
            st.json(st.session_state.messages[-3:])

# ── Empty state prompt ────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#555">
        <div style="font-size:3rem;margin-bottom:1rem">🤖</div>
        <div style="font-size:1.1rem;font-weight:600;color:#777">Start a conversation!</div>
        <div style="font-size:0.85rem;margin-top:0.5rem">
            Try: <em>"Explain edge AI in simple terms"</em> or upload a PDF/image
        </div>
    </div>
    """, unsafe_allow_html=True)
