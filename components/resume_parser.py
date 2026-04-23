"""
resume_parser.py — Parses raw resume text into ResumeData using the chosen AI provider.
"""

import json
import streamlit as st

from models.resume_schema import ResumeData
from utils.prompt_templates import get_parse_prompt


def parse_resume(raw_text: str, provider=None) -> ResumeData | None:
    """
    Takes raw resume text and an AIProvider instance.
    Returns a populated ResumeData, or None on failure.
    """
    if not raw_text or not raw_text.strip():
        st.error("No resume text provided.")
        return None

    if provider is None:
        st.error("No AI provider configured. Choose a provider and add a key if needed.")
        return None

    with st.spinner(f"Analysing resume structure with {provider.name}…"):
        try:
            prompt = get_parse_prompt(raw_text)
            response_text = provider.complete(prompt)

            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]

            data_dict = json.loads(cleaned)
            return ResumeData.from_dict(data_dict)

        except json.JSONDecodeError as e:
            st.error(f"❌ AI returned invalid JSON. Try again. ({e})")
            with st.expander("Raw AI response (debug)"):
                st.code(response_text if 'response_text' in dir() else "no response", language="json")
            return None
        except Exception as e:
            st.error(f"❌ Parsing failed: {e}")
            return None
