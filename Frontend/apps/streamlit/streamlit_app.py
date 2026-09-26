"""DAIOPH Streamlit Application - Main entry point."""

import streamlit as st
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from apps.streamlit.state import init_state, get_state
from apps.streamlit.session import SessionManager
from apps.streamlit.components import (
    render_sidebar,
    render_chat,
    render_analytics,
    render_logs,
    render_models,
)


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="DAIOPH Edge AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    init_state()
    state = get_state()

    # Initialize session manager
    session = SessionManager()

    # Render sidebar
    render_sidebar(state)

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat",
        "📊 Analytics",
        "📜 Logs",
        "🧠 Models",
    ])

    with tab1:
        render_chat(state, session)
    with tab2:
        render_analytics(state)
    with tab3:
        render_logs(state)
    with tab4:
        render_models(state)


if __name__ == "__main__":
    main()