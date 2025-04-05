# services/generation_service.py

def generate_job_ad(job_details: dict) -> str:
    """
    Generate a job ad text from the dictionary of details in session.
    You can also pass this to an LLM for a more dynamic generation.
    """
    title = job_details.get("job_title", "Unknown Role")
    company = job_details.get("company_name", "Unknown Company")
    location = job_details.get("location", "")
    mission = job_details.get("company_mission", "")
    responsibilities = job_details.get("responsibility_distribution", [])
    tasks = job_details.get("tasks", [])
    benefits = job_details.get("benefits", [])
    salary = job_details.get("salary_range", "N/A")

    ad_text = f"**Join us at {company} as a {title} in {location}!**\n\n"
    if mission:
        ad_text += f"**Our Mission**: {mission}\n\n"
    if responsibilities:
        ad_text += "**Key Responsibilities:**\n"
        for r in responsibilities:
            ad_text += f"- {r}\n"
        ad_text += "\n"
    if tasks:
        ad_text += "**Core Tasks:**\n"
        for t in tasks:
            ad_text += f"- {t}\n"
        ad_text += "\n"
    if benefits:
        ad_text += "**Benefits & Perks:**\n"
        for b in benefits:
            ad_text += f"- {b}\n"
        ad_text += "\n"
    ad_text += f"**Salary Range**: {salary}\n\n"
    ad_text += "Apply now and be part of our team!"
    return ad_text

def generate_interview_guide(job_details: dict, audience: str = "HR") -> str:
    """
    Generate a simplistic interview guide. 
    Optionally feed job_details to an LLM for more advanced generation.
    """
    title = job_details.get("job_title", "Unknown Role")
    tasks = job_details.get("tasks", [])
    responsibilities = job_details.get("responsibility_distribution", [])
    guide = f"**Interview Guide for {title} (for {audience} Interviewers)**\n\n"
    guide += "Recommended focus areas:\n"
    if responsibilities:
        guide += "- Ask about top responsibilities and how the candidate's experience aligns.\n"
    if tasks:
        guide += "- Discuss how they would handle key tasks:\n"
        for t in tasks:
            guide += f"  • {t}\n"
    guide += "\nSample Questions:\n"
    guide += f"1. What attracts you to the {title} role?\n"
    guide += "2. Can you describe a recent challenge you faced and how you resolved it?\n"
    guide += f"3. Which of your skills directly map to the responsibilities for {title}?\n"
    return guide
