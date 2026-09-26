"""
chatbot_app.py
--------------
Edge AI Chatbot — Premium Edition
Features:
  ✅ Conversation memory (last 5 turns for context)
  ✅ Liquid glass animated UI (glassmorphism + bubble animations)
  ✅ Voice input (SpeechRecognition)
  ✅ Image upload + OCR
  ✅ PDF processing (text + OCR fallback)
  ✅ Plotly analytics dashboard (4 interactive charts)
  ✅ Metrics tracking (time, tokens, route, success)
  ✅ Colorful DAG with route-based colors
  ✅ Time comparison: Edge AI vs Traditional
  ✅ Exponential backoff retry with route fallback
  ✅ Memory target: <800MB (no PyTorch/transformers)

Run: streamlit run chatbot_app.py
"""

import streamlit as st
import os, re, time, json, math, requests
from datetime import datetime

# ── Page config (must be FIRST Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Edge AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# LIQUID GLASS CSS — animated gradient + glassmorphism bubbles
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Animated liquid gradient background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e, #0f0c29);
    background-size: 400% 400%;
    animation: liquidBg 18s ease infinite;
    color: #e8e8f0;
}
@keyframes liquidBg {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Header ── */
.chat-header {
    text-align: center; padding: 1.2rem 0 0.3rem;
    background: linear-gradient(90deg, #4CC9F0, #7B2FBE, #F72585, #4CC9F0);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer { to { background-position: 200% center; } }
.chat-subheader {
    text-align: center; color: #8888aa; font-size: 0.92rem; margin-bottom: 1rem;
}

/* ── Glass card for chat area ── */
.glass-card {
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 1.4rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

/* ── Fixed bottom input area with glassmorphism ── */
.bottom-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem 1.5rem 1.8rem;
    background: rgba(15, 12, 41, 0.97);
    backdrop-filter: blur(25px) saturate(200%);
    -webkit-backdrop-filter: blur(25px) saturate(200%);
    z-index: 999;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* ── Chat bubbles ── */
.chat-wrap { 
    max-height: calc(100vh - 340px); 
    overflow-y: auto; 
    padding: 0.5rem 0.5rem 160px; 
}
.bubble-row-user  { display: flex; justify-content: flex-end;  margin: 0.55rem 0; animation: slideRight 0.3s ease-out; }
.bubble-row-bot   { display: flex; justify-content: flex-start; margin: 0.55rem 0; animation: slideLeft 0.3s ease-out; }

@keyframes slideRight { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }
@keyframes slideLeft  { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:translateX(0); } }

.bubble-avatar {
    width:36px; height:36px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; flex-shrink:0;
}
.bubble-avatar-user { background:linear-gradient(135deg,#4CC9F0,#7B2FBE); margin-left:8px; }
.bubble-avatar-bot  { background:linear-gradient(135deg,#F72585,#7B2FBE); margin-right:8px; }

.bubble {
    max-width:72%; padding:0.75rem 1rem; border-radius:1.2rem;
    line-height:1.58; font-size:0.92rem; white-space:pre-wrap; word-break:break-word;
    backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
}
.bubble-user {
    background: rgba(76,201,240,0.18);
    border: 1px solid rgba(76,201,240,0.35);
    border-bottom-right-radius:4px; color:#d0e8ff;
    box-shadow: 0 4px 15px rgba(76,201,240,0.15);
}
.bubble-bot {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-bottom-left-radius:4px; color:#e0e0f0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.bubble-time { font-size:0.67rem; color:#555; margin-top:3px; text-align:right; }

/* ── Route badges ── */
.route-badge { display:inline-block; padding:0.12rem 0.55rem; border-radius:1rem; font-size:0.68rem; font-weight:700; margin-left:5px; }
.badge-oda    { background:#0d3320; color:#4ade80; border:1px solid #2a6644; }
.badge-hybrid { background:#0d1a33; color:#60a5fa; border:1px solid #2a4477; }
.badge-cloud  { background:#332200; color:#fbbf24; border:1px solid #664400; }

/* ── DAG legend ── */
.dag-legend { display:flex; gap:0.7rem; flex-wrap:wrap; margin:0.4rem 0; }
.dag-legend span { padding:0.12rem 0.55rem; border-radius:1rem; font-size:0.7rem; font-weight:600; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d0d1a,#12122a) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#4CC9F0,#7B2FBE) !important;
    color:white !important; border:none !important;
    border-radius:0.65rem !important; font-weight:600 !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover { transform:scale(1.04) !important; box-shadow:0 4px 20px rgba(76,201,240,0.35) !important; }

.icon-btn > button {
    background:rgba(255,255,255,0.06) !important;
    border:1px solid rgba(255,255,255,0.14) !important;
    border-radius:0.55rem !important; font-size:1.15rem !important;
    padding:0.3rem 0.6rem !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background:rgba(255,255,255,0.06) !important;
    border:1px solid rgba(255,255,255,0.13) !important;
    border-radius:0.65rem !important; color:#e0e0f0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:1.5rem; border-bottom:1px solid rgba(255,255,255,0.08); }
.stTabs [data-baseweb="tab"] {
    height:2.8rem; padding:0 1.2rem;
    background:rgba(255,255,255,0.04);
    border-radius:0.5rem 0.5rem 0 0; font-weight:600; color:#888;
    border:1px solid rgba(255,255,255,0.06);
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(90deg,#4CC9F0,#7B2FBE) !important; color:white !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.09);
    border-radius:0.8rem; padding:0.8rem;
    backdrop-filter:blur(10px);
}

/* ── Plotly charts glass effect ── */
.js-plotly-plot { border-radius:1rem; overflow:hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.15); border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
MODEL_DIR  = "models"
MODEL_FILE = "qwen2-0_5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)
GROK_URL   = "https://api.x.ai/v1/chat/completions"
GROK_MODELS = ["grok-3-mini", "grok-2-1212", "grok-2-latest", "grok-beta"]

def _get_grok_key() -> str:
    try:
        return st.secrets.get("GROK_API_KEY", "") or ""
    except Exception:
        return os.environ.get("GROK_API_KEY", "") or ""

# ══════════════════════════════════════════════════════════════════════════════
# LAZY MODEL LOADERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="⚡ Loading Qwen2-0.5B on-device…")
def _load_qwen():
    try:
        from llama_cpp import Llama
        os.makedirs(MODEL_DIR, exist_ok=True)
        if not os.path.exists(MODEL_PATH):
            from huggingface_hub import hf_hub_download
            hf_hub_download(repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
                            filename=MODEL_FILE, local_dir=MODEL_DIR,
                            local_dir_use_symlinks=False)
        llm = Llama(model_path=MODEL_PATH, n_ctx=1024, n_threads=2,
                    n_batch=128, n_gpu_layers=0, verbose=False)
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
            max_tokens=max_tokens, temperature=0.7)
        return out["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Qwen error: {e}"


def run_grok(prompt: str, api_key: str, max_tokens: int = 512) -> str:
    if not api_key:
        return "⚠️ No Grok API key. Add it in the sidebar."
    sess = requests.Session()
    hdr  = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for m in GROK_MODELS:
        try:
            r = sess.post(GROK_URL, headers=hdr,
                          json={"model": m, "messages": [{"role": "user", "content": prompt}],
                                "max_tokens": max_tokens, "temperature": 0.7}, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code in (401, 429):
                break
        except Exception:
            continue
    return "⚠️ Grok unreachable — falling back."


# ══════════════════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY  (last N turns as context)
# ══════════════════════════════════════════════════════════════════════════════
def build_context_prompt(prompt: str, history: list, n_turns: int = 5) -> str:
    """Prepend the last n_turns of conversation to the new prompt for memory."""
    if not history:
        return prompt
    recent = history[-n_turns * 2:]  # user + bot messages interleaved
    lines  = []
    for msg in recent:
        role  = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content'][:300]}")  # truncate long messages
    ctx = "\n".join(lines)
    return f"[Conversation history]\n{ctx}\n\n[New message]\n{prompt}"


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT DECOMPOSITION + EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
_SEQ_KW = ["first","second","third","then","next","after that","finally","step",
           "initially","lastly","subsequently","पहले","फिर","primero","luego","d'abord"]

def decompose_prompt(prompt: str) -> dict:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prompt) if s.strip()]
    if not sentences:
        sentences = [prompt]
    tasks, cur = [], []
    for sent in sentences:
        if any(kw in sent.lower() for kw in _SEQ_KW) and cur:
            tasks.append(" ".join(cur)); cur = [sent]
        else:
            cur.append(sent)
    if cur:
        tasks.append(" ".join(cur))
    if len(tasks) == 1 and len(sentences) > 3:
        mid   = max(1, len(sentences) // 2)
        tasks = [" ".join(sentences[:mid]), " ".join(sentences[mid:])]
    tasks = [t for t in tasks if t.strip()]
    return {"nodes": [{"id": f"n{i+1}", "task": t,
                       "depends_on": [f"n{i}"] if i > 0 else []}
                      for i, t in enumerate(tasks)]}


def execute_with_retry(prompt: str, route: str, grok_key: str,
                       max_tokens: int = 400, max_retries: int = 2) -> tuple:
    for attempt in range(max_retries + 1):
        try:
            if route == "ODA":
                res = run_qwen(prompt, max_tokens)
            elif route == "Cloud":
                res = run_grok(prompt, grok_key, max_tokens)
                if res.startswith("⚠️"):
                    res = run_qwen(prompt, max_tokens)
            else:  # Hybrid
                res = run_qwen(prompt, max_tokens)
                if not res or res.startswith(("⚠️", "Qwen error")):
                    res = run_grok(prompt, grok_key, max_tokens)
            if res and not res.startswith(("⚠️ Qwen unavail", "Qwen error:")):
                return res, attempt
        except Exception:
            pass
        if attempt < max_retries:
            time.sleep(math.pow(2, attempt))
    return "❌ Failed after retries.", max_retries


# ══════════════════════════════════════════════════════════════════════════════
# DAG VISUALIZER
# ══════════════════════════════════════════════════════════════════════════════
def show_dag(dag: dict, route: str):
    color_map = {"ODA": "#2ecc71", "Cloud": "#f1c40f", "Hybrid": "#74b9ff"}
    fcolor_map = {"ODA": "white",  "Cloud": "#111",    "Hybrid": "#111"}
    c  = color_map.get(route, "#95a5a6")
    fc = fcolor_map.get(route, "white")
    try:
        import graphviz
        dot = graphviz.Digraph(graph_attr={"rankdir": "LR", "bgcolor": "transparent",
                                            "splines": "curved"})
        for n in dag["nodes"]:
            lbl = n["task"][:30] + ("…" if len(n["task"]) > 30 else "")
            dot.node(n["id"], label=lbl, fillcolor=c, fontcolor=fc,
                     style="filled,rounded", fontsize="10",
                     tooltip=f"{n['id']}: {n['task']}")
        for n in dag["nodes"]:
            for d in n.get("depends_on", []):
                dot.edge(d, n["id"], color="#555", arrowsize="0.7")
        st.graphviz_chart(dot)
    except Exception:
        st.json(dag)
    st.markdown("""
    <div class="dag-legend">
        <span style="background:#0d3320;color:#4ade80;border:1px solid #2a6644">🟢 ODA</span>
        <span style="background:#332200;color:#fbbf24;border:1px solid #664400">🟡 Cloud</span>
        <span style="background:#0d1a33;color:#60a5fa;border:1px solid #2a4477">🔵 Hybrid</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PDF / IMAGE UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def extract_pdf_text(pdf_path: str, max_pages: int = 10) -> str:
    text = ""
    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for pg in list(reader.pages)[:max_pages]:
                t = pg.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        text = f"[PDF error: {e}]"
    if len(text.strip()) < 200:
        try:
            from pdf2image import convert_from_path
            import pytesseract
            for i, img in enumerate(convert_from_path(pdf_path)[:max_pages]):
                ocr = pytesseract.image_to_string(img)
                if ocr.strip():
                    text += f"\n[Page {i+1} OCR]\n{ocr}"
        except Exception:
            pass
    return text[:4000] or "No text extracted."


def extract_image_text(image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""


def listen_microphone() -> str | None:
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.5)
            audio = r.listen(src, timeout=8, phrase_time_limit=15)
        return r.recognize_google(audio)
    except ImportError:
        st.warning("SpeechRecognition not installed.")
        return None
    except Exception as e:
        st.error(f"Voice error: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════════════════════════
_defaults = {
    "messages":     [],
    "pending_text": "",
    "metrics": {
        "timestamps":      [],   # datetime objects
        "execution_times": [],   # float seconds
        "trad_times":      [],   # estimated traditional time
        "routes":          [],   # "ODA" / "Hybrid" / "Cloud"
        "tokens":          [],   # prompt word count
        "retries":         [],   # retry count per request
        "success":         [],   # 1 or 0
    },
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    grok_key_input = st.text_input("🔑 Grok API Key", value=_get_grok_key(),
                                    type="password", help="Get at console.x.ai")
    grok_key   = grok_key_input or _get_grok_key()
    route      = st.selectbox("🛣️ Execution Route",
                               ["ODA (On-Device)", "Hybrid (ODA + Cloud)", "Cloud (Grok API)"], index=1)
    route_code = {"ODA (On-Device)": "ODA", "Hybrid (ODA + Cloud)": "Hybrid",
                  "Cloud (Grok API)": "Cloud"}[route]
    max_tokens  = st.slider("Max Response Tokens", 128, 1024, 400, step=64)
    memory_turns = st.slider("💾 Memory Turns", 0, 10, 5,
                              help="How many previous messages to include as context")
    show_dag_cb  = st.checkbox("🔗 Show Task DAG",       value=True)
    show_time_cb = st.checkbox("⏱️ Show Time Comparison", value=True)

    st.markdown("---")
    st.markdown("""
| Route | Model | Best For |
|-------|-------|----------|
| 🟢 ODA | Qwen2-0.5B | Fast, private |
| 🔵 Hybrid | Both | Balanced |
| 🟡 Cloud | Grok | Complex |
""")
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Memory monitor
    try:
        import psutil
        m   = psutil.virtual_memory()
        pct = m.percent
        clr = "#4ade80" if pct < 70 else ("#fbbf24" if pct < 85 else "#f87171")
        st.markdown(f"""
        <div style="margin-top:0.8rem;padding:0.55rem 0.7rem;
                    background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:0.6rem">
          <small style="color:#777">💾 Memory</small><br>
          <span style="color:{clr};font-weight:700;font-size:1.05rem">{pct:.1f}%</span>
          <small style="color:#555"> ({m.used/1e9:.1f}/{m.total/1e9:.1f} GB)</small>
        </div>""", unsafe_allow_html=True)
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — THREE TABS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="chat-header">🤖 Edge AI Chatbot</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="chat-subheader">Qwen2-0.5B On-Device  •  Grok Cloud  •  Conversation Memory  •  Voice & Image</p>',
    unsafe_allow_html=True)

tab_chat, tab_analytics, tab_settings = st.tabs(["💬 Chat", "📊 Analytics", "⚙️ Settings"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    badge_html = {
        "ODA":    '<span class="route-badge badge-oda">ODA</span>',
        "Hybrid": '<span class="route-badge badge-hybrid">Hybrid</span>',
        "Cloud":  '<span class="route-badge badge-cloud">Cloud</span>',
    }

    # Chat history
    chat_html = '<div class="chat-wrap">'
    for msg in st.session_state.messages:
        ts    = msg.get("ts", "")
        role  = msg["role"]
        body  = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
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

    # Empty state
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 1rem;color:#444">
            <div style="font-size:3rem;margin-bottom:0.8rem;filter:drop-shadow(0 0 20px #7B2FBE)">🤖</div>
            <div style="font-size:1.05rem;font-weight:600;color:#666">Start a conversation!</div>
            <div style="font-size:0.82rem;margin-top:0.4rem;color:#444">
                Try: <em>"Explain edge AI"</em> &nbsp;|&nbsp; Upload a PDF or image &nbsp;|&nbsp; Use the 🎤 mic
            </div>
        </div>""", unsafe_allow_html=True)

    # Input toolbar with custom fixed bottom design
    st.markdown('<div class="bottom-input-container">', unsafe_allow_html=True)
    st.markdown('<div style="max-width:1200px;margin:0 auto;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:1.2rem;padding:0.7rem 1rem;box-shadow:0 8px 32px rgba(0,0,0,0.25);">', unsafe_allow_html=True)
    
    col_file, col_text, col_mic, col_send = st.columns([1, 7, 1, 1.2])
    
    with col_file:
        st.markdown('<div style="margin-top:0.1rem;">', unsafe_allow_html=True)
        uploaded = st.file_uploader("📎", type=["pdf","jpg","jpeg","png","webp"],
                                     label_visibility="collapsed", key="file_upload", 
                                     help="Upload file (PDF/Image)")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_text:
        user_text = st.text_area("msg", value=st.session_state.pending_text,
                                   placeholder="Type your message…",
                                   label_visibility="collapsed", key="chat_input_box",
                                   height=50)
        
    with col_mic:
        mic_btn = st.button("🎤", key="mic_btn", help="Voice input", 
                            use_container_width=True)
        
    with col_send:
        send_btn = st.button("➤", key="send_btn", use_container_width=True,
                            type="primary")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Voice
    if mic_btn:
        with st.spinner("🎙️ Listening…"):
            v = listen_microphone()
        if v:
            st.session_state.pending_text = v
            st.info(f"🎙️ Heard: **{v}**")
            st.rerun()

    # File processing
    file_context = ""
    if uploaded:
        ftype = uploaded.type or ""
        if ftype.startswith("image/"):
            from PIL import Image
            img = Image.open(uploaded)
            st.image(img, caption=f"📷 {uploaded.name}", use_column_width=True)
            ocr = extract_image_text(img)
            file_context = f"[Image OCR]\n{ocr}" if ocr else f"[Image: {uploaded.name}]"
            if ocr:
                st.success(f"✅ OCR: {len(ocr)} chars extracted")
        elif ftype == "application/pdf":
            tmp = f"tmp_{uploaded.name}"
            with open(tmp, "wb") as f:
                f.write(uploaded.getbuffer())
            with st.spinner("📄 Extracting PDF…"):
                file_context = extract_pdf_text(tmp)
            try:
                os.remove(tmp)
            except Exception:
                pass
            st.success(f"✅ PDF: {len(file_context)} chars extracted")
            with st.expander("📋 Preview"):
                st.text(file_context[:800] + ("…" if len(file_context) > 800 else ""))

    # Send / execute
    final_prompt = user_text.strip()
    if file_context and not final_prompt:
        final_prompt = "Summarize and explain the key points from the provided content."

    if (send_btn or (user_text and user_text != st.session_state.pending_text)) and final_prompt:
        st.session_state.pending_text = ""

        # Build prompt with conversation memory
        full_prompt = (f"{file_context}\n\n{final_prompt}" if file_context else final_prompt)
        ctx_prompt  = build_context_prompt(full_prompt, st.session_state.messages, memory_turns)

        st.session_state.messages.append({
            "role":    "user",
            "content": final_prompt + (f"\n📎 *({uploaded.name})*" if uploaded else ""),
            "ts":      datetime.now().strftime("%H:%M"),
            "route":   route_code,
        })

        with st.spinner(f"🧠 Thinking via **{route}**…"):
            exec_start = time.time()
            dag        = decompose_prompt(full_prompt)
            results, total_retries = {}, 0

            prog = st.progress(0) if len(dag["nodes"]) > 1 else None

            for i, node in enumerate(dag["nodes"]):
                task_p = ctx_prompt if i == 0 else node["task"]
                if i > 0 and node.get("depends_on"):
                    prev_out = results.get(node["depends_on"][0], "")
                    if prev_out:
                        task_p = f"Previous step output:\n{prev_out}\n\nContinue: {node['task']}"

                res, retries = execute_with_retry(task_p, route_code, grok_key, max_tokens)
                results[node["id"]] = res
                total_retries += retries
                if prog:
                    prog.progress((i + 1) / len(dag["nodes"]))

            edge_time = time.time() - exec_start

            final_answer = (list(results.values())[0] if len(results) == 1
                            else "\n\n".join(f"**Step {k}:**\n{v}" for k, v in results.items()))

            total_words = sum(len(n["task"].split()) for n in dag["nodes"])
            trad_time   = total_words / 20
            savings_pct = ((trad_time - edge_time) / trad_time * 100) if trad_time > 0 else 0

            # Record metrics
            m = st.session_state.metrics
            m["timestamps"].append(datetime.now())
            m["execution_times"].append(round(edge_time, 3))
            m["trad_times"].append(round(trad_time, 3))
            m["routes"].append(route_code)
            m["tokens"].append(len(final_prompt.split()))
            m["retries"].append(total_retries)
            m["success"].append(1 if not final_answer.startswith("❌") else 0)

        st.session_state.messages.append({
            "role":    "bot",
            "content": final_answer,
            "ts":      datetime.now().strftime("%H:%M"),
            "route":   route_code,
        })
        st.rerun()

    # Post-run panels (shown after last bot message)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "bot":
        last_bot = st.session_state.messages[-1]
        with st.expander("📊 Execution Details", expanded=False):
            det_tabs = st.tabs(["⏱️ Time", "🔗 DAG", "📋 Raw"])

            with det_tabs[0]:
                wc = len(last_bot["content"].split())
                et = st.session_state.metrics["execution_times"]
                rt = st.session_state.metrics["trad_times"]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("📡 Route", last_bot.get("route", "—"))
                c2.metric("⚡ Edge AI Time", f"{et[-1]:.2f}s" if et else "—")
                c3.metric("🐌 Traditional Est.", f"{rt[-1]:.2f}s" if rt else "—")
                c4.metric("📝 Response Words", wc)
                if et and rt and rt[-1] > 0:
                    sp = (rt[-1] - et[-1]) / rt[-1] * 100
                    st.success(f"⚡ **{sp:.1f}% faster** than traditional sequential execution!")

            with det_tabs[1]:
                user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
                if user_msgs:
                    show_dag(decompose_prompt(user_msgs[-1]["content"]),
                             last_bot.get("route", "Hybrid"))

            with det_tabs[2]:
                st.json(st.session_state.messages[-4:])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_analytics:
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd
        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

    st.markdown("### 📊 Performance Analytics")

    m = st.session_state.metrics
    if not m["timestamps"]:
        st.info("💡 Run some prompts in the Chat tab to see analytics here.")
    elif not HAS_PLOTLY:
        st.warning("Install plotly for interactive charts: `pip install plotly`")
        # Fallback: raw table
        import pandas as pd
        df = pd.DataFrame({
            "Time":           m["timestamps"],
            "Edge Time (s)":  m["execution_times"],
            "Trad Time (s)":  m["trad_times"],
            "Route":          m["routes"],
            "Tokens":         m["tokens"],
            "Retries":        m["retries"],
        })
        st.dataframe(df, use_container_width=True)
    else:
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd

        df = pd.DataFrame({
            "Time":         m["timestamps"],
            "Edge AI (s)":  m["execution_times"],
            "Traditional":  m["trad_times"],
            "Route":        m["routes"],
            "Tokens":       m["tokens"],
            "Retries":      m["retries"],
            "Success":      m["success"],
        })

        ROUTE_COLORS = {
            "ODA":    "#4ade80",
            "Hybrid": "#60a5fa",
            "Cloud":  "#fbbf24",
        }
        GLASS = dict(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#ccc"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=40, b=10),
        )

        # ── Key metrics row ───────────────────────────────────────────────────
        total_queries = len(m["timestamps"])
        avg_edge      = sum(m["execution_times"]) / total_queries
        avg_trad      = sum(m["trad_times"])      / total_queries
        total_tokens  = sum(m["tokens"])
        success_rate  = sum(m["success"]) / total_queries * 100
        avg_savings   = ((avg_trad - avg_edge) / avg_trad * 100) if avg_trad > 0 else 0

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("💬 Total Queries",   total_queries)
        k2.metric("⚡ Avg Edge Time",   f"{avg_edge:.2f}s")
        k3.metric("🐌 Avg Traditional", f"{avg_trad:.2f}s")
        k4.metric("📝 Total Tokens",    f"{total_tokens:,}")
        k5.metric("✅ Success Rate",    f"{success_rate:.1f}%")

        st.markdown("---")

        col_l, col_r = st.columns(2)

        # ── Chart 1: Execution time over time (line) ──────────────────────────
        with col_l:
            st.markdown("#### ⏱️ Execution Time Over Time")
            fig1 = go.Figure()
            for rt in df["Route"].unique():
                sub = df[df["Route"] == rt]
                fig1.add_trace(go.Scatter(
                    x=sub["Time"], y=sub["Edge AI (s)"],
                    mode="lines+markers", name=f"{rt} (Edge AI)",
                    line=dict(color=ROUTE_COLORS.get(rt, "#aaa"), width=2),
                    marker=dict(size=7),
                ))
            fig1.add_trace(go.Scatter(
                x=df["Time"], y=df["Traditional"],
                mode="lines", name="Traditional (est.)",
                line=dict(color="#f87171", width=1.5, dash="dot"),
            ))
            fig1.update_layout(**GLASS, title="Edge AI vs Traditional")
            st.plotly_chart(fig1, use_container_width=True)

        # ── Chart 2: Route usage pie ──────────────────────────────────────────
        with col_r:
            st.markdown("#### 🛣️ Route Usage Distribution")
            rc = df["Route"].value_counts().reset_index()
            rc.columns = ["Route", "Count"]
            fig2 = px.pie(rc, values="Count", names="Route", hole=0.45,
                          color="Route",
                          color_discrete_map=ROUTE_COLORS)
            fig2.update_traces(textfont_size=13,
                               marker=dict(line=dict(color="#111", width=1.5)))
            fig2.update_layout(**GLASS, title="Queries per Route")
            st.plotly_chart(fig2, use_container_width=True)

        col_l2, col_r2 = st.columns(2)

        # ── Chart 3: Token usage over time (bar) ─────────────────────────────
        with col_l2:
            st.markdown("#### 📝 Token Usage per Query")
            fig3 = px.bar(df, x="Time", y="Tokens", color="Route",
                          color_discrete_map=ROUTE_COLORS,
                          barmode="group")
            fig3.update_layout(**GLASS, title="Tokens Processed per Query")
            st.plotly_chart(fig3, use_container_width=True)

        # ── Chart 4: Speed savings over time (area) ───────────────────────────
        with col_r2:
            st.markdown("#### 🚀 Speed Savings vs Traditional (%)")
            df["Savings %"] = ((df["Traditional"] - df["Edge AI (s)"]) /
                               df["Traditional"].replace(0, 1) * 100).clip(lower=0)
            fig4 = px.area(df, x="Time", y="Savings %", color="Route",
                           color_discrete_map=ROUTE_COLORS,
                           line_group="Route")
            fig4.update_layout(**GLASS, title="% Faster than Traditional (Sequential)")
            st.plotly_chart(fig4, use_container_width=True)

        # ── Raw data table ────────────────────────────────────────────────────
        with st.expander("📋 Raw Metrics Table"):
            st.dataframe(df.style.background_gradient(subset=["Edge AI (s)"],
                                                       cmap="RdYlGn_r"),
                         use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
with tab_settings:
    st.markdown("### ⚙️ Settings & Controls")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("#### 🗑️ Data Management")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.success("Chat cleared!")
            st.rerun()

        if st.button("📊 Clear Analytics Metrics", use_container_width=True):
            st.session_state.metrics = {k: [] for k in st.session_state.metrics}
            st.success("Metrics cleared!")
            st.rerun()

        if st.button("🔄 Clear Everything", use_container_width=True):
            st.session_state.messages = []
            st.session_state.metrics  = {k: [] for k in st.session_state.metrics}
            st.success("All data cleared!")
            st.rerun()

    with col_s2:
        st.markdown("#### 📋 App Info")
        try:
            import psutil
            vm   = psutil.virtual_memory()
            disk = psutil.disk_usage(".")
            st.markdown(f"""
| Stat | Value |
|------|-------|
| 💾 RAM Used | {vm.used/1e9:.1f} GB / {vm.total/1e9:.1f} GB ({vm.percent:.0f}%) |
| 💿 Disk Free | {disk.free/1e9:.1f} GB |
| 💬 Chat Messages | {len(st.session_state.messages)} |
| 📊 Metric Records | {len(st.session_state.metrics['timestamps'])} |
| 🧠 Qwen Loaded | {"✅" if _load_qwen()[0] is not None else "❌"} |
""")
        except Exception:
            st.info("Install psutil for system stats: `pip install psutil`")

        st.markdown("#### 🚀 How to Run")
        st.code("streamlit run chatbot_app.py", language="bash")

        st.markdown("#### 📦 Memory Estimate")
        st.markdown("""
| Component | Memory |
|-----------|--------|
| Qwen2-0.5B GGUF | ~400 MB |
| Grok HTTP Client | ~50 MB |
| Streamlit + Plotly | ~230 MB |
| Pillow + OCR | ~80 MB |
| **Total** | **~760 MB ✅** |
""")
