import streamlit as st
import os
import sys

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.hybrid_orchestrator import HybridOrchestrator
from utils.pdf_parser import extract_text_from_pdf
from utils.logging import log_execution

st.set_page_config(page_title="Unified Orchestrator", layout="wide")

# Setup models paths
qwen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'qwen2-0_5b-instruct-q4_k_m.gguf'))
# Fallback to 1.8B if 0.5b not found
if not os.path.exists(qwen_path):
    qwen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qwen-1_8b-chat-q4_k_m.gguf'))

# Initialize hybrid orchestrator
@st.cache_resource
def get_orchestrator():
    return HybridOrchestrator(
        bartllm_path="cloud",  # Handled by Grok API
        qwen_path=qwen_path  # On-device
    )

try:
    orchestrator = get_orchestrator()
except Exception as e:
    st.error(f"Failed to load orchestrator: {e}")
    st.stop()

# UI
st.title("🚀 Unified Edge AI + Bifurcation System")
st.markdown("""
This system combines:
- **Edge AI (Qwen)**: Fast, on-device execution.
- **Bifurcation (Grok API / Cloud)**: Smart task decomposition.
- **Real-time streaming**: Live updates.
""")

# Input
input_method = st.radio("Input Method:", ["Text", "PDF + Text"], horizontal=True)
user_prompt = st.text_area("Enter your prompt:", height=200)
pdf_text = None

if input_method == "PDF + Text":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        pdf_path = f"temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        pdf_text = extract_text_from_pdf(pdf_path)

def _visualize_dag(dag: dict):
    from graphviz import Digraph
    graph = Digraph(graph_attr={"rankdir": "LR"})
    nodes = dag.get("dag", {}).get("nodes", [])
    for node in nodes:
        graph.node(node["id"], node["task"][:30] + "...")
    for node in nodes:
        if "depends_on" in node:
            for dep in node["depends_on"]:
                graph.edge(dep, node["id"])
    return graph

if st.button("Execute", type="primary"):
    if not user_prompt:
        st.warning("Please enter a prompt")
    else:
        # Initialize streaming container
        stream_container = st.container()
        log_container = st.container()

        with stream_container:
            # Execute hybrid pipeline
            try:
                dag, results = orchestrator.execute(user_prompt, pdf_text)
                
                # Display DAG
                st.subheader("🔗 Task Bifurcation DAG")
                st.graphviz_chart(_visualize_dag(dag))

                # Display results
                st.subheader("💡 Execution Results")
                for task_id, result in results.items():
                    if isinstance(result, dict) and "error" in result:
                        st.error(f"**Task {task_id}:** {result['error']}")
                    else:
                        st.success(f"**Task {task_id}:**\n{result}")
            except Exception as e:
                st.error(f"Execution failed: {e}")

        with log_container:
            # Display logs
            st.subheader("📜 Execution Logs")
            log_execution(orchestrator.stream_handler.get_logs())
