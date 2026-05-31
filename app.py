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
from PIL import Image
import speech_recognition as sr
import pytesseract

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
try:
    grok_api_key = st.secrets.get("GROK_API_KEY", None)
except Exception:
    grok_api_key = os.environ.get("GROK_API_KEY", None)

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

@st.cache_resource(show_spinner="Loading AI Models (This happens once to save memory)...")
def load_models():
    # Only instantiated once across all Streamlit reruns
    orch = HybridOrchestrator(
        distilbert_path="distilbert-base-uncased",
        qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
        grok_api_key=None
    )
    # Share the Qwen instance to cut RAM usage in half
    shared_llm = getattr(orch.executor, 'qwen', None)
    pg = PromptGenerator(
        model_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
        llm_instance=shared_llm
    )
    return orch, pg

orchestrator, prompt_generator = load_models()

# Inject grok api key dynamically to avoid invalidating the cache
if grok_api_key:
    from core.grok_client import GrokClient
    orchestrator.grok = GrokClient(grok_api_key)
    orchestrator.HAS_GROK = True
    if hasattr(orchestrator, 'executor'):
        orchestrator.executor.grok = GrokClient(grok_api_key)
        orchestrator.executor.HAS_GROK = True

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
        from core.grok_client import GrokClient
        grok_api_key = grok_api_key_ui
        orchestrator.grok = GrokClient(grok_api_key)
        orchestrator.HAS_GROK = True
        if hasattr(orchestrator, 'executor'):
            orchestrator.executor.grok = GrokClient(grok_api_key)
            orchestrator.executor.HAS_GROK = True

# --- Main App (Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Classify & Execute",
    "📊 Analytics",
    "📜 Logs",
    "🔍 ODA Insights",
    "✨ Generate Prompts"
])

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# --- Tab 1: Classify & Execute ---
with tab1:
    st.markdown("### Classify & Execute a Prompt")
    st.info("DistilBERT splits prompts into tasks, then executes them using the selected route (ODA/Hybrid/Cloud).")

    # --- Minimalist Chatbox UI ---
    st.markdown("""
    <style>
        /* Chatbox Container */
        .chatbox {
            position: fixed;
            bottom: 20px;
            left: 5%;
            right: 5%;
            background: rgba(15, 15, 15, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
        }

        /* Input Area */
        .chat-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            color: white;
            outline: none;
        }
        .chat-input:focus {
            background: rgba(255, 255, 255, 0.1);
        }

        /* Icon Buttons */
        .icon-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 4px;
            width: 36px;
            height: 36px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .icon-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        /* File Uploader (Hidden) */
        .stFileUploader > div > div > div {
            display: none;
        }

        /* Send Button */
        .send-btn {
            background: #4C97F0;
            border: none;
            border-radius: 4px;
            width: 36px;
            height: 36px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .send-btn:hover {
            background: #3A7BC8;
        }
        .send-btn:disabled {
            background: rgba(255, 255, 255, 0.1);
            cursor: not-allowed;
        }

        /* Message Bubbles */
        .user-message {
            background: rgba(76, 151, 240, 0.8);
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            margin: 8px 0;
            max-width: 70%;
            float: right;
            clear: both;
        }
        .bot-message {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            margin: 8px 0;
            max-width: 70%;
            float: left;
            clear: both;
        }
        
        .chat-messages-wrap {
            padding-bottom: 120px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Chat Messages ---
    st.markdown('<div class="chat-messages-wrap">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

            # Also show DAG and results if available
            if "dag" in message and "results" in message:
                with st.expander("🔗 View Details"):
                    try:
                        graph = graphviz.Digraph(graph_attr={"rankdir": "LR"})
                        for node in message["dag"]["dag"]["nodes"]:
                            graph.node(node["id"], node["task"][:30] + "...")
                        for node in message["dag"]["dag"]["nodes"]:
                            if "depends_on" in node:
                                for dep in node["depends_on"]:
                                    graph.edge(dep, node["id"])
                        st.graphviz_chart(graph)
                    except Exception as e:
                        st.json(message["dag"]["dag"])
                    
                    st.json(message["results"])

    st.markdown('</div>', unsafe_allow_html=True)

    # --- Chatbox Input (Fixed at Bottom) ---
    st.markdown('<div class="chatbox">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 6, 1, 1])

    with col1:
        # File Upload Button (Hidden Uploader + Visible Icon)
        uploaded_file = st.file_uploader(
            "📎",
            type=["pdf", "jpg", "png", "jpeg"],
            key="chat_file_uploader",
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file

    with col2:
        # Text Input
        user_input = st.text_input(
            "Type your message...",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="Ask me anything..."
        )

    with col3:
        # Mic Button
        if st.button("🎤", key="mic_button", use_container_width=False):
            with st.spinner("Listening..."):
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    try:
                        audio = r.listen(source, timeout=10)
                        user_input = r.recognize_google(audio)
                    except:
                        user_input = None

    with col4:
        # Send Button
        send_disabled = not user_input and not st.session_state.get("uploaded_file")
        send_pressed = st.button("→", key="send_button", disabled=send_disabled, use_container_width=False)

    st.markdown('</div>', unsafe_allow_html=True)

    if (user_input or st.session_state.get("uploaded_file")) and (send_pressed or user_input):
        if st.session_state.get("uploaded_file"):
            file = st.session_state.uploaded_file
            if file.type.startswith("image/"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"![Uploaded Image]({file.name})",
                    "type": "image"
                })
            elif file.type == "application/pdf":
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"[Uploaded PDF: {file.name}]",
                    "type": "pdf"
                })
            st.session_state.uploaded_file = None

        if user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "type": "text"
            })
            
        st.rerun()

    # After the chatbox UI code above, process logic
    if st.session_state.get("uploaded_file"):
        uploaded_file = st.session_state.uploaded_file
        if uploaded_file.type.startswith("image/"):
            image = Image.open(uploaded_file)
            st.session_state.messages[-1]["content"] = f"![Uploaded Image]({uploaded_file.name})"
            # Process image (OCR, etc.)
            extracted_text = pytesseract.image_to_string(image)
            st.session_state.messages[-1]["content"] += f"\n\nExtracted Text: {extracted_text}"
        elif uploaded_file.type == "application/pdf":
            pdf_path = f"temp_{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            pdf_text = extract_text_from_pdf(pdf_path)
            st.session_state.messages[-1]["content"] = f"[Uploaded PDF: {uploaded_file.name}]\n\n{pdf_text[:1000]}..."

    # Process user input (your existing logic)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_message = st.session_state.messages[-1]["content"]
        if not user_message.startswith("[Uploaded") and not user_message.startswith("![Uploaded"):
            # Regular text prompt - execute as before
            route = st.selectbox("Route:", ["ODA", "Hybrid", "Cloud"], index=1, key="route")
            
            route_map = {
                "ODA": "ODA",
                "Hybrid": "Hybrid",
                "Cloud": "Cloud"
            }

            with st.spinner("Processing..."):
                start_time = datetime.now()
                log_entry = {
                    "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "prompt": user_message,
                    "route": route,
                    "status": "started",
                    "model": f"{route} (DistilBERT + Qwen/Grok)"
                }
                logger.log(log_entry)

                dag, results = orchestrator.execute(user_message, None, route_map[route])

                end_time = datetime.now()
                log_entry.update({
                    "status": "completed",
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "duration": str(end_time - start_time),
                    "dag": dag,
                    "results": results
                })
                logger.log(log_entry)

                st.session_state.messages.append({
                    "role": "bot",
                    "content": results.get("final_output", "No output generated."),
                    "dag": dag,
                    "results": results
                })
                st.rerun()

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
