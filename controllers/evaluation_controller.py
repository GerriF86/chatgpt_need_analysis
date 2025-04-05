# controllers/evaluation_controller.py

import streamlit as st
from utils.session_utils import get_from_session_state, store_in_state

def analyze_uploaded_sources():
    """
    Merge the uploaded file content (if any) and the provided URL,
    then auto-fill relevant fields in session state. 
    Example logic: simply store the combined text, or parse out job title, etc.
    """
    existing_content = get_from_session_state("uploaded_file","")
    input_url = get_from_session_state("input_url","")

    # Placeholder for scraping (if you'd like to do real URL scraping)
    # For now, we just store them in 'analyzed_job_content'.
    combined = existing_content
    if input_url and input_url.lower().startswith("http"):
        combined += f"\n(Demo) Additional text from URL: {input_url}"
    
    store_in_state("analyzed_job_content", combined)

    if combined.strip():
        st.success("Sources analyzed. Fields auto-filled where possible (demo).")
    else:
        st.warning("No content found to analyze from file or URL.")
