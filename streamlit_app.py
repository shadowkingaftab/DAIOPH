import streamlit as st
from core.hybrid_orchestrator import HybridOrchestrator
from core.prompt_generator import PromptGenerator
from utils.pdf_parser import extract_text_from_pdf
from utils.logger import Logger
import graphviz
import pandas as pd
from datetime import datetime
import os
from huggingface_hub import hf_hub_download

# --- Setup ---
st.set_page_config(
    page_title="Edge AI Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] {
        height: 3rem; padding: 0 2rem; background-color: #f0f2f6;
        border-radius: 0.5rem 0.5rem 0 0; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CC9F0; color: white;
    }
    .main-header {
        font-size: 3rem; font-weight: 800; color: #4CC9F0;
        text-align: center; margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem; color: #484848; margin-bottom: 2rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #4CC9F0; color: white; border: none;
        border-radius: 0.5rem; padding: 0.5rem 2rem; font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #48B5E9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
logger = Logger()
grok_api_key = st.secrets.get("GROK_API_KEY", None)

# Auto-download Qwen model if it doesn't exist
MODEL_DIR = "models"
MODEL_FILE = "qwen2-0_5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

os.makedirs(MODEL_DIR, exist_ok=True)
if not os.path.exists(MODEL_PATH):
    with st.spinner(f"Downloading {MODEL_FILE} (approx 400MB). This happens only once..."):
        hf_hub_download(
            repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
            filename=MODEL_FILE,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False
        )

orchestrator = HybridOrchestrator(
    distilbert_path="distilbert-base-uncased",
    qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
    grok_api_key=grok_api_key
)
prompt_generator = PromptGenerator("models/qwen2-0_5b-instruct-q4_k_m.gguf")

# --- Title ---
st.markdown('<p class="main-header">🤖 Edge AI Orchestrator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">DistilBERT Orchestrator • Qwen2-0.5B Execution • Grok Cloud Fallback</p>', unsafe_allow_html=True)

if getattr(orchestrator, 'executor', None) and not getattr(orchestrator.executor, 'HAS_QWEN', True):
    st.error(f"⚠️ **Qwen2-0.5B failed to load!** Reason: `{getattr(orchestrator.executor, 'qwen_error', 'Unknown Error')}`")
    st.info("💡 You can still use the Cloud LLM route if you provide a Grok API Key in the sidebar.")

# --- Sidebar: Model Routes ---
with st.sidebar:
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
    if grok_api_key_ui:
        orchestrator.grok_api_key = grok_api_key_ui
        grok_api_key = grok_api_key_ui

# --- Main App (Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Classify & Execute",
    "📊 Analytics",
    "📜 Logs",
    "🔍 ODA Insights",
    "✨ Generate Prompts"
])

# --- Tab 1: Classify & Execute ---
with tab1:
    st.markdown("### Classify & Execute a Prompt")
    st.info("DistilBERT splits prompts into tasks, then executes them using the selected route (ODA/Hybrid/Cloud).")

    route = st.selectbox(
        "Select execution route:",
        ["ODA (Qwen2-0.5B only)", "Hybrid (Qwen + Grok)", "Cloud LLM (Grok + Qwen fallback)"],
        index=1
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        user_prompt = st.text_area("Your prompt:", placeholder="e.g., First, summarize this PDF. Then, write a tweet about it.", height=150)
    with col2:
        input_method = st.radio("Input Method:", ["Text", "PDF + Text"])

    pdf_text = None
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
        else:
            with st.spinner("Processing..."):
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
                dag, results = orchestrator.execute(user_prompt, pdf_text, route_map[route])

                end_time = datetime.now()
                log_entry.update({
                    "status": "completed",
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "duration": str(end_time - start_time),
                    "dag": dag,
                    "results": results
                })
                logger.log(log_entry)

                st.markdown("#### 🔗 Task Bifurcation DAG")
                try:
                    graph = graphviz.Digraph(graph_attr={"rankdir": "LR"})
                    for node in dag["dag"]["nodes"]:
                        graph.node(node["id"], node["task"][:30] + "...")
                    for node in dag["dag"]["nodes"]:
                        if "depends_on" in node:
                            for dep in node["depends_on"]:
                                graph.edge(dep, node["id"])
                    st.graphviz_chart(graph)
                except Exception as e:
                    st.warning("Graphviz is not installed on this system. Showing raw DAG structure:")
                    st.json(dag["dag"])

                st.markdown("#### 💡 Execution Results")
                for task_id, result in results.items():
                    if isinstance(result, dict) and "error" in result:
                        st.error(f"**Task {task_id}:** {result['error']}")
                    else:
                        st.success(f"**Task {task_id}:**")
                        st.write(result)

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
