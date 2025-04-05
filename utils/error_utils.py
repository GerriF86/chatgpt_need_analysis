# utils/error_utils.py
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def handle_error(error: Exception, context: str = ""):
    """
    Log the error and display a user-friendly message in Streamlit.
    """
    msg = f"Error in {context}: {error}" if context else f"Error: {error}"
    logger.error(msg)
    st.error(msg)
