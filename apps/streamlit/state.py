"""Session state management for the DAIOPH Streamlit app."""

from typing import Any, Dict, List, Optional

import streamlit as st


def init_state() -> None:
    """Initialize all session state keys."""
    defaults: Dict[str, Any] = {
        "messages": [],
        "route": "Hybrid",
        "logs": [],
        "models": [],
        "api_key": "",
        "language": "en",
        "uploaded_file": None,
        "execution_count": 0,
        "total_time": 0.0,
        "success_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state() -> Dict[str, Any]:
    """Get the current session state as a dict.

    Returns:
        Dict[str, Any]: Session state values.
    """
    return {key: st.session_state[key] for key in st.session_state}


def set_state(key: str, value: Any) -> None:
    """Set a session state value.

    Args:
        key: State key.
        value: Value to set.
    """
    st.session_state[key] = value


def add_message(role: str, content: str, **kwargs: Any) -> None:
    """Add a message to the chat history.

    Args:
        role: Message role (user/assistant/system).
        content: Message content.
        **kwargs: Additional message metadata.
    """
    message = {"role": role, "content": content, **kwargs}
    st.session_state.messages.append(message)


def get_messages() -> List[Dict[str, Any]]:
    """Get all chat messages.

    Returns:
        List[Dict[str, Any]]: Chat messages.
    """
    return st.session_state.get("messages", [])


def clear_messages() -> None:
    """Clear all chat messages."""
    st.session_state.messages = []