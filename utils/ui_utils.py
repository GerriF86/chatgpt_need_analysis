# utils/ui_utils.py
import streamlit as st

def apply_base_styling():
    """
    Insert custom CSS or apply a general theme. 
    """
    st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        margin: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

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
