import streamlit as st
from typing import List

def log_execution(logs: List[str]):
    """Display execution logs nicely."""
    for log in logs:
        st.text(log)
