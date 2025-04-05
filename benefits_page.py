import streamlit as st
from utils.session_utils import init_session_state
from services.llm_service import LLMService
from utils.ui_utils import display_suggestions

# Initialize session state
init_session_state()

st.title("Job Description Wizard - Benefits")

# Ensure job title is provided
if not st.session_state.get("job_title"):
    st.text_input("Job Title", key="job_title", placeholder="Enter the job title")
    st.warning("Please enter a job title to proceed.")
    st.stop()

job_title = st.session_state["job_title"]
st.header(f"Define Key Benefits for the '{job_title}' Role")
st.write("List the benefits or perks offered for this position. You can also get AI-generated suggestions and add them to the list.")

# Benefits text input area
st.text_area("Benefits", key="benefits_text", height=200, placeholder="Enter one benefit or perk per line")

# Sync the benefits list with the text area content
benefits_list = [line.strip() for line in st.session_state["benefits_text"].splitlines() if line.strip()]
st.session_state["benefits"] = benefits_list

# Button to get AI suggestions for benefits
if st.button("Get AI Benefit Suggestions"):
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
            suggestions = st.session_state.llm_service.generate_suggestions(job_title, category="benefits", count=15)
            st.session_state["suggestions_benefits"] = suggestions
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")

# Display suggestions as buttons
display_suggestions("benefits")

# Navigation button (Previous only, last step of wizard)
if st.button("← Back to Skills"):
    try:
        st.switch_page("Skills")
    except Exception:
        st.markdown('<a href="/Skills" target="_self">← Back to Skills</a>', unsafe_allow_html=True)

# Completion message
st.success("You have completed all the steps of the wizard. You can now review all inputs and finalize the job description.")
