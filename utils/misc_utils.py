from typing import List

def format_list_as_bullets(items: List[str]) -> str:
    """
    Format a list of strings as a bullet-point list.
    :param items: List of strings.
    :return: A single string with each item on a new line prefixed by a bullet.
    """
    return "\n".join(f"- {item}" for item in items)

def sanitize_text(text: str) -> str:
    """
    Basic text sanitization: trims and normalizes whitespace.
    :param text: Input text.
    :return: Sanitized text.
    """
    return " ".join(text.split()).strip()

def safe_int(val, default=0):
    try:
        return int(val)
    except:
        return default