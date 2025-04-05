# utils/session_utils.py
import streamlit as st

def init_main_state():
    """
    Initialize main wizard control. 
    Call this in app.py to ensure 'current_section' is set.
    """
    if "current_section" not in st.session_state:
        st.session_state["current_section"] = 1

def store_in_state(key: str, value):
    """Set st.session_state[key] = value safely."""
    st.session_state[key] = value

def get_from_session_state(key: str, default=None):
    """Get st.session_state[key], or default if missing."""
    return st.session_state.get(key, default)
