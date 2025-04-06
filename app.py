import streamlit as st
from controllers import wizard_pages

# Configure the page
st.set_page_config(page_title="Job Analysis Wizard", layout="wide")
# Initialize session state variables to avoid KeyErrors
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'job_title' not in st.session_state:
    st.session_state.job_title = ""
# Text fields for wizard steps (store content as multi-line strings)
if 'tasks_text' not in st.session_state:
    st.session_state.tasks_text = ""
if 'skills_text' not in st.session_state:
    st.session_state.skills_text = ""
if 'benefits_text' not in st.session_state:
    st.session_state.benefits_text = ""
if 'job_ad_text' not in st.session_state:
    st.session_state.job_ad_text = ""
if 'interview_questions_text' not in st.session_state:
    st.session_state.interview_questions_text = ""
# Fields for source inputs on analysis page
for i in range(1, 4):
    key = f"source{i}"
    if key not in st.session_state:
        st.session_state[key] = ""
# Render the appropriate wizard page based on current section
wizard_pages.render_current_page()
