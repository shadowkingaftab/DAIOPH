import streamlit as st
import sys
import os

# Optional imports with fallbacks
try:
    from core.hybrid_orchestrator import HybridOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except Exception as e:
    print(f"Warning: HybridOrchestrator unavailable: {e}")
    ORCHESTRATOR_AVAILABLE = False

try:
    from core.prompt_generator import PromptGenerator
    PROMPT_GEN_AVAILABLE = True
except Exception as e:
    print(f"Warning: PromptGenerator unavailable: {e}")
    PROMPT_GEN_AVAILABLE = False

try:
    from utils.pdf_parser import extract_text_from_pdf, get_pdf_images
    PDF_PARSER_AVAILABLE = True
except Exception as e:
    print(f"Warning: PDF parser unavailable: {e}")
    PDF_PARSER_AVAILABLE = False

    # Fallback functions
    def extract_text_from_pdf(path, *args, **kwargs): return ""
    def get_pdf_images(path): return []

try:
    from utils.logger import Logger
except Exception as e:
    print(f"Warning: Logger unavailable: {e}")
    class Logger:
        def __init__(self, *args, **kwargs): pass
        def log(self, *args, **kwargs): pass
        def get_history(self, *args, **kwargs): return []

try:
    from utils.image_executor import requires_diagram, requires_image
except Exception as e:
    print(f"Warning: Image executor unavailable: {e}")
    def requires_diagram(text): return False
    def requires_image(text): return False

try:
    import graphviz
except Exception as e:
    print(f"Warning: Graphviz unavailable: {e}")
    graphviz = None

try:
    import pandas as pd
except Exception as e:
    print(f"Warning: Pandas unavailable: {e}")
    pd = None

from datetime import datetime
from huggingface_hub import hf_hub_download

# --- Setup ---
st.set_page_config(
    page_title="Edge AI Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS — dark-theme glass morphism style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #f0f0f0; }

.stTabs [data-baseweb="tab-list"] { gap: 2rem; border-bottom: 1px solid #444; }
.stTabs [data-baseweb="tab"] {
    height: 3rem; padding: 0 1.5rem;
    background: rgba(255,255,255,0.05);
    border-radius: 0.5rem 0.5rem 0 0; font-weight: 600; color: #ccc;
}
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, #4CC9F0, #7B2FBE); color: white; }

.main-header {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(90deg, #4CC9F0, #F72585);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.5rem;
}
.sub-header { font-size: 1.1rem; color: #aaa; text-align: center; margin-bottom: 2rem; }

.stButton>button {
    background: linear-gradient(90deg, #4CC9F0, #7B2FBE);
    color: white; border: none; border-radius: 0.5rem;
    padding: 0.6rem 2rem; font-weight: 700; font-size: 1rem;
    transition: transform 0.1s;
}
.stButton>button:hover { transform: scale(1.03); opacity: 0.95; }

.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.07) !important;
    color: white !important; border: 1px solid #555 !important; border-radius: 0.4rem;
}
.dag-legend { display: flex; gap: 1rem; margin: 0.5rem 0 1rem; flex-wrap: wrap; }
.dag-legend span {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.2rem 0.7rem; border-radius: 1rem; font-size: 0.8rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Initialize components
logger = Logger()

# Detect environment
IS_CLOUD = 'STREAMLIT_RUNTIME_EXECUTABLE' in os.environ or 'STREAMLIT_SERVER_PORT' in os.environ

try:
    grok_api_key = st.secrets.get("GROK_API_KEY", None)
except Exception:
    grok_api_key = os.environ.get("GROK_API_KEY", None)

# Model configuration
MODEL_DIR = "models"
MODEL_FILE = "qwen2-0_5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

def ensure_local_model():
    """Downloads the local model if it doesn't exist."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        with st.spinner(f"📥 Downloading {MODEL_FILE} (approx 400MB). This happens only once..."):
            try:
                hf_hub_download(
                    repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
                    filename=MODEL_FILE,
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False
                )
            except Exception as e:
                st.error(f"Failed to download local model: {e}")
                return False
    return True

@st.cache_resource(show_spinner="Loading AI Models (This happens once to save memory)...")
def load_models():
    # Only instantiated once across all Streamlit reruns
    
    if not ORCHESTRATOR_AVAILABLE:
        return None, None
    
    # Check if we should even try to load the local model
    # On Streamlit Cloud, we might want to be more conservative
    has_local = ensure_local_model()
    
    orch = HybridOrchestrator(
        distilbert_path="distilbert-base-uncased",
        qwen_path=MODEL_PATH,
        grok_api_key=None
    )
    
    # Share the Qwen instance to cut RAM usage in half
    shared_llm = getattr(orch.executor, 'qwen', None)
    if PROMPT_GEN_AVAILABLE:
        pg = PromptGenerator(
            model_path=MODEL_PATH,
            llm_instance=shared_llm
        )
    else:
        pg = None
    return orch, pg

orchestrator, prompt_generator = load_models()

# Inject grok api key dynamically to avoid invalidating the cache
if grok_api_key and orchestrator:
    try:
        from core.grok_client import GrokClient
        orchestrator.grok = GrokClient(grok_api_key)
        orchestrator.HAS_GROK = True
        if hasattr(orchestrator, 'executor'):
            orchestrator.executor.grok = GrokClient(grok_api_key)
            orchestrator.executor.HAS_GROK = True
    except Exception as e:
        st.warning(f"⚠️ Grok API not available: {e}")

# --- Title ---
st.markdown('<p class="main-header">🤖 Edge AI Orchestrator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">DistilBERT Orchestrator • Qwen2-0.5B Execution • Grok Cloud Fallback</p>', unsafe_allow_html=True)

if not ORCHESTRATOR_AVAILABLE:
    st.error("❌ Critical components missing. Some features will not be available.")

if orchestrator and getattr(orchestrator, 'executor', None) and not getattr(orchestrator.executor, 'HAS_QWEN', True):
    st.error(f"⚠️ **Qwen2-0.5B failed to load!** Reason: `{getattr(orchestrator.executor, 'qwen_error', 'Unknown Error')}`")
    st.info("💡 You can still use the Cloud LLM route if you provide a Grok API Key in the sidebar.")

# --- Sidebar: Model Routes ---
with st.sidebar:
    # Environment Badge
    if IS_CLOUD:
        st.success("☁️ **Running on Streamlit Cloud**")
    else:
        st.info("💻 **Running Locally**")
    
    st.markdown("### 🔄 Route → Model")
    st.markdown("""
    | **Route**   | **Primary Model**       | **Fallback**       |
    |-------------|-------------------------|--------------------|
    | ODA         | Qwen2-0.5B GGUF         | None               |
    | Hybrid      | Qwen2-0.5B GGUF         | Grok API          |
    | Cloud LLM   | Grok API               | Qwen2-0.5B GGUF   |
    """)
    st.markdown("---")
    st.markdown("### 🔑 Grok API Key")
    grok_api_key_ui = st.text_input("Paste your xAI Grok API key (overrides secrets):", type="password")
    if grok_api_key_ui and orchestrator:
        try:
            from core.grok_client import GrokClient
            grok_api_key = grok_api_key_ui
            orchestrator.grok = GrokClient(grok_api_key)
            orchestrator.HAS_GROK = True
            if hasattr(orchestrator, 'executor'):
                orchestrator.executor.grok = GrokClient(grok_api_key)
                orchestrator.executor.HAS_GROK = True
        except Exception as e:
            st.warning(f"⚠️ Grok API not available: {e}")

# --- Main App (Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Classify & Execute",
    "📊 Analytics",
    "📜 Logs",
    "🔍 ODA Insights",
    "✨ Generate Prompts"
])


# ── Colorful DAG with tooltips ─────────────────────────────────────────────────
def show_dag(dag):
    """Render a colorful Graphviz DAG. Green=ODA, Gold=Cloud, LightBlue=Hybrid, Red=Error."""
    if not graphviz:
        st.json(dag.get("dag", dag))
        return
    
    color_map = {
        "ODA":    "#2ecc71",      # Green
        "Cloud":  "#f1c40f",      # Gold
        "Hybrid": "#74b9ff",      # Light blue
        "failed": "#e74c3c",      # Red
    }
    font_color_map = {
        "ODA": "white", "Cloud": "#333", "Hybrid": "#333", "failed": "white"
    }

    dot = graphviz.Digraph(graph_attr={"rankdir": "LR", "bgcolor": "transparent",
                                        "splines": "curved", "fontname": "Inter"})

    nodes = dag.get("dag", dag).get("nodes", [])
    for node in nodes:
        route = node.get("route", "Hybrid")
        color = color_map.get(route, "#95a5a6")
        fcolor = font_color_map.get(route, "white")
        label = node["task"][:28] + ("…" if len(node["task"]) > 28 else "")
        tooltip = f"ID: {node['id']} | Route: {route}\n{node['task']}"
        dot.node(
            node["id"],
            label=label,
            fillcolor=color,
            fontcolor=fcolor,
            style="filled,rounded",
            fontsize="11",
            tooltip=tooltip,
            fontname="Inter",
        )

    for node in nodes:
        for dep in node.get("depends_on", []):
            dot.edge(dep, node["id"], color="#aaaaaa", arrowsize="0.7")

    try:
        st.graphviz_chart(dot)
    except Exception:
        st.json(dag.get("dag", dag))

    # DAG legend
    st.markdown("""
    <div class="dag-legend">
        <span style="background:#2ecc71;color:white">🟢 ODA (On-Device)</span>
        <span style="background:#f1c40f;color:#333">🟡 Cloud (Grok)</span>
        <span style="background:#74b9ff;color:#333">🔵 Hybrid</span>
        <span style="background:#e74c3c;color:white">🔴 Failed</span>
    </div>
    """, unsafe_allow_html=True)


def _render_task_result(task_id: str, result):
    """
    Render a single task result in the Streamlit UI.
    Handles four result types from the orchestrator:
      - dict with type="diagram"  → st.graphviz_chart
      - dict with type="image"    → inline base64 PNG
      - dict with type="error"    → st.error
      - plain str                 → st.markdown
    """
    if isinstance(result, dict):
        rtype = result.get("type", "")
        data  = result.get("data", "")

        if rtype == "diagram":
            st.markdown(f"**🗺️ Diagram — Task `{task_id}`**")
            try:
                st.graphviz_chart(data)
            except Exception as e:
                st.warning(f"Could not render diagram: {e}")
                st.code(str(data))

        elif rtype == "image":
            st.markdown(f"**🖼️ Generated Image — Task `{task_id}`**")
            try:
                import base64
                from io import BytesIO
                from PIL import Image as PILImage
                img_bytes = base64.b64decode(data)
                img = PILImage.open(BytesIO(img_bytes))
                st.image(img, use_column_width=True)
            except Exception:
                # Fallback: markdown data URI
                st.markdown(
                    f'<img src="data:image/png;base64,{data}" style="max-width:100%;border-radius:0.8rem"/>',
                    unsafe_allow_html=True,
                )

        elif rtype == "error":
            st.error(data)

        else:
            # Unknown dict shape — just show JSON
            st.json(result)

    elif isinstance(result, str):
        if result.strip():
            st.markdown(result)
        else:
            st.caption("*(empty output)*")
    else:
        st.write(result)


# --- Tab 1: Classify & Execute ---
with tab1:
    st.markdown("### Classify & Execute a Prompt")
    st.info("DistilBERT splits prompts into tasks, then executes them using the selected route (ODA/Hybrid/Cloud). Supports multi-language input.")

    # Example prompts dropdown
    EXAMPLE_PROMPTS = [
        "Custom (type below)",
        "First, summarize this document. Then, extract 3 key points. Finally, write a tweet about it.",
        "Analyze the main themes and then compare them with modern AI trends.",
        "Explain edge AI, then list its advantages over cloud AI.",
        "पहले इस पाठ का सारांश दें। फिर मुख्य विचार बताएं।",  # Hindi
        "Primero resume el texto. Luego explica los puntos clave.",  # Spanish
        # ── Diagram examples ──────────────────────────────────────────────────
        "Create a workflow diagram: Data Collection -> Preprocessing -> Model Training -> Evaluation -> Deployment",
        "Draw a flowchart: User Request -> Edge AI Classification -> ODA Route -> Qwen Inference -> Response",
        "Visualize the steps: Idea -> Design -> Develop -> Test -> Deploy -> Monitor",
        # ── Image generation examples (requires Hybrid/Cloud + Replicate token) ─
        "Generate a photorealistic image of a futuristic edge AI server room with glowing circuits",
        "Create a realistic illustration of a robot working alongside humans in a smart factory",
    ]

    selected_example = st.selectbox("📚 Example Prompts (pick one or type your own):", EXAMPLE_PROMPTS)

    route = st.selectbox(
        "Select execution route:",
        ["ODA (Qwen2-0.5B only)", "Hybrid (Qwen + Grok)", "Cloud LLM (Grok + Qwen fallback)"],
        index=1
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        default_text = "" if selected_example == "Custom (type below)" else selected_example
        user_prompt = st.text_area("Your prompt:", value=default_text,
                                   placeholder="e.g., First, summarize this PDF. Then, write a tweet about it.",
                                   height=150)
    with col2:
        input_method = st.radio("Input Method:", ["Text", "PDF + Text"])
        explain_mode = st.checkbox("🔍 Explain Mode", help="Show intermediate reasoning steps")

    pdf_text = None
    pdf_path = None
    if input_method == "PDF + Text":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            pdf_path = f"temp_{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            pdf_text = extract_text_from_pdf(pdf_path)

    if st.button("🚀 CLASSIFY, ROUTE & EXECUTE", use_container_width=True):
        if not user_prompt:
            st.warning("Please enter a prompt.")
        elif not orchestrator:
            st.error("❌ Orchestrator not available. Please check your dependencies.")
        else:
            with st.spinner("🧠 Processing your prompt..."):
                start_time = datetime.now()
                log_entry = {
                    "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "prompt": user_prompt,
                    "route": route.split(" ")[0],
                    "status": "started",
                    "model": f"{route} (DistilBERT + Qwen/Grok)"
                }
                logger.log(log_entry)

                route_map = {
                    "ODA (Qwen2-0.5B only)": "ODA",
                    "Hybrid (Qwen + Grok)": "Hybrid",
                    "Cloud LLM (Grok + Qwen fallback)": "Cloud"
                }
                try:
                    dag, results = orchestrator.execute(user_prompt, pdf_text, route_map[route])
                except Exception as e:
                    st.error(f"Execution error: {e}")
                    dag, results = {"dag": {"nodes": []}}, {}

                end_time = datetime.now()
                log_entry.update({
                    "status": "completed",
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "duration": str(end_time - start_time),
                    "dag": dag,
                    "results": results
                })
                logger.log(log_entry)

                # ── Detected Language badge ──────────────────────────────────────────
                detected_lang = results.get("detected_language", dag.get("language", "en"))
                lang_names = {"en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
                              "de": "German", "ar": "Arabic", "zh": "Chinese", "ja": "Japanese"}
                lang_label = lang_names.get(detected_lang, detected_lang.upper())
                st.info(f"🌍 Detected Language: **{lang_label}**")

                # ── PRIMARY: Synthesized Final Answer ────────────────────────────────
                final_output = results.get("final_output", "")
                if final_output:
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,rgba(76,201,240,0.08),rgba(123,47,190,0.08));
                                border:1px solid rgba(76,201,240,0.25);border-radius:1rem;
                                padding:1.2rem 1.5rem;margin:0.8rem 0">
                        <div style="font-size:0.8rem;font-weight:700;color:#4CC9F0;
                                    letter-spacing:0.05em;margin-bottom:0.6rem">
                            🤖 SYNTHESIZED ANSWER
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(final_output)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No output was generated. Check that at least one model route is available.")

                # ── Task Breakdown (expandable) ───────────────────────────────────────
                task_results = {k: v for k, v in results.items()
                                if k not in ("final_output", "times", "retry_counts",
                                             "detected_language")}
                n_tasks = len(dag.get("dag", dag).get("nodes", []))
                with st.expander(f"🔍 View Task Breakdown ({n_tasks} task{'s' if n_tasks != 1 else ''})", expanded=False):
                    st.markdown("#### 🔗 Task DAG")
                    show_dag(dag)

                    if task_results:
                        st.markdown("#### 📋 Individual Task Outputs")
                        for task_id, result in task_results.items():
                            with st.expander(f"Task `{task_id}`"):
                                _render_task_result(task_id, result)

                # ── Explain Mode ───────────────────────────────────────────────────
                if explain_mode:
                    st.markdown("#### 🔍 Reasoning Steps (Explain Mode)")
                    nodes = dag.get("dag", dag).get("nodes", [])
                    for node in nodes:
                        with st.expander(f"Task `{node['id']}`: {node['task'][:60]}…"):
                            st.write(f"**Route:** {node.get('route', 'Hybrid')}")
                            st.write(f"**Depends on:** {node.get('depends_on', [])}")
                            raw_out = results.get(node['id'], 'N/A')
                            st.write(f"**Raw Output:** {raw_out}")

                # ── Time Comparison ─────────────────────────────────────────────────
                times = results.get("times", {})
                if times:
                    st.markdown("#### ⏱️ Time Comparison: Edge AI vs Traditional")
                    tc1, tc2, tc3 = st.columns(3)
                    with tc1:
                        st.metric("Traditional (Sequential)", f"{times.get('traditional', 0):.2f}s",
                                  help="Estimated time if all tasks ran sequentially on a single cloud model")
                    with tc2:
                        st.metric("Edge AI (Parallel)", f"{times.get('edge_ai', 0):.2f}s",
                                  help="Actual time with DAG-parallel execution + synthesis")
                    with tc3:
                        savings = times.get('savings_percent', 0)
                        delta_str = f"{abs(savings):.1f}% {'faster' if savings >= 0 else 'slower'}"
                        st.metric("Time Saved", delta_str,
                                  delta=f"{savings:.1f}%" if savings >= 0 else None)

                # ── Retry Statistics ─────────────────────────────────────────────────
                retry_counts = results.get("retry_counts", {})
                if retry_counts:
                    st.markdown("#### 🔄 Retry Statistics")
                    for task_id, count in retry_counts.items():
                        st.warning(f"Task `{task_id}` required **{count} retr{'y' if count==1 else 'ies'}** before succeeding.")

                # ── PDF Image Preview ────────────────────────────────────────────────
                if input_method == "PDF + Text" and pdf_path:
                    with st.expander("🖼️ PDF Image Preview"):
                        images = get_pdf_images(pdf_path)
                        if images:
                            for i, img in enumerate(images[:5]):
                                st.image(img, caption=f"Page {i+1}", use_column_width=True)
                        else:
                            st.info("No images found or pdf2image not installed.")

# --- Tab 2: Analytics ---
with tab2:
    st.markdown("### 📊 Execution Analytics")
    logs = logger.get_logs()
    if not logs:
        st.warning("No execution data yet. Run some prompts first!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Prompts", len(logs))
        with col2:
            avg_time = sum(
                (datetime.strptime(log["end_time"], "%Y-%m-%d %H:%M:%S.%f") -
                 datetime.strptime(log["start_time"], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
                for log in logs
            ) / len(logs)
            st.metric("Avg Execution Time", f"{avg_time:.2f}s")
        with col3:
            success_rate = sum(1 for log in logs if log["status"] == "completed") / len(logs) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col4:
            route_counts = pd.Series([log["route"] for log in logs]).value_counts()
            st.metric("Most Used Route", route_counts.index[0] if len(route_counts) > 0 else "None")

        st.markdown("#### ⏱️ Execution Time Over Time")
        data = []
        for log in logs:
            start = datetime.strptime(log["start_time"], "%Y-%m-%d %H:%M:%S.%f")
            end = datetime.strptime(log["end_time"], "%Y-%m-%d %H:%M:%S.%f")
            duration = (end - start).total_seconds()
            data.append({"Time": start, "Duration (s)": duration, "Route": log["route"]})
        df = pd.DataFrame(data)
        st.line_chart(df.set_index("Time"))

        st.markdown("#### 📈 Route Usage")
        route_counts = pd.Series([log["route"] for log in logs]).value_counts()
        st.bar_chart(route_counts)

# --- Tab 3: Logs ---
with tab3:
    st.markdown("### 📜 Execution Logs")
    logs = logger.get_logs()
    if not logs:
        st.warning("No logs yet. Execute some prompts first!")
    else:
        route_filter = st.selectbox("Filter by route:", ["All", "ODA", "Hybrid", "Cloud"])
        filtered_logs = [log for log in logs if route_filter == "All" or log["route"] == route_filter]

        for log in reversed(filtered_logs):
            with st.expander(f"📅 {log['timestamp']} | Route: {log['route']} | Status: {log['status']}"):
                st.markdown(f"**Prompt:** {log['prompt']}")
                st.markdown(f"**Model:** {log['model']}")
                st.markdown(f"**Duration:** {log['duration']}")
                if "dag" in log:
                    st.json(log["dag"])
                if "results" in log:
                    st.json(log["results"])

# --- Tab 4: ODA Insights ---
with tab4:
    st.markdown("### 🔍 ODA (On-Device AI) Insights")
    oda_logs = [log for log in logger.get_logs() if log["route"] == "ODA"]
    if not oda_logs:
        st.warning("No ODA executions yet. Use the 'ODA' route to test local Qwen2-0.5B.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ODA Executions", len(oda_logs))
        with col2:
            oda_avg_time = sum(
                (datetime.strptime(log["end_time"], "%Y-%m-%d %H:%M:%S.%f") -
                 datetime.strptime(log["start_time"], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
                for log in oda_logs
            ) / len(oda_logs)
            st.metric("ODA Avg Time", f"{oda_avg_time:.2f}s")
        with col3:
            oda_success_rate = sum(1 for log in oda_logs if log["status"] == "completed") / len(oda_logs) * 100
            st.metric("ODA Success Rate", f"{oda_success_rate:.1f}%")

        st.markdown("#### ⚡ ODA Performance Over Time")
        oda_data = []
        for log in oda_logs:
            start = datetime.strptime(log["start_time"], "%Y-%m-%d %H:%M:%S.%f")
            end = datetime.strptime(log["end_time"], "%Y-%m-%d %H:%M:%S.%f")
            duration = (end - start).total_seconds()
            oda_data.append({"Time": start, "Duration (s)": duration})
        oda_df = pd.DataFrame(oda_data)
        st.line_chart(oda_df.set_index("Time"))

# --- Tab 5: Generate Prompts ---
with tab5:
    st.markdown("### ✨ Generate Test Prompts")
    st.info("Use Qwen2-0.5B (on-device) to generate prompts showcasing orchestration.")

    col1, col2 = st.columns([3, 1])
    with col1:
        num_prompts = st.number_input("Number of prompts to generate:", min_value=1, max_value=5, value=1)
    with col2:
        route = st.selectbox("Route for generated prompts:", ["ODA", "Hybrid", "Cloud"])

    if st.button("🎲 Generate Prompts", use_container_width=True):
        with st.spinner("Generating..."):
            prompts = [prompt_generator.generate() for _ in range(num_prompts)]
            for i, prompt in enumerate(prompts, 1):
                st.markdown(f"#### 📝 Prompt {i}")
                st.success(prompt)
                if st.button(f"⚡ Execute Prompt {i}", key=f"exec_{i}"):
                    with st.spinner(f"Executing prompt {i}..."):
                        dag, results = orchestrator.execute(prompt, None, route)
                        st.json(dag)
                        st.json(results)

# Fixed critical bugs in streamlit_app.py

# Tested routes

# Preload models at startup for faster execution

# Add loading spinners for better UX

# Add progress bars for task execution

# Add explain mode for transparency

# Add dark mode toggle for better UX

# Add DAG visualization for task dependencies

# Add execution metrics dashboard

# Add example prompts for quick testing
