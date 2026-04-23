"""
validators.py — Input validation helpers used across the application.
"""

import re
from typing import Tuple

MAX_RESUME_TEXT_CHARS = 8_000


def validate_email(email: str) -> Tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    if not email:
        return True, ""  # Optional field
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email.strip()):
        return True, ""
    return False, "Invalid email address format."


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Returns (is_valid, error_message). Accepts common international formats."""
    if not phone:
        return True, ""
    cleaned = re.sub(r"[\s\-().+]", "", phone)
    if cleaned.isdigit() and 7 <= len(cleaned) <= 15:
        return True, ""
    return False, "Invalid phone number. Use digits, spaces, dashes, or parentheses."


def validate_linkedin_url(url: str) -> Tuple[bool, str]:
    """Validates that a LinkedIn URL looks plausible."""
    if not url:
        return True, ""
    pattern = r"^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?$"
    if re.match(pattern, url.strip()):
        return True, ""
    return False, "LinkedIn URL should look like: https://linkedin.com/in/your-name"


def validate_resume_text(text: str) -> Tuple[bool, str]:
    """Ensures pasted text is long enough to be a real resume."""
    if not text or not text.strip():
        return False, "Resume text cannot be empty."
    if len(text.strip()) < 100:
        return False, "Resume text seems too short. Please paste the full resume."
    if len(text.strip()) > MAX_RESUME_TEXT_CHARS:
        return False, f"Resume text is too long (max {MAX_RESUME_TEXT_CHARS:,} characters)."
    return True, ""


def validate_resume_data(data: dict) -> Tuple[bool, list]:
    """
    Cross-validates a full ResumeData dict.
    Returns (is_valid, list_of_warnings).
    Warnings don't block submission but are shown to the user.
    """
    warnings = []

    if not data.get("name", "").strip():
        warnings.append("Name is missing.")
    if not data.get("email", "").strip():
        warnings.append("Email is missing.")

    ok, msg = validate_email(data.get("email", ""))
    if not ok:
        warnings.append(msg)

    ok, msg = validate_phone(data.get("phone", ""))
    if not ok:
        warnings.append(msg)

    if not data.get("skills"):
        warnings.append("No skills listed — consider adding a skills section.")

    if not data.get("experience"):
        warnings.append("No work experience found.")

    return len(warnings) == 0, warnings
