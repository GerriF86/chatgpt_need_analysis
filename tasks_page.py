import streamlit as st
from utils.session_utils import init_session_state
from services.llm_service import LLMService
from utils.ui_utils import display_suggestions

# Initialize session state with required keys
init_session_state()

st.title("Job Description Wizard - Tasks")

# Ensure job title is provided
if not st.session_state.get("job_title"):
    st.text_input("Job Title", key="job_title", placeholder="Enter the job title")
    st.warning("Please enter a job title to proceed.")
    st.stop()

job_title = st.session_state["job_title"]
st.header(f"Define Key Tasks for the '{job_title}' Role")
st.write("List the main responsibilities or tasks for this position. You can also get AI-generated suggestions and add them to the list.")

# Tasks text input area (multi-line)
st.text_area("Tasks", key="tasks_text", height=200, placeholder="Enter one task per line")

# Sync the tasks list with the text area content
tasks_list = [line.strip() for line in st.session_state["tasks_text"].splitlines() if line.strip()]
st.session_state["tasks"] = tasks_list

# Button to get AI suggestions for tasks
if st.button("Get AI Task Suggestions"):
    # Initialize LLM service if not already done
    if "llm_service" not in st.session_state:
        # Check for configuration in Streamlit secrets (optional)
        openai_api_key = None
        local_model_path = None
        try:
            openai_api_key = st.secrets.get("openai_api_key", None)
            local_model_path = st.secrets.get("local_model_path", None)
        except AttributeError:
            # st.secrets might not exist
            pass
        try:
            if local_model_path:
                st.session_state.llm_service = LLMService(openai_api_key=openai_api_key, local_model=local_model_path)
            else:
                st.session_state.llm_service = LLMService(openai_api_key=openai_api_key)
        except Exception as e:
            st.error(f"Error initializing AI suggestion service: {e}")
    # Generate suggestions if service is available
    if "llm_service" in st.session_state:
        try:
            suggestions = st.session_state.llm_service.generate_suggestions(job_title, category="tasks", count=15)
            st.session_state["suggestions_tasks"] = suggestions
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")

# Display suggestions as buttons
display_suggestions("tasks")

# Navigation button to next page
next_col = st.columns([1, 1])[1]
if next_col.button("Next: Skills →"):
    try:
        st.switch_page("Skills")
    except Exception:
        st.markdown('<a href="/Skills" target="_self">Next: Skills →</a>', unsafe_allow_html=True)
