# utils/ui_utils.py

import base64
import streamlit as st
from pathlib import Path

def apply_base_styling():
    """
    Insert custom CSS or apply a general theme, including
    a conditional background image based on the wizard section.
    """

    # 1) Determine which image to use. If st.session_state["current_section"] == 1, pick image1, else image2.
    current_section = st.session_state.get("current_section", 1)

    if current_section == 1:
        image_path = Path("images/AdobeStock_258774440.jpeg")
    else:
        image_path = Path("images/AdobeStock_567681994.jpeg")

    # 2) Encode the selected image in base64 to embed in CSS
    try:
        with open(image_path, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode()
    except Exception as e:
        # Fallback if something goes wrong (e.g., file not found):
        print(f"Warning: Could not read {image_path}: {e}")
        encoded_image = ""

    # 3) Define our CSS: 
    # - Add an overlay so text is readable (optional)
    # - Use the .stApp selector to cover the entire Streamlit main area
    # - Use background-size: cover to scale or crop the image for a full-page background
    css_style = f"""
    <style>
    body {{
        font-family: 'Arial', sans-serif;
    }}
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.45), rgba(255,255,255,0.45)),
                    url("data:image/jpeg;base64,{encoded_image}") no-repeat center center fixed;
        background-size: cover;
    }}
    .stButton>button {{
        background-color: #4CAF50;
        color: white;
        margin: 3px;
    }}
    </style>
    """

    # 4) Inject the final style block
    st.markdown(css_style, unsafe_allow_html=True)

def show_sidebar_links():
    """Placeholder for any global nav or links in the sidebar."""
    st.sidebar.markdown("[Home](#)")
    st.sidebar.markdown("[Contact Us](#)")

def display_suggestions(session_key: str, existing_set: set = None, store_key: str = None):
    """
    Display AI suggestions as clickable buttons. 
    If a user clicks one, it's added to 'existing_set' (if provided) 
    and removed from the suggestion list in session.
    :param session_key: The session state key where suggestions are stored as a list of strings.
    :param existing_set: A set of existing items in the category (to add new suggestions to).
    :param store_key: The session state key (string) under which the final set is stored.
    """
    if session_key not in st.session_state or not st.session_state[session_key]:
        return
    suggestions = st.session_state[session_key]
    if not suggestions:
        return

    st.write("**AI Suggestions:**")
    cols = st.columns(3)
    for idx, suggestion in enumerate(list(suggestions)):
        col = cols[idx % 3]
        if col.button(f"➕ {suggestion}", key=f"{session_key}_sugg_btn_{idx}"):
            # Add suggestion to the existing set
            if existing_set is not None:
                existing_set.add(suggestion)
            # Remove from the suggestion list
            updated_sugg = list(suggestions)
            updated_sugg.pop(idx)
            st.session_state[session_key] = updated_sugg
            # Update the session store key if provided
            if store_key is not None and existing_set is not None:
                from utils.session_utils import store_in_state
                # Convert set back to list or string
                if isinstance(existing_set, set):
                    store_in_state(store_key, list(existing_set))
                else:
                    store_in_state(store_key, existing_set)
            st.experimental_rerun()
