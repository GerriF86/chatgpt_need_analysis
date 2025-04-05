import streamlit as st
from utils.session_utils import init_session_state
from services.llm_service import LLMService
from utils.ui_utils import display_suggestions

# Initialize session state
init_session_state()

st.title("Job Description Wizard - Skills")

# Ensure job title is provided
if not st.session_state.get("job_title"):
    st.text_input("Job Title", key="job_title", placeholder="Enter the job title")
    st.warning("Please enter a job title to proceed.")
    st.stop()

job_title = st.session_state["job_title"]
st.header(f"Define Key Skills for the '{job_title}' Role")
st.write("List the essential skills or qualifications required for this position. You can also get AI-generated suggestions and add them to the list.")

# Skills text input area
st.text_area("Skills", key="skills_text", height=200, placeholder="Enter one skill or qualification per line")

# Sync the skills list with the text area content
skills_list = [line.strip() for line in st.session_state["skills_text"].splitlines() if line.strip()]
st.session_state["skills"] = skills_list

# Button to get AI suggestions for skills
if st.button("Get AI Skill Suggestions"):
    if "llm_service" not in st.session_state:
        openai_api_key = None
        local_model_path = None
        try:
            openai_api_key = st.secrets.get("openai_api_key", None)
            local_model_path = st.secrets.get("local_model_path", None)
        except AttributeError:
            pass
        try:
            if local_model_path:
                st.session_state.llm_service = LLMService(openai_api_key=openai_api_key, local_model=local_model_path)
            else:
                st.session_state.llm_service = LLMService(openai_api_key=openai_api_key)
        except Exception as e:
            st.error(f"Error initializing AI suggestion service: {e}")
    if "llm_service" in st.session_state:
        try:
            suggestions = st.session_state.llm_service.generate_suggestions(job_title, category="skills", count=15)
            st.session_state["suggestions_skills"] = suggestions
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")

# Display suggestions as buttons
display_suggestions("skills")

# Navigation buttons (Previous and Next)
prev_col, next_col = st.columns([1, 1])
if prev_col.button("← Back to Tasks"):
    try:
        st.switch_page("Tasks")
    except Exception:
        st.markdown('<a href="/Tasks" target="_self">← Back to Tasks</a>', unsafe_allow_html=True)
if next_col.button("Next: Benefits →"):
    try:
        st.switch_page("Benefits")
    except Exception:
        st.markdown('<a href="/Benefits" target="_self">Next: Benefits →</a>', unsafe_allow_html=True)
