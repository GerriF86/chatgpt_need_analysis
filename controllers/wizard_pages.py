# controllers/wizard_pages.py

import streamlit as st
import openai

from controllers.evaluation_controller import analyze_uploaded_sources

from services.file_parser  import parse_file, match_and_store_keys, SESSION_KEYS
from services.rag_service import RAGService, build_index, search
from services.llm_service import complete, generate_suggestions, _parse_suggestions_from_text, create_llm_service
from services.generation_service import generate_job_ad, generate_interview_guide
from services.ai_generator import generate_key_tasks, generate_skills, generate_benefits, generate_job_ad, generate_interview_questions

from utils.session_utils import store_in_state, init_main_state, get_from_session_state
from utils.ui_utils import apply_base_styling, show_sidebar_links, display_suggestions
from utils.misc_utils import safe_int, format_list_as_bullets, sanitize_text 
from utils.error_utils import handle_error



###############################################################################
# WIZARD ROUTING
###############################################################################

def render_current_page():
    """
    Determine and render the current page based on st.session_state["current_section"].
    Make sure init_main_state() is called in app.py before calling this function.
    """
    current_step = st.session_state["current_section"]

    # Adjust if you want 1-based steps. Here, we assume 1..9:
    if current_step == 1:
        start_discovery_page()
    elif current_step == 2:
        company_information_page()
    elif current_step == 3:
        department_information_page()
    elif current_step == 4:
        role_description_page()
    elif current_step == 5:
        task_scope_page()
    elif current_step == 6:
        skills_competencies_page()
    elif current_step == 7:
        benefits_compensation_page()
    elif current_step == 8:
        recruitment_process_page()
    elif current_step == 9:
        summary_outputs_page()
    else:
        # If somehow out of range, reset to the first page:
        st.session_state["current_section"] = 1
        st.experimental_rerun()

###############################################################################
# PAGE 1: Start Discovery
###############################################################################

def start_discovery_page():
    """ Wizard Page 1: Start Discovery. """
    apply_base_styling()
    show_sidebar_links()

    st.image("images/sthree.png", width=80)
    st.title("Vacalyser")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, world!"}]
    )

    print(response.choices[0].message.content)
    st.write(st.secrets["OPENAI_API_KEY"])  # temporary, just for checking
    st.markdown(
        "**Enhancing hiring workflows** with intelligent suggestions and automations. "
        "We help teams fine-tune job postings and CVs efficiently for better hiring outcomes."
    )

    st.header("1) Start Discovery")
    st.write(
        "Enter a **Job Title**, optionally a link or an uploaded file. We'll auto-fill fields "
        "where possible after analysis."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        # Basic data: job title & URL
        job_title_val = get_from_session_state("job_title", "")
        job_title = st.text_input("Enter a **Job Title**", value=job_title_val)
        store_in_state("job_title", job_title)

        default_url = get_from_session_state("input_url", "http://www.")
        input_url = st.text_input("🔗 Link to a Job Ad / Company Website", value=default_url)
        store_in_state("input_url", input_url)

    with col2:
        # File upload
        uploaded_file = st.file_uploader("Upload Job Ad (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file:
            try:
                content = parse_file(uploaded_file, file_name=uploaded_file.name)  # returns raw text
                store_in_state("uploaded_file", content)
                st.success("File uploaded and parsed successfully.")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

    # Buttons row
    c1, c2 = st.columns([1, 1])
    with c1:
        # "Analyse Sources" button
        if st.button("Analyse Sources"):
            try:
                # 1) Retrieve the text from session
                raw_text = get_from_session_state("uploaded_file", "")
                if not raw_text.strip():
                    st.warning("No file content found. Please upload a file first.")
                else:
                    # 2) Use match_and_store_keys to extract relevant fields (company_name, job_title, etc.)
                    match_and_store_keys(raw_text, SESSION_KEYS)
                    st.success("Keys extracted successfully from the uploaded file.")
            except Exception as err:
                st.error(f"Analysis failed: {err}")
            else:
                # Optional: remain on this page or navigate
                st.experimental_rerun()

    with c2:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 2: Company Information
###############################################################################

def company_information_page():
    """ Wizard Page 2: Company Information """
    apply_base_styling()
    show_sidebar_links()

    st.header("2) Information about")
    st.write("Company:", st.session_state.get("company_name"))


    company_name = st.text_input("Company Name", get_from_session_state("company_name", ""))
    store_in_state("company_name", company_name)

    loc_val = get_from_session_state("location", "Düsseldorf, Germany")
    location_input = st.text_input("Location", loc_val)
    store_in_state("location", location_input)

    colA, colB = st.columns([1, 1])
    with colA:
        place_of_work = st.checkbox("Is this the actual place of work?", value=True)
    with colB:
        fully_remote = st.checkbox("Alternatively 100% remote?", value=False)
    store_in_state("place_of_work_confirmed", place_of_work)
    store_in_state("fully_remote", fully_remote)

    if not place_of_work and not fully_remote:
        alt_work = st.text_input("Please provide the actual address of place of work", "")
        store_in_state("alternate_work_address", alt_work)

    web_default = get_from_session_state("company_website", "https://www.")
    website = st.text_input("Company Website / Social Media Links", web_default)
    store_in_state("company_website", website)

    if st.button("Scrape Website for Mission & Vision"):
        # placeholder scraping logic
        found_mission = "(Demo) Discovered mission statement from website scraping."
        store_in_state("company_mission", found_mission)
        st.info("Mission & Vision updated from website scraping (demo).")

    # Industry + Company Size
    top10_inds = [
        "Automotive", "Consulting", "E-Commerce", "Education", "Finance",
        "Healthcare", "Manufacturing", "Retail", "Technology", "Tourism"
    ]
    stored_ind = get_from_session_state("industry", "")
    sorted_inds = sorted(top10_inds)
    idx_ind = 0
    if stored_ind in sorted_inds:
        idx_ind = sorted_inds.index(stored_ind)
    chosen_ind = st.selectbox("Industry / Sector", sorted_inds, index=idx_ind)
    store_in_state("industry", chosen_ind)

    size_opts = ["Small (<50)", "Medium (50-500)", "Large (>500)"]
    st_size = get_from_session_state("company_size", "Small (<50)")
    if st_size not in size_opts:
        st_size = "Small (<50)"
    chosen_size = st.selectbox("Company Size", size_opts, index=size_opts.index(st_size))
    store_in_state("company_size", chosen_size)

    # Mission & Vision
    mission_txt = st.text_area("Mission & Vision", get_from_session_state("company_mission", ""))
    store_in_state("company_mission", mission_txt)

    # Back/Next
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back (Start)"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 3: Department Information
###############################################################################

def department_information_page():
    """ Wizard Page 3: Department Information """
    apply_base_styling()
    show_sidebar_links()

    st.header("3) Department Information")

    dept = st.text_input("Department Name", get_from_session_state("department", ""))
    store_in_state("department", dept)

    tm_val = get_from_session_state("team_size", 0)
    new_team_size = st.number_input("Team Size in this Department", value=int(tm_val), min_value=0)
    store_in_state("team_size", new_team_size)

    dspv = st.text_input("Direct Supervisor (Full Name)", get_from_session_state("direct_supervisor", ""))
    store_in_state("direct_supervisor", dspv)

    dspv_email = st.text_input("Supervisor E-Mail", get_from_session_state("supervisor_email", ""))
    store_in_state("supervisor_email", dspv_email)

    dept_strat = st.text_area(
        "Department Strategy / Future Plans",
        get_from_session_state("department_strategy", "")
    )
    store_in_state("department_strategy", dept_strat)

    dept_challenge = st.text_area(
        "Challenges / Problems within Department/Team",
        get_from_session_state("department_challenges", "")
    )
    store_in_state("department_challenges", dept_challenge)

    # Technologies
    st.subheader("Technologies / Software Commonly Used")
    recommended_techs = [
        "Python", "Java", "JavaScript", "React", "Angular", "SQL", "NoSQL", "AWS",
        "Azure", "Docker", "Kubernetes", "Salesforce", "SAP", "Tableau", "PowerBI"
    ]
    st.caption("Click any that apply; you can also add your own below.")
    stored_techs = set(get_from_session_state("technologies_used", []))
    col_techs = st.columns(5)
    for i, tech in enumerate(recommended_techs):
        cidx = i % 5
        if col_techs[cidx].button(tech):
            stored_techs.add(tech)

    manual_tech = st.text_input("Add Another Technology:")
    if st.button("Add Technology"):
        if manual_tech.strip():
            stored_techs.add(manual_tech.strip())

    store_in_state("technologies_used", list(stored_techs))
    if stored_techs:
        st.write("**Currently Selected Technologies:**", ", ".join(stored_techs))

    # Culture / Collaborations
    c_opts = ["Agile", "Hierarchical", "Cross-functional", "Startup Mindset", "Other"]
    cur_cult = get_from_session_state("department_culture", "Agile")
    if cur_cult not in c_opts:
        cur_cult = "Agile"
    chosen_culture = st.selectbox("Department Culture / Environment", c_opts, index=c_opts.index(cur_cult))
    store_in_state("department_culture", chosen_culture)

    collab_opts = ["Finance", "HR", "Marketing", "IT", "Legal", "External Vendors"]
    def_collabs = get_from_session_state("department_collaborations", [])
    chosen_collabs = st.multiselect("Key Collaborations with Other Departments", collab_opts, default=def_collabs)
    store_in_state("department_collaborations", chosen_collabs)

    # Next/Back
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 4: Role Description
###############################################################################

def role_description_page():
    """ Wizard Page 4: Role Description """
    apply_base_styling()
    show_sidebar_links()

    st.header("4) Role Description")

    # Reason for Hiring
    st.write("**Reason for Hiring** (check all that apply):")
    reason_opts = ["New Role", "Growth", "Replacement", "Project-based"]
    current_reason = set(get_from_session_state("job_reason", []))
    new_set = []
    for r in reason_opts:
        checked = (r in current_reason)
        val = st.checkbox(r, value=checked, key=f"cb_{r}")
        if val:
            new_set.append(r)
    store_in_state("job_reason", new_set)

    # Responsibilities
    st.subheader("Key Responsibilities / Accountabilities")
    existing_resps = set(get_from_session_state("responsibility_distribution", []))

    if st.button("AI: Generate Responsibilities"):
        if st.session_state["job_title"].strip():
            try:
                # Use generate_key_tasks (or a dedicated function) if you want separate responsibilities
                suggestions = generate_key_tasks(st.session_state["job_title"], count=8)
                # Add to existing, remove duplicates
                for item in suggestions:
                    existing_resps.add(item)
                store_in_state("responsibility_distribution", list(existing_resps))
            except Exception as e:
                st.error(f"Failed to generate responsibilities: {e}")
        else:
            st.warning("Please provide a job title first.")

    new_resp = st.text_input("Add a Responsibility/Accountability:")
    if st.button("Add Responsibility"):
        if new_resp.strip():
            existing_resps.add(new_resp.strip())
            store_in_state("responsibility_distribution", list(existing_resps))
            st.experimental_rerun()

    if existing_resps:
        st.write("**Currently Selected Responsibilities:**")
        for r in existing_resps:
            st.markdown(f"- {r}")

    # Core Tasks
    st.subheader("Core Tasks or Duties")
    existing_tasks = set(get_from_session_state("tasks", []))

    if st.button("AI: Generate Tasks"):
        if st.session_state["job_title"].strip():
            try:
                tasks_found = generate_key_tasks(st.session_state["job_title"], count=8)
                for tsk in tasks_found:
                    existing_tasks.add(tsk)
                store_in_state("tasks", list(existing_tasks))
            except Exception as e:
                st.error(f"Failed to generate tasks: {e}")
        else:
            st.warning("Please provide a job title first.")

    new_task = st.text_input("Add a Task/Duty:")
    if st.button("Add Task"):
        if new_task.strip():
            existing_tasks.add(new_task.strip())
            store_in_state("tasks", list(existing_tasks))
            st.experimental_rerun()

    if existing_tasks:
        st.write("**Currently Selected Tasks:**")
        for t in existing_tasks:
            st.markdown(f"- {t}")

    # Challenges
    st.subheader("Typical Challenges in This Role")
    existing_challenges = set(get_from_session_state("job_challenges", []))

    # If you want AI for challenges, call a relevant generator or handle differently.
    new_chal = st.text_input("Add a Challenge:")
    if st.button("Add Challenge"):
        if new_chal.strip():
            existing_challenges.add(new_chal.strip())
            store_in_state("job_challenges", list(existing_challenges))
            st.experimental_rerun()

    if existing_challenges:
        st.write("**Currently Selected Challenges:**")
        for c in existing_challenges:
            st.markdown(f"- {c}")

    st.markdown("---")
    st.subheader("Travel & Remote Requirements")

    travel_opts = ["None", "Occasional", "Frequent"]
    cur_travel = get_from_session_state("travel_required_flag", "None")
    if cur_travel not in travel_opts:
        cur_travel = "None"
    chosen_travel = st.selectbox("Is Travel Required?", travel_opts, index=travel_opts.index(cur_travel))
    store_in_state("travel_required_flag", chosen_travel)

    if chosen_travel != "None":
        travel_details = st.text_area(
            "Travel Details (frequency, locations, purpose)",
            get_from_session_state("travel_required", "")
        )
        store_in_state("travel_required", travel_details)
    else:
        store_in_state("travel_required", "")

    remote_opts = ["None (on-site)", "Partial (hybrid)", "Fully Remote"]
    cur_remote = get_from_session_state("remote_policy", "None (on-site)")
    if cur_remote not in remote_opts:
        cur_remote = "None (on-site)"
    chosen_remote = st.selectbox(
        "Remote / Hybrid Work Policy",
        remote_opts,
        index=remote_opts.index(cur_remote)
    )
    store_in_state("remote_policy", chosen_remote)

    # Navigation
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 5: Task Scope
###############################################################################

def task_scope_page():
    """ Wizard Page 5: Task Scope """
    apply_base_styling()
    show_sidebar_links()

    st.header("5) Task Scope")
    st.markdown(
        "This page shows tasks auto-extracted or AI-generated. "
        "You can edit them, remove them, or add new ones."
    )

    current_tasks = get_from_session_state("tasks", [])
    updated_tasks = set(current_tasks)

    st.write("**Current Tasks:**")
    for t in current_tasks:
        colT1, colT2 = st.columns([4, 1])
        with colT1:
            st.write("- ", t)
        with colT2:
            if st.button(f"Remove {t}"):
                updated_tasks.discard(t)
                store_in_state("tasks", list(updated_tasks))
                st.experimental_rerun()

    new_task_val = st.text_input("Add Another Task:")
    if st.button("Add This Task"):
        if new_task_val.strip():
            updated_tasks.add(new_task_val.strip())
            store_in_state("tasks", list(updated_tasks))
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("Autonomy Level")
    auto_opts = ["Low", "Medium", "High"]
    c_auto = get_from_session_state("autonomy_level", "Medium")
    if c_auto not in auto_opts:
        c_auto = "Medium"
    chosen_auto = st.selectbox("Choose Autonomy Level", auto_opts, index=auto_opts.index(c_auto))
    store_in_state("autonomy_level", chosen_auto)

    # Navigation
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 6: Skills & Competencies
###############################################################################

def skills_competencies_page():
    """ Wizard Page 6: Required Skills & Competencies """
    apply_base_styling()
    show_sidebar_links()

    st.header("6) Required Skills & Competencies")
    st.markdown(
        "We can parse skills from the uploaded data or generate them via AI. "
        "You can separate them into Must-Have vs. Nice-to-Have, Hard vs. Soft, etc."
    )

    must_hard_raw = set(
        s.strip() for s in get_from_session_state("must_have_hard", "").split(",") if s.strip()
    )
    must_soft_raw = set(
        s.strip() for s in get_from_session_state("must_have_soft", "").split(",") if s.strip()
    )
    nice_hard_raw = set(
        s.strip() for s in get_from_session_state("nice_have_hard", "").split(",") if s.strip()
    )
    nice_soft_raw = set(
        s.strip() for s in get_from_session_state("nice_have_soft", "").split(",") if s.strip()
    )

    st.write("**AI-Generated Skills**")
    if st.button("Generate Skills via AI"):
        job_title = st.session_state.get("job_title", "")
        if not job_title:
            st.warning("Please specify the Job Title first.")
        else:
            try:
                # generate_skills can take job_title and an optional count
                suggestions = generate_skills(job_title, count=10)
                st.info("Click below to add them to Must-Have Hard Skills. You can reclassify them later.")
                for idx, skill in enumerate(suggestions):
                    if st.button(f"Add '{skill}' to Must-Have Hard", key=f"ai_skill_{idx}"):
                        must_hard_raw.add(skill.strip())
                        store_in_state("must_have_hard", ", ".join(must_hard_raw))
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to generate skills: {e}")

    st.markdown("---")
    # Must-Have Hard
    st.subheader("Must-Have Hard Skills")
    show_skill_list(must_hard_raw, "must_have_hard", "Remove from Must-Have Hard")
    new_mhh = st.text_input("Add Hard Skill to Must-Have:")
    if st.button("Add Must-Have Hard"):
        if new_mhh.strip():
            must_hard_raw.add(new_mhh.strip())
            store_in_state("must_have_hard", ", ".join(must_hard_raw))
            st.experimental_rerun()

    # Must-Have Soft
    st.subheader("Must-Have Soft Skills")
    show_skill_list(must_soft_raw, "must_have_soft", "Remove from Must-Have Soft")
    new_mhs = st.text_input("Add Soft Skill to Must-Have:")
    if st.button("Add Must-Have Soft"):
        if new_mhs.strip():
            must_soft_raw.add(new_mhs.strip())
            store_in_state("must_have_soft", ", ".join(must_soft_raw))
            st.experimental_rerun()

    # Nice-to-Have Hard
    st.subheader("Nice-to-Have Hard Skills")
    show_skill_list(nice_hard_raw, "nice_have_hard", "Remove from Nice-to-Have Hard")
    new_nhh = st.text_input("Add Hard Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Hard"):
        if new_nhh.strip():
            nice_hard_raw.add(new_nhh.strip())
            store_in_state("nice_have_hard", ", ".join(nice_hard_raw))
            st.experimental_rerun()

    # Nice-to-Have Soft
    st.subheader("Nice-to-Have Soft Skills")
    show_skill_list(nice_soft_raw, "nice_have_soft", "Remove from Nice-to-Have Soft")
    new_nhs = st.text_input("Add Soft Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Soft"):
        if new_nhs.strip():
            nice_soft_raw.add(new_nhs.strip())
            store_in_state("nice_have_soft", ", ".join(nice_soft_raw))
            st.experimental_rerun()

    # Back/Next
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def show_skill_list(skill_set, store_key, remove_label):
    """Helper to display each skill as a removable button."""
    if skill_set:
        st.caption(f"Click to remove from {store_key}")
        for skill in list(skill_set):
            if st.button(f"Remove '{skill}'", key=f"remove_{skill}_{store_key}"):
                skill_set.discard(skill)
                store_in_state(store_key, ", ".join(skill_set))
                st.experimental_rerun()
        st.write("**Current list:**", ", ".join(skill_set))


###############################################################################
# PAGE 7: Benefits & Compensation
###############################################################################

def benefits_compensation_page():
    """ Wizard Page 7: Benefits & Compensation """
    apply_base_styling()
    show_sidebar_links()

    st.header("7) Benefits & Compensation")

    st.subheader("Salary Range")
    min_sal = get_from_session_state("min_salary", 50000)
    max_sal = get_from_session_state("max_salary", 70000)
    c1, c2 = st.columns(2)
    with c1:
        updated_min = c1.number_input("Minimum Salary (€)", value=min_sal, step=1000)
    with c2:
        updated_max = c2.number_input("Maximum Salary (€)", value=max_sal, step=1000)
    store_in_state("min_salary", updated_min)
    store_in_state("max_salary", updated_max)
    store_in_state("salary_range", f"{updated_min}-{updated_max}")

    st.subheader("Key Benefits")
    benefits_list = set(get_from_session_state("benefits", []))

    if st.button("AI: Generate Benefits"):
        job_title = st.session_state.get("job_title", "")
        if not job_title:
            st.warning("Please provide Job Title to generate relevant benefits.")
        else:
            try:
                suggestions = generate_benefits(job_title, count=10)
                for s in suggestions:
                    benefits_list.add(s)
                store_in_state("benefits", list(benefits_list))
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to generate benefits: {e}")

    new_ben = st.text_input("Add a Benefit:")
    if st.button("Add Benefit"):
        if new_ben.strip():
            benefits_list.add(new_ben.strip())
            store_in_state("benefits", list(benefits_list))
            st.experimental_rerun()

    if benefits_list:
        st.write("**Selected Benefits:**", ", ".join(benefits_list))

    # Additional categories can be placed here (Health, L&D, etc.)

    # Next/Back
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 8: Recruitment Process
###############################################################################

def recruitment_process_page():
    """ Wizard Page 8: Recruitment Process """
    apply_base_styling()
    show_sidebar_links()

    st.header("8) Recruitment Process")
    st.markdown(
        "Define your entire recruitment flow, from initial approvals to final hiring steps."
    )

    st.subheader("Internal Contacts (Need / Authority / Budget)")

    cA, cB, cC = st.columns(3)
    with cA:
        need_name = st.text_input("Name (Need)", get_from_session_state("need_name", ""))
        store_in_state("need_name", need_name)
        need_email = st.text_input("E-Mail (Need)", get_from_session_state("need_email", ""))
        store_in_state("need_email", need_email)
    with cB:
        auth_name = st.text_input("Name (Authority)", get_from_session_state("authority_name", ""))
        store_in_state("authority_name", auth_name)
        auth_email = st.text_input("E-Mail (Authority)", get_from_session_state("authority_email", ""))
        store_in_state("authority_email", auth_email)
    with cC:
        money_name = st.text_input("Name (Budget Holder)", get_from_session_state("money_name", ""))
        store_in_state("money_name", money_name)
        money_email = st.text_input("E-Mail (Budget Holder)", get_from_session_state("money_email", ""))
        store_in_state("money_email", money_email)

    st.subheader("Documents / Requirements")
    doc_text = st.text_area(
        "List of required documents (CV, references, approvals, etc.)",
        get_from_session_state("required_documents", "")
    )
    store_in_state("required_documents", doc_text)

    st.subheader("Approvals & Mail Loops")
    approval_text = st.text_area(
        "Who must approve and at which stages?",
        get_from_session_state("approval_flow", "")
    )
    store_in_state("approval_flow", approval_text)

    st.subheader("Interview Process & Timeline")
    iv_num = get_from_session_state("interview_stages", 0)
    updated_iv = st.number_input("Number of Interview Rounds", min_value=0, value=iv_num)
    store_in_state("interview_stages", updated_iv)

    timeline_val = get_from_session_state("application_timeline", "")
    updated_timeline = st.text_input("Application / Hiring Timeline", timeline_val)
    store_in_state("application_timeline", updated_timeline)

    # Next/Back
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()


###############################################################################
# PAGE 9: Summary & Outputs
###############################################################################

def summary_outputs_page():
    """ Wizard Page 9: Summary & Outputs """
    apply_base_styling()
    show_sidebar_links()

    st.header("9) Final Summary & Outputs")
    st.markdown(
        "Review all key fields. You can go back to any step to revise, or generate final outputs below."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("General")
        st.write("**Job Title**:", get_from_session_state("job_title", "Not provided"))
        st.write("**Company Name**:", get_from_session_state("company_name", ""))
        st.write("**Location**:", get_from_session_state("location", ""))
        st.write("**Website**:", get_from_session_state("company_website", ""))
        st.write("**Industry**:", get_from_session_state("industry", ""))
        st.write("**Department**:", get_from_session_state("department", ""))
        st.write("**Team Size**:", get_from_session_state("team_size", 0))
        st.write("**Direct Supervisor**:", get_from_session_state("direct_supervisor", ""))

        st.subheader("Compensation & Benefits")
        st.write("**Salary Range**:", get_from_session_state("salary_range", "Not specified"))
        st.write("**Key Benefits**:", get_from_session_state("benefits", []))

    with c2:
        st.subheader("Role Description")
        st.write("**Reasons**:", get_from_session_state("job_reason", []))
        st.write("**Responsibilities**:", get_from_session_state("responsibility_distribution", []))
        st.write("**Tasks**:", get_from_session_state("tasks", []))
        st.write("**Challenges**:", get_from_session_state("job_challenges", []))
        st.subheader("Recruitment Process")
        st.write("**Interview Rounds**:", get_from_session_state("interview_stages", 0))
        st.write("**Timeline**:", get_from_session_state("application_timeline", ""))

    st.markdown("---")
    st.markdown("### Generate Outputs")

    colGen1, colGen2 = st.columns(2)
    with colGen1:
        if st.button("🎯 Generate Job Ad"):
            job_details = dict(st.session_state)
            try:
                job_ad = generate_job_ad(job_details)
                st.subheader("Generated Job Ad")
                st.write(job_ad)
            except Exception as e:
                st.error(f"Failed to generate job ad: {e}")

    with colGen2:
        if st.button("📝 Generate Interview Guide"):
            job_details = dict(st.session_state)
            try:
                guide = generate_interview_questions(job_details, audience="HR")
                st.subheader("Interview Preparation Guide")
                st.write(guide)
            except Exception as e:
                st.error(f"Failed to generate interview questions: {e}")

    st.info("You can always return to previous sections to refine details.")

    if st.button("⬅ Back"):
        st.session_state["current_section"] -= 1
        st.experimental_rerun()