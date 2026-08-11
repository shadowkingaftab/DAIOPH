import streamlit as st
from typing import List
import contextlib

class StreamHandler:
    def __init__(self):
        self.logs = []

    @contextlib.contextmanager
    def stream(self, message: str):
        """Stream a message to the UI (context manager for 'with' block)."""
        self.logs.append(message)
        placeholder = st.empty()
        placeholder.write(f"> {message}")
        try:
            yield
        finally:
            placeholder.empty()

    def get_logs(self) -> List[str]:
        """Return all logs."""
        return self.logs
