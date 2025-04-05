import streamlit as st
from controllers.evaluation_controller import analyze_uploaded_sources
from utils.session_utils import store_in_state, get_from_session_state
from services.file_parser import parse_file
from utils.ui_utils import apply_base_styling, show_sidebar_links, display_suggestions
from services.ai_generator import generate_key_tasks, generate_skills, generate_benefits, generate_job_ad, generate_interview_questions

def start_discovery_page():
    """1) START DISCOVERY PAGE"""
    apply_base_styling()
    show_sidebar_links()
    # Model selection and configuration in sidebar
    if "llm_choice" not in st.session_state:
        st.session_state["llm_choice"] = "openai_3.5"
    st.sidebar.subheader("Model Choice")
    llm_options = ["local_llama", "openai_o3_mini", "openai_3.5"]
    chosen_model = st.sidebar.selectbox("Select LLM:", llm_options, index=llm_options.index(st.session_state["llm_choice"]))
    st.session_state["llm_choice"] = chosen_model
    current_temp = st.session_state.get("model_temperature", 0.2)
    st.session_state["model_temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, current_temp, 0.05)
    # Page header and introduction
    st.image("images/sthree.png", width=80)
    st.title("Vacalyser")
    st.markdown("""
**Enhancing hiring workflows** with intelligent suggestions and automations. By leveraging FAISS for semantic search and LLaMA/OpenAI for generative AI, we help teams fine-tune job postings and CVs efficiently, enabling better hiring outcomes.
    """)
    st.header(" Start Discovery")
    st.write("Enter a Job Title, optionally a link or an uploaded file. We'll auto-fill fields where possible.")
    # Inputs for job title, optional URL, and file upload
    default_url = get_from_session_state("input_url", "http://www.")
    col1, col2 = st.columns([1, 1])
    with col1:
        job_title = st.text_input("Enter a **Job Title**", get_from_session_state("job_title", ""))
        store_in_state("job_title", job_title)
        input_url = st.text_input(" Link to a Job Ad / Company Website", value=default_url)
        store_in_state("input_url", input_url)
    with col2:
        uploaded_file = st.file_uploader("Upload Job Ad (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file:
            try:
                file_text = parse_file(uploaded_file, file_name=uploaded_file.name)
                store_in_state("uploaded_file", file_text)
            except Exception as e:
                st.error(f"Failed to parse file: {e}")
    # Buttons to analyze sources or proceed
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Analyse Sources"):
            analyze_uploaded_sources()
    with c2:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def company_information_page():
    """2) COMPANY INFORMATION"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Company Information")
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
        st.info("You may specify an alternative arrangement if neither option is selected.")
    # Navigation buttons
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def department_information_page():
    """3) DEPARTMENT INFORMATION"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Department Information")
    dept_name = st.text_input("Department Name", get_from_session_state("department_name", ""))
    store_in_state("department_name", dept_name)
    dept_size = st.number_input("Team Size", value=get_from_session_state("team_size", 5), step=1)
    store_in_state("team_size", int(dept_size))
    colA, colB, colC = st.columns(3)
    with colA:
        need_name = st.text_input("Name (Hiring Need)", get_from_session_state("need_name", ""))
        store_in_state("need_name", need_name)
        need_email = st.text_input("E-Mail (Need)", get_from_session_state("need_email", ""))
        store_in_state("need_email", need_email)
    with colB:
        auth_name = st.text_input("Name (Authority)", get_from_session_state("authority_name", ""))
        store_in_state("authority_name", auth_name)
        auth_email = st.text_input("E-Mail (Authority)", get_from_session_state("authority_email", ""))
        store_in_state("authority_email", auth_email)
    with colC:
        money_name = st.text_input("Name (Budget Holder)", get_from_session_state("money_name", ""))
        store_in_state("money_name", money_name)
        money_email = st.text_input("E-Mail (Budget Holder)", get_from_session_state("money_email", ""))
        store_in_state("money_email", money_email)
    st.subheader("Documents / Requirements")
    doc_text = st.text_area("List of required documents for applying or internal approvals", 
                             get_from_session_state("required_documents", ""))
    store_in_state("required_documents", doc_text)
    # Navigation buttons
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def role_description_page():
    """4) ROLE DESCRIPTION"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Role Description")
    st.subheader("Why does this job exist?")
    reason = st.text_area("Primary reason or goal for this position", get_from_session_state("job_reason", ""))
    store_in_state("job_reason", reason)
    st.subheader("Top 3 Responsibilities")
    resp_text = st.text_area("List the top 3 responsibility areas for this role", 
                              get_from_session_state("responsibility_distribution", ""))
    resp_list = [r.strip() for r in resp_text.split("\n") if r.strip()]
    store_in_state("responsibility_distribution", resp_list)
    st.subheader("Key Challenges")
    challenges = st.text_area("Notable challenges of this role", get_from_session_state("job_challenges", ""))
    store_in_state("job_challenges", challenges)
    # Navigation buttons
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def task_scope_page():
    """5) TASK SCOPE"""
    apply_base_styling()
    show_sidebar_links()
    st.header("️ Task Scope")
    st.markdown("""
This page shows tasks auto-extracted from your file (if any) or from earlier steps. You can edit them, remove them, or add new ones. Additionally, you can retrieve task suggestions from an AI.
    """)
    # Display current tasks (from prior auto-fill or manual input)
    current_tasks = set(get_from_session_state("tasks", []))
    st.write("**Current Tasks (Auto-Filled or Manually Added):**")
    for t in list(current_tasks):
        colT1, colT2 = st.columns([4, 1])
        with colT1:
            st.write("-", t)
        with colT2:
            if st.button(f"Remove: {t}"):
                current_tasks.discard(t)
                store_in_state("tasks", list(current_tasks))
                st.experimental_rerun()
    new_task_val = st.text_input("Add Another Task:")
    if st.button("Add This Task"):
        if new_task_val.strip():
            current_tasks.add(new_task_val.strip())
            store_in_state("tasks", list(current_tasks))
            st.experimental_rerun()
    st.markdown("---")
    st.subheader("Retrieve Additional Tasks via AI")
    job_title = st.session_state.get("job_title", "Role")
    if st.button("Get 15 AI Suggestions for Tasks"):
        try:
            suggestions = generate_key_tasks(job_title, count=15)
            st.session_state["task_scope_suggestions"] = suggestions
            st.success(f"Fetched {len(suggestions)} AI suggestions.")
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")
    # Display AI task suggestions as clickable buttons (adding to tasks list)
    display_suggestions("task_scope_suggestions", current_tasks, store_key="tasks")
    st.markdown("---")
    st.subheader("Autonomy Level")
    auto_opts = ["Low", "Medium", "High"]
    c_auto = get_from_session_state("autonomy_level", "Medium")
    if c_auto not in auto_opts:
        c_auto = "Medium"
    chosen_auto = st.selectbox("Choose Autonomy Level for These Tasks", auto_opts, index=auto_opts.index(c_auto))
    store_in_state("autonomy_level", chosen_auto)
    # Navigation buttons
    cA, cB = st.columns([1, 1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def skills_competencies_page():
    """6) REQUIRED SKILLS & COMPETENCIES"""
    apply_base_styling()
    show_sidebar_links()
    st.header("️ Required Skills & Competencies")
    st.markdown("""
We can generate skills using AI suggestions, then categorize them as Must-Have or Nice-to-Have.
    """)
    # Initialize skill categories from session (stored as comma-separated strings)
    must_hard_raw = set(s.strip() for s in get_from_session_state("must_have_hard", "").split(",") if s.strip())
    must_soft_raw = set(s.strip() for s in get_from_session_state("must_have_soft", "").split(",") if s.strip())
    nice_hard_raw = set(s.strip() for s in get_from_session_state("nice_have_hard", "").split(",") if s.strip())
    nice_soft_raw = set(s.strip() for s in get_from_session_state("nice_have_soft", "").split(",") if s.strip())
    st.subheader("AI-Generated Skills")
    job_title = st.session_state.get("job_title", "Role")
    if st.button("Get 15 AI Skill Suggestions"):
        try:
            suggestions = generate_skills(job_title, count=15)
            st.session_state["skills_suggestions_key"] = suggestions
            # (Optional success message can be added if needed)
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")
    st.caption("Click a suggestion to add it to 'Must-Have Hard Skills' (you can reassign later).")
    suggestions = get_from_session_state("skills_suggestions_key", [])
    cols = st.columns(3)
    for idx, suggestion in enumerate(suggestions):
        col = cols[idx % 3]
        if col.button(f"➕ {suggestion}", key=f"skill_sugg_{idx}"):
            must_hard_raw.add(suggestion)
            # Remove added suggestion from the list
            updated_sugg = list(suggestions)
            updated_sugg.pop(idx)
            store_in_state("skills_suggestions_key", updated_sugg)
            store_in_state("must_have_hard", ", ".join(must_hard_raw))
            st.experimental_rerun()
    st.markdown("---")
    # Must-Have Hard Skills
    st.subheader("Must-Have Hard Skills")
    if must_hard_raw:
        st.caption("Click any skill to remove it.")
    for skill in list(must_hard_raw):
        if st.button(f"Remove '{skill}' from Must-Have Hard"):
            must_hard_raw.discard(skill)
            store_in_state("must_have_hard", ", ".join(must_hard_raw))
            st.experimental_rerun()
    new_must_hard = st.text_input("Add Hard Skill to Must-Have:")
    if st.button("Add Must-Have Hard"):
        if new_must_hard.strip():
            must_hard_raw.add(new_must_hard.strip())
            store_in_state("must_have_hard", ", ".join(must_hard_raw))
            st.experimental_rerun()
    st.markdown("---")
    # Must-Have Soft Skills
    st.subheader("Must-Have Soft Skills")
    if must_soft_raw:
        st.caption("Click any skill to remove it.")
    for skill in list(must_soft_raw):
        if st.button(f"Remove '{skill}' from Must-Have Soft"):
            must_soft_raw.discard(skill)
            store_in_state("must_have_soft", ", ".join(must_soft_raw))
            st.experimental_rerun()
    new_must_soft = st.text_input("Add Soft Skill to Must-Have:")
    if st.button("Add Must-Have Soft"):
        if new_must_soft.strip():
            must_soft_raw.add(new_must_soft.strip())
            store_in_state("must_have_soft", ", ".join(must_soft_raw))
            st.experimental_rerun()
    st.markdown("---")
    # Nice-to-Have Hard Skills
    st.subheader("Nice-to-Have Hard Skills")
    if nice_hard_raw:
        st.caption("Click any skill to remove it.")
    for skill in list(nice_hard_raw):
        if st.button(f"Remove '{skill}' from Nice-to-Have Hard"):
            nice_hard_raw.discard(skill)
            store_in_state("nice_have_hard", ", ".join(nice_hard_raw))
            st.experimental_rerun()
    new_nice_hard = st.text_input("Add Hard Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Hard"):
        if new_nice_hard.strip():
            nice_hard_raw.add(new_nice_hard.strip())
            store_in_state("nice_have_hard", ", ".join(nice_hard_raw))
            st.experimental_rerun()
    st.markdown("---")
    # Nice-to-Have Soft Skills
    st.subheader("Nice-to-Have Soft Skills")
    if nice_soft_raw:
        st.caption("Click any skill to remove it.")
    for skill in list(nice_soft_raw):
        if st.button(f"Remove '{skill}' from Nice-to-Have Soft"):
            nice_soft_raw.discard(skill)
            store_in_state("nice_have_soft", ", ".join(nice_soft_raw))
            st.experimental_rerun()
    new_nice_soft = st.text_input("Add Soft Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Soft"):
        if new_nice_soft.strip():
            nice_soft_raw.add(new_nice_soft.strip())
            store_in_state("nice_have_soft", ", ".join(nice_soft_raw))
            st.experimental_rerun()
    # Navigation buttons
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def benefits_compensation_page():
    """7) BENEFITS & COMPENSATION"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Benefits & Compensation")
    st.subheader("Salary Range")
    c1, c2 = st.columns(2)
    min_sal = get_from_session_state("min_salary", 50000)
    max_sal = get_from_session_state("max_salary", 70000)
    updated_min = c1.number_input("Minimum Salary (€)", value=min_sal, step=1000)
    updated_max = c2.number_input("Maximum Salary (€)", value=max_sal, step=1000)
    store_in_state("min_salary", updated_min)
    store_in_state("max_salary", updated_max)
    store_in_state("salary_range", f"{int(updated_min)}-{int(updated_max)}")
    st.subheader("Key Benefits")
    existing_benefits = set(get_from_session_state("benefits", []))
    job_title = st.session_state.get("job_title", "Role")
    if st.button("Get 15 AI Benefit Suggestions"):
        try:
            suggestions = generate_benefits(job_title, count=15)
            st.session_state["benefits_suggestions_key"] = suggestions
            st.success(f"Fetched {len(suggestions)} AI suggestions.")
        except Exception as e:
            st.error(f"Failed to get AI suggestions: {e}")
    new_benefit = st.text_input("Add a Benefit:")
    if st.button("Add Benefit"):
        if new_benefit.strip():
            existing_benefits.add(new_benefit.strip())
            store_in_state("benefits", list(existing_benefits))
    display_suggestions("benefits_suggestions_key", existing_benefits, store_key="benefits")
    if existing_benefits:
        st.write("**Selected Benefits:**", ", ".join(existing_benefits))
    st.subheader("Health Benefits")
    health_list = set(get_from_session_state("health_benefits", []))
    if st.button("Show Health Benefit Suggestions (Demo)"):
        try:
            suggestions = generate_benefits(job_title, count=10)
            st.session_state["health_suggestions_key"] = suggestions
            st.success(f"Fetched {len(suggestions)} suggestions.")
        except Exception as e:
            st.error(f"Failed to get suggestions: {e}")
    display_suggestions("health_suggestions_key", health_list, store_key="health_benefits")
    new_health = st.text_input("Add a Health Benefit:")
    if st.button("Add Health Benefit"):
        if new_health.strip():
            health_list.add(new_health.strip())
            store_in_state("health_benefits", list(health_list))
    if health_list:
        st.write("**Selected Health Benefits:**", ", ".join(health_list))
    st.subheader("Learning & Development Opportunities")
    lnd_list = set(get_from_session_state("learning_opportunities", []))
    if st.button("Show L&D Suggestions"):
        try:
            suggestions = generate_benefits(job_title, count=10)
            st.session_state["lnd_suggestions_key"] = suggestions
            st.success(f"Fetched {len(suggestions)} suggestions.")
        except Exception as e:
            st.error(f"Failed to get suggestions: {e}")
    display_suggestions("lnd_suggestions_key", lnd_list, store_key="learning_opportunities")
    new_lnd = st.text_input("Add an L&D Opportunity:")
    if st.button("Add L&D"):
        if new_lnd.strip():
            lnd_list.add(new_lnd.strip())
            store_in_state("learning_opportunities", list(lnd_list))
    if lnd_list:
        st.write("**Selected L&D Opportunities:**", ", ".join(lnd_list))
    # Navigation buttons
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def recruitment_process_page():
    """8) RECRUITMENT PROCESS"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Recruitment Process")
    stages = st.number_input("Number of Interview Stages/Rounds", value=get_from_session_state("interview_stages", 3), step=1)
    store_in_state("interview_stages", int(stages))
    timeline = st.text_input("Estimated Timeline (e.g., 6 weeks from posting to hire)", 
                              get_from_session_state("application_timeline", ""))
    store_in_state("application_timeline", timeline)
    notes = st.text_area("Additional Notes about the hiring process", get_from_session_state("process_notes", ""))
    store_in_state("process_notes", notes)
    # Navigation buttons
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.experimental_rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.experimental_rerun()

def summary_outputs_page():
    """9) SUMMARY & OUTPUTS"""
    apply_base_styling()
    show_sidebar_links()
    st.header(" Summary & Outputs")
    st.markdown("Review all inputs below and generate the final outputs.")
    # Display a summary of all inputs for review
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Position Overview")
        st.write("**Job Title**:", st.session_state.get("job_title", ""))
        st.write("**Company**:", st.session_state.get("company_name", ""))
        st.write("**Location**:", st.session_state.get("location", ""))
        st.write("**Department**:", st.session_state.get("department_name", ""))
        st.write("**Team Size**:", st.session_state.get("team_size", ""))
        st.write("**Key Responsibilities**:", st.session_state.get("responsibility_distribution", []))
        st.write("**Must-Have Hard Skills**:", st.session_state.get("must_have_hard", ""))
        st.write("**Must-Have Soft Skills**:", st.session_state.get("must_have_soft", ""))
        st.write("**Nice-to-Have Hard Skills**:", st.session_state.get("nice_have_hard", ""))
        st.write("**Nice-to-Have Soft Skills**:", st.session_state.get("nice_have_soft", ""))
        st.write("**Benefits**:", st.session_state.get("benefits", []))
    with c2:
        st.subheader("Role Description")
        st.write("**Reason for Role**:", st.session_state.get("job_reason", ""))
        st.write("**Top Responsibilities**:", st.session_state.get("responsibility_distribution", []))
        st.write("**Key Tasks**:", st.session_state.get("tasks", []))
        st.write("**Challenges**:", st.session_state.get("job_challenges", ""))
        st.subheader("Recruitment Process")
        st.write("**Interview Rounds**:", st.session_state.get("interview_stages", 0))
        st.write("**Timeline**:", st.session_state.get("application_timeline", ""))
    st.markdown("---")
    st.markdown("### Generate Outputs")
    colGen1, colGen2 = st.columns(2)
    job_ad_text = ""
    interview_guide_text = ""
    with colGen1:
        if st.button(" Generate Job Ad"):
            job_details = dict(st.session_state)
            job_ad_text = generate_job_ad(job_details)
            st.session_state["generated_job_ad"] = job_ad_text
            st.subheader("Generated Job Ad")
            st.write(job_ad_text)
    with colGen2:
        if st.button(" Generate Interview Guide"):
            job_details = dict(st.session_state)
            interview_guide_text = generate_interview_questions(job_details, "HR")
            st.session_state["generated_interview_guide"] = interview_guide_text
            st.subheader("Generated Interview Guide")
            st.write(interview_guide_text)
    st.info("You can return to previous sections to refine details before finalizing.")
    # Export/Share options
    st.markdown("---")
    st.subheader("Export or Share")
    # Retrieve generated content from session (if any)
    job_ad_text = st.session_state.get("generated_job_ad", "")
    interview_guide_text = st.session_state.get("generated_interview_guide", "")
    # Offer download buttons for the outputs
    if job_ad_text:
        st.download_button("Download Job Ad Text", job_ad_text, file_name="JobAd.txt")
    if interview_guide_text:
        st.download_button("Download Interview Guide", interview_guide_text, file_name="InterviewGuide.txt")
    # Simulate email sharing
    recipient = st.text_input("Recipient Email Address", "")
    if st.button("Simulate Send via Email"):
        if recipient:
            if job_ad_text or interview_guide_text:
                st.success(f"Simulated sending outputs to {recipient}.")
            else:
                st.warning("Please generate the content first before sending.")
        else:
            st.warning("Please provide a recipient email address.")
    # Back button to allow editing if needed
    if st.button("⬅ Back"):
        st.session_state["current_section"] -= 1
        st.experimental_rerun()
