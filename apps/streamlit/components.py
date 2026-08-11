"""UI components for the DAIOPH Streamlit app."""

from typing import Any, Dict

import streamlit as st

from apps.streamlit.state import add_message, get_messages, set_state


def render_sidebar(state: Dict[str, Any]) -> None:
    """Render the sidebar.

    Args:
        state: Session state dict.
    """
    with st.sidebar:
        st.markdown("## 🤖 DAIOPH")
        st.markdown("---")

        st.markdown("### 🔄 Route")
        route = st.selectbox(
            "Execution route:",
            ["Hybrid", "ODA", "Cloud"],
            index=0,
            key="route_select",
        )
        set_state("route", route)

        st.markdown("### 🔑 API Key")
        api_key = st.text_input(
            "Grok API key (optional):",
            type="password",
            value=state.get("api_key", ""),
            key="api_key_input",
        )
        if api_key:
            set_state("api_key", api_key)

        st.markdown("---")
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()


def render_chat(state: Dict[str, Any], session: Any) -> None:
    """Render the chat tab.

    Args:
        state: Session state dict.
        session: SessionManager instance.
    """
    st.markdown("## 💬 DAIOPH Chat")
    st.caption("Hybrid edge-cloud AI orchestration")

    # Display messages
    for msg in get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("route"):
                st.caption(f"Route: {msg['route']}")

    # Input
    prompt = st.chat_input("Type your message...")
    if prompt:
        add_message("user", prompt, route=state.get("route", "Hybrid"))

        with st.spinner("Processing..."):
            try:
                from core.hybrid_orchestrator import HybridOrchestrator

                orch = HybridOrchestrator(
                    distilbert_path="distilbert-base-uncased",
                    qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
                    grok_api_key=state.get("api_key") or None,
                )
                import time

                start = time.time()
                dag, results = orch.execute(prompt, None, state.get("route", "Hybrid"))
                latency = time.time() - start
                output = results.get("final_output", "No output generated.")

                session.record_execution(prompt, state.get("route", "Hybrid"), latency, output=output)

                add_message("assistant", output, route=state.get("route", "Hybrid"), dag=dag)
            except Exception as e:
                add_message("assistant", f"⚠️ Error: {str(e)}")
                session.record_execution(prompt, state.get("route", "Hybrid"), 0, status="error")

        st.rerun()


def render_analytics(state: Dict[str, Any]) -> None:
    """Render the analytics tab.

    Args:
        state: Session state dict.
    """
    st.markdown("## 📊 Analytics")

    metrics = state.get("metrics", {})
    if not metrics:
        st.info("Run some prompts to see analytics.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Executions", metrics.get("executions", 0))
    col2.metric("Avg Latency", f"{metrics.get('avg_latency', 0):.2f}s")
    col3.metric("Total Time", f"{metrics.get('total_latency', 0):.2f}s")
    col4.metric("Uptime", f"{metrics.get('uptime', 0)/60:.1f}m")

    routes = metrics.get("route_counts", {})
    if routes:
        st.markdown("### Route Usage")
        st.bar_chart(routes)


def render_logs(state: Dict[str, Any]) -> None:
    """Render the logs tab.

    Args:
        state: Session state dict.
    """
    st.markdown("## 📜 Logs")
    history = state.get("history", [])
    if not history:
        st.info("No execution logs yet.")
        return

    for record in reversed(history[-50:]):
        with st.expander(f"⚡ {record['prompt'][:50]} | {record['route']} | {record['latency']:.2f}s"):
            st.markdown(f"**Prompt:** {record['prompt']}")
            st.markdown(f"**Route:** {record['route']}")
            st.markdown(f"**Latency:** {record['latency']:.2f}s")
            st.markdown(f"**Status:** {record['status']}")
            st.markdown(f"**Output:** {record.get('output', '')[:500]}")


def render_models(state: Dict[str, Any]) -> None:
    """Render the models tab.

    Args:
        state: Session state dict.
    """
    st.markdown("## 🧠 Models")
    models = [
        {"name": "Qwen2-0.5B-Instruct GGUF", "type": "Local Edge", "status": "Available"},
        {"name": "DistilBERT-base-uncased", "type": "Local Classifier", "status": "Available"},
        {"name": "xAI Grok", "type": "Cloud", "status": "Available"},
    ]
    for model in models:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.markdown(f"**{model['name']}**")
            col2.markdown(model["type"])
            col3.markdown(f"✅ {model['status']}")
        st.divider()