#main
# app.py

import streamlit as st
import openai
import requests
from controllers import wizard_pages
from utils.session_utils import init_main_state

def main():
    st.set_page_config(page_title="Vacalyser Wizard", layout="wide")

    # Ensure we have essential session keys ready
    init_main_state()  # sets "current_section", etc., if not already set

    step = st.session_state["current_section"]

    if step == 1:
        wizard_pages.start_discovery_page()
    elif step == 2:
        wizard_pages.company_information_page()
    elif step == 3:
        wizard_pages.department_information_page()
    elif step == 4:
        wizard_pages.role_description_page()
    elif step == 5:
        wizard_pages.task_scope_page()
    elif step == 6:
        wizard_pages.skills_competencies_page()
    elif step == 7:
        wizard_pages.benefits_compensation_page()
    elif step == 8:
        wizard_pages.recruitment_process_page()
    elif step == 9:
        wizard_pages.summary_outputs_page()
    else:
        st.warning("Invalid section. Resetting to section 1.")
        st.session_state["current_section"] = 1
        st.experimental_rerun()

if __name__ == "__main__":
    main()
