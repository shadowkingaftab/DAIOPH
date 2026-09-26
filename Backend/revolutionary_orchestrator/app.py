import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import LLMOrchestrator
from orchestrator.visualizer import visualize_dag
from utils.pdf_parser import extract_text_from_pdf

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LLMCompiler + Self-Refine",
    page_icon="🔥",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); }
    .main-header {
        background: linear-gradient(90deg, #e94560, #0f3460);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 700;
    }
    .role-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-success { background: #1a4731; color: #4ade80; }
    .badge-failed  { background: #4b1c1c; color: #f87171; }
    .badge-partial { background: #3b2f00; color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🔥 Revolutionary Prompt Bifurcation</h1>', unsafe_allow_html=True)
st.markdown("**Dual-Role Architecture** · Planner (structured) + Executor (generative) · 100% offline")

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Model Configuration")

    # Auto-detect working model path
    parent_models_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_05b = os.path.join(parent_models_dir, "qwen2-0_5b-instruct-q4_k_m.gguf")
    model_18b = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "qwen-1_8b-chat-q4_k_m.gguf"))
    default_model = model_05b if os.path.exists(model_05b) else model_18b

    st.markdown("**🧠 Planner Model** *(fast, structured JSON)*")
    planner_path = st.text_input(
        "Planner GGUF path",
        value=default_model,
        help="Small, deterministic model for DAG generation (n_ctx=1024, temp=0.1)"
    )

    st.markdown("**⚡ Executor Model** *(generative, context-aware)*")
    executor_path = st.text_input(
        "Executor GGUF path",
        value=default_model,
        help="Generative model for task execution (n_ctx=4096, temp=0.3)"
    )

    st.markdown("---")
    st.markdown("**Pipeline**")
    st.markdown("1. 🧠 **Planner** → generates task DAG (temp=0.1)")
    st.markdown("2. ⚡ **Executor** → runs tasks with context (temp=0.3)")
    st.markdown("3. 🔁 **Refiner** → fixes failures (shares Planner)")
    st.markdown("4. 📊 Real-time DAG visualization")
    st.markdown("---")
    st.caption("✅ Fully offline. No API keys. Swap models anytime.")

# ─── Session State ────────────────────────────────────────────────────────────
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None

# ─── Model Loader ─────────────────────────────────────────────────────────────
col_btn, col_status = st.columns([3, 1])
with col_btn:
    if st.button("🚀 Initialize Orchestrator", use_container_width=True):
        errors = []
        if not os.path.exists(planner_path):
            errors.append(f"Planner model not found: `{planner_path}`")
        if not os.path.exists(executor_path):
            errors.append(f"Executor model not found: `{executor_path}`")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            with st.spinner("Loading Planner + Executor instances..."):
                try:
                    st.session_state.orchestrator = LLMOrchestrator(
                        planner_model_path=planner_path,
                        executor_model_path=executor_path
                    )
                    # Show which config is active
                    same = planner_path == executor_path
                    if same:
                        st.success("✅ Orchestrator ready! (Dual-config, single model file)")
                    else:
                        st.success("✅ Orchestrator ready! (Separate planner + executor models)")
                except Exception as e:
                    st.error(f"❌ Failed to initialize: {e}")
                    st.exception(e)

with col_status:
    if st.session_state.orchestrator:
        st.markdown('<span class="status-badge badge-success">● READY</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge badge-failed">● NOT LOADED</span>', unsafe_allow_html=True)

st.divider()

# ─── Input ────────────────────────────────────────────────────────────────────
input_method = st.radio("📥 Input Method", ["Text Prompt", "PDF + Prompt"], horizontal=True)
pdf_text = None

if input_method == "Text Prompt":
    user_prompt = st.text_area(
        "Enter your complex prompt:",
        height=160,
        placeholder="e.g. Write a blog post about the future of AI — engaging and informative"
    )
else:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        pdf_path = os.path.join(os.path.dirname(__file__), f"temp_{uploaded_file.name}")
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        pdf_text = extract_text_from_pdf(pdf_path)
        st.success(f"✅ Extracted **{len(pdf_text.split())} words** from PDF")
        with st.expander("📄 PDF Preview"):
            st.write(pdf_text[:600] + "...")
    user_prompt = st.text_input(
        "What to do with this PDF?",
        value="Summarize this document and list the main action items"
    )

# ─── Execute ─────────────────────────────────────────────────────────────────
if st.button("⚡ Execute Pipeline", type="primary", use_container_width=True):
    if not st.session_state.orchestrator:
        st.warning("⚠️ Please initialize the orchestrator first.")
    elif not user_prompt:
        st.warning("⚠️ Please enter a prompt.")
    else:
        with st.spinner("🧠 Planning DAG → ⚡ Executing tasks → 🔁 Self-refining..."):
            try:
                result = st.session_state.orchestrator.execute(user_prompt, pdf_text)

                # ── DAG Visualization ──────────────────────────────────────
                st.subheader("🔗 Task Bifurcation DAG")
                visualize_dag(result["dag"], result["execution_results"])

                # ── Status ────────────────────────────────────────────────
                status = result["status"]
                if status == "completed":
                    st.success("🎉 All tasks completed successfully!")
                else:
                    st.warning("⚠️ Pipeline completed with some failures (self-refine attempted).")

                # ── Final Synthesized Response ────────────────────────────
                st.subheader("💡 Final Synthesized Response")
                final_parts = []
                for node in result["dag"].get("nodes", []):
                    tid = node["id"]
                    output = result["execution_results"].get(tid)
                    if output and not (isinstance(output, dict) and "error" in output):
                        label = node["task"][:60]
                        final_parts.append(f"**🔹 {label}**\n\n{output}")

                if final_parts:
                    st.markdown("\n\n---\n\n".join(final_parts))
                else:
                    st.warning("No successful outputs to display.")

            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.exception(e)
