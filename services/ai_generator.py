# services/ai_generator.py


from typing import List, Dict, Optional

from services.llm_service import LLMService, create_llm_service

def generate_key_tasks(job_title: str, count: int = 15) -> List[str]:
    """
    Generate a list of key tasks or responsibilities for a given job title using AI.
    """
    llm = create_llm_service()  # Initialize LLM service (uses default or configured model)
    try:
        suggestions = llm.generate_suggestions(job_title=job_title, category="tasks", count=count)
    except Exception as e:
        raise RuntimeError(f"AI task suggestion generation failed: {e}")
    return suggestions

def generate_skills(job_title: str, count: int = 15) -> List[str]:
    """
    Generate a list of important skills needed for a given job title using AI.
    """
    llm = create_llm_service()
    try:
        suggestions = llm.generate_suggestions(job_title=job_title, category="skills", count=count)
    except Exception as e:
        raise RuntimeError(f"AI skill suggestion generation failed: {e}")
    return suggestions

def generate_benefits(job_title: str, count: int = 15) -> List[str]:
    """
    Generate a list of compelling benefits that could be offered for a given job title using AI.
    """
    llm = create_llm_service()
    try:
        suggestions = llm.generate_suggestions(job_title=job_title, category="benefits", count=count)
    except Exception as e:
        raise RuntimeError(f"AI benefit suggestion generation failed: {e}")
    return suggestions

def generate_job_ad(job_details: Dict) -> str:
    """
    Generate a job advertisement text from the provided job details.
    Combines fields like company, title, tasks, benefits, and salary into a formatted job ad string.
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

def generate_interview_questions(job_details: Dict, audience: str = "HR") -> str:
    """
    Generate an interview preparation guide (with sample questions) for a given role and audience.
    """
    title = job_details.get("job_title", "Unknown Role")
    tasks = job_details.get("tasks", [])
    responsibilities = job_details.get("responsibility_distribution", [])
    guide = f"**Interview Guide for {title} (Audience: {audience})**\n\n"
    guide += "Recommended focus areas:\n"
    if responsibilities:
        guide += "- Ask about top responsibilities and how the candidate's experience aligns.\n"
    if tasks:
        guide += "- Discuss how they would handle key tasks such as:\n"
        for t in tasks:
            guide += f"  • {t}\n"
    guide += "\nSample Interview Questions:\n"
    guide += f"1. What attracts you to the {title} role?\n"
    guide += "2. Can you describe a recent challenge you faced and how you resolved it?\n"
    guide += f"3. Which of your skills do you feel best align with the responsibilities of the {title} role?\n"
    return guide
