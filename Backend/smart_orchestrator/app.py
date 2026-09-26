import streamlit as st
import sys
import os

# Ensure the parent directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import LLMOrchestrator
from utils.visualizer import visualize_orchestration

st.set_page_config(page_title="Smart LLM Orchestrator", layout="wide")

# Ensure required secrets exist
if "GROK_API_KEY" not in st.secrets:
    st.error("GROK_API_KEY is missing from Streamlit secrets.")
    st.stop()

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    # We expect qwen-1_8b-chat-q4_k_m.gguf in the parent or current directory
    # Look in the main project folder
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(parent_dir, "qwen-1_8b-chat-q4_k_m.gguf")
    
    if not os.path.exists(model_path):
        # Fallback to local directory
        model_path = "qwen-1_8b-chat-q4_k_m.gguf"
        
    return LLMOrchestrator(
        qwen_model_path=model_path,
        grok_api_key=st.secrets["GROK_API_KEY"]
    )

try:
    orchestrator = get_orchestrator()
except Exception as e:
    st.error(f"Failed to load orchestrator: {e}")
    st.stop()

# UI
st.title("🤖 Smart LLM Orchestrator")
st.markdown("""
This system:
1. **Intelligently decomposes** complex prompts using Bartender
2. **Routes tasks** to optimal executors (on-device vs cloud)
3. **Shows the entire process** in real-time
4. **Handles failures gracefully**

Enter any complex prompt and see how it gets broken down and executed!
""")

# User input
user_prompt = st.text_area("Enter your complex prompt:", height=200, placeholder="Write a Python function to implement BERT and calculate its F1 score on the SST-2 dataset, then explain the architecture in simple terms.")

if st.button("Execute"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt")
    else:
        with st.spinner("Analyzing and executing..."):
            try:
                # Execute orchestration
                final_response, visualization_data = orchestrator.execute(user_prompt)

                # Display visualization
                st.subheader("🔍 Orchestration Process")
                visualize_orchestration(visualization_data)

                # Display final response
                st.subheader("💡 Final Response")
                st.write(final_response)

                # Performance metrics
                st.markdown("### ⚡ Performance Metrics")
                total_time = sum(
                    data.get('execution_time', 0)
                    for data in visualization_data['execution_plan']
                    if data['status'] == 'completed'
                )
                if total_time > 0:
                    st.metric("Total Execution Time", f"{total_time:.2f} seconds")
            except Exception as e:
                st.error(f"An error occurred during execution: {e}")
