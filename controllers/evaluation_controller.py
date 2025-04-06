# controllers/evaluation_controller.property

import streamlit as st
from utils.session_utils import get_from_session_state, store_in_state

def analyze_uploaded_sources():
    """
    Merge the uploaded file content (if any) with the provided URL content (if any),
    then auto-fill relevant fields in session state from the combined text.
    """
    # Retrieve uploaded file text and input URL from session
    file_text = get_from_session_state("uploaded_file", "")
    input_url = get_from_session_state("input_url", "")
    combined_text = file_text
    if input_url and input_url.lower().startswith("http"):
        # (Optional) In a real scenario, fetch URL content. Here, just note the URL.
        combined_text += f"\nAdditional context from URL: {input_url}\n"
    # Store combined content in session for reference
    store_in_state("analyzed_job_content", combined_text)
    # Auto-extract tasks (bullet points) from combined content as a demonstration
    if combined_text.strip():
        tasks_found = []
        for line in combined_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line[0] in ("-", "*", "•", "–") or line[:1].isdigit():
                # Treat lines starting with bullet or number as potential tasks
                cleaned = line.lstrip("-*•–0123456789. \t").strip()
                if cleaned:
                    tasks_found.append(cleaned)
        if tasks_found:
            # Remove duplicates while preserving order
            unique_tasks = list(dict.fromkeys(tasks_found))
            store_in_state("tasks", unique_tasks)
        st.success("Sources analyzed. Relevant fields auto-filled where possible.")
    else:
        st.warning("No content found to analyze from file or URL.")
