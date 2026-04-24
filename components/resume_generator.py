"""
resume_generator.py — Template preview, AI enhancement, job tailoring, and PDF/text export.
"""

from __future__ import annotations
import json
import hashlib
import streamlit as st
import streamlit.components.v1 as components

from models.resume_schema import ResumeData
from utils.prompt_templates import get_improve_prompt, get_job_tailor_prompt
from utils.resume_templates import TEMPLATES, render_template
from utils.pdf_export import html_to_pdf
from utils.rate_limiter import check_limit, increment


# ─────────────────────────────────────────────────────────────────────────────
# Plain-text formatter
# ─────────────────────────────────────────────────────────────────────────────

def format_resume_as_text(resume: ResumeData) -> str:
    lines = []
    if resume.name:
        lines += [resume.name.upper(), "=" * len(resume.name)]
    contact = [p for p in [resume.email, resume.phone, resume.location, resume.linkedin, resume.website] if p]
    if contact:
        lines.append(" | ".join(contact))
    lines.append("")
    if resume.summary:
        lines += ["PROFESSIONAL SUMMARY", "-" * 20, resume.summary, ""]
    if resume.skills:
        lines += ["SKILLS", "-" * 20, ", ".join(resume.skills), ""]
    if resume.experience:
        lines += ["WORK EXPERIENCE", "-" * 20]
        for exp in resume.experience:
            date_str = " - ".join(filter(None, [exp.start_date, exp.end_date]))
            loc = f"  |  {exp.location}" if exp.location else ""
            lines.append(f"{exp.title}  |  {exp.company}{loc}  |  {date_str}")
            for b in exp.bullets:
                lines.append(f"  - {b}")
            lines.append("")
    if resume.education:
        lines += ["EDUCATION", "-" * 20]
        for edu in resume.education:
            date_str = " - ".join(filter(None, [edu.start_date, edu.end_date]))
            deg = ", ".join(filter(None, [edu.degree, edu.field_of_study]))
            lines.append(f"{deg}  |  {edu.institution}  |  {date_str}")
            lines.append("")
    if resume.certifications:
        lines += ["CERTIFICATIONS", "-" * 20] + [f"- {c}" for c in resume.certifications] + [""]
    if resume.languages:
        lines += ["LANGUAGES", "-" * 20, ", ".join(resume.languages), ""]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Template Selector & HTML Preview
# ─────────────────────────────────────────────────────────────────────────────

def _on_template_change() -> None:
    """Called when the template radio changes — invalidates the cached PDF."""
    st.session_state["pdf_signature"] = None
    st.session_state["pdf_bytes"] = None
    st.session_state["pdf_filename"] = None


def render_template_selector(resume: ResumeData) -> str:
    """Renders template radio + live HTML preview. Returns selected template key."""
    template_keys = list(TEMPLATES.keys())
    if st.session_state.get("selected_template") not in template_keys:
        st.session_state["selected_template"] = template_keys[0]

    choice = st.radio(
        "Template",
        options=template_keys,
        format_func=lambda k: f"{TEMPLATES[k]['emoji']}  {TEMPLATES[k]['name']}",
        horizontal=True,
        key="selected_template",
        label_visibility="collapsed",
        on_change=_on_template_change,
    )

    st.caption(TEMPLATES[choice]["description"])

    if not resume.is_empty():
        html_str = render_template(choice, resume)
        components.html(f"<!-- preview:{choice} -->{html_str}", height=700, scrolling=True)
    else:
        st.info("Your resume preview will appear here once data is entered.")

    return choice


# ─────────────────────────────────────────────────────────────────────────────
# Job Tailoring
# ─────────────────────────────────────────────────────────────────────────────

def render_job_tailor(resume: ResumeData, provider) -> ResumeData:
    """Renders job description input and triggers AI tailoring."""
    st.markdown("### 🎯 Tailor to a Job")
    st.caption("Paste a job description and let AI adapt your resume to match it.")

    with st.expander("📋 Enter Job Details", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            job_title = st.text_input("Job Title *", placeholder="Senior Product Manager", key="jd_title")
        with c2:
            company = st.text_input("Company (optional)", placeholder="Acme Corp", key="jd_company")

        job_desc = st.text_area(
            "Job Description *",
            height=220,
            placeholder="Paste the full job description here...",
            key="jd_text",
        )

        if st.button("🎯 Tailor Resume to This Job", type="primary", use_container_width=True):
            if not job_title or not job_desc:
                st.warning("Please enter at least a job title and description.")
            elif resume.is_empty():
                st.warning("Parse your resume first.")
            elif provider is None:
                st.error("No AI provider configured. Choose a provider and add a key if needed.")
            else:
                allowed, message = check_limit("ai_tailors")
                if not allowed:
                    st.warning(message)
                    return st.session_state.get("resume_data", resume)

                with st.spinner(f"Tailoring with {provider.name}..."):
                    try:
                        prompt = get_job_tailor_prompt(resume.to_json(), job_title, job_desc, company)
                        response_text = provider.complete(prompt)
                        cleaned = response_text.strip()
                        if cleaned.startswith("```"):
                            cleaned = cleaned.split("```")[1]
                            if cleaned.startswith("json"):
                                cleaned = cleaned[4:]
                        data_dict = json.loads(cleaned)
                        tailored = ResumeData.from_dict(data_dict)
                        st.session_state["resume_data"] = tailored
                        increment("ai_tailors")
                        st.success("Resume tailored to the job! Review the preview below.")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("AI returned invalid JSON. Please try again.")
                    except Exception as e:
                        st.error(f"Tailoring failed: {e}")

    return st.session_state.get("resume_data", resume)


# ─────────────────────────────────────────────────────────────────────────────
# AI General Enhancement
# ─────────────────────────────────────────────────────────────────────────────

def render_resume_generator(resume: ResumeData, provider=None) -> ResumeData:
    """General AI enhancement panel."""
    st.markdown("### ✨ AI Enhancement")
    st.caption("Strengthen bullet points and summary without a specific job target.")

    target_role = st.text_input(
        "Target role (optional)",
        placeholder="e.g. Senior Software Engineer",
        key="target_role",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("✨ Improve with AI", type="primary", use_container_width=True):
            if resume.is_empty():
                st.warning("Please parse or enter resume data first.")
            elif provider is None:
                st.error("No AI provider configured. Choose a provider and add a key if needed.")
            else:
                allowed, message = check_limit("ai_improves")
                if not allowed:
                    st.warning(message)
                    return st.session_state.get("resume_data", resume)

                with st.spinner(f"{provider.name} is rewriting your resume..."):
                    try:
                        prompt = get_improve_prompt(resume.to_json(), target_role)
                        response_text = provider.complete(prompt)
                        cleaned = response_text.strip()
                        if cleaned.startswith("```"):
                            cleaned = cleaned.split("```")[1]
                            if cleaned.startswith("json"):
                                cleaned = cleaned[4:]
                        data_dict = json.loads(cleaned)
                        improved = ResumeData.from_dict(data_dict)
                        st.session_state["resume_data"] = improved
                        increment("ai_improves")
                        st.success("Resume improved! See the updated preview below.")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("AI returned invalid JSON. Please try again.")
                    except Exception as e:
                        st.error(f"Enhancement failed: {e}")

    with col2:
        if st.button("Reset to Original", use_container_width=True):
            if "original_resume" in st.session_state:
                st.session_state["resume_data"] = st.session_state["original_resume"]
                st.success("Reverted.")
                st.rerun()

    return st.session_state.get("resume_data", resume)


# ─────────────────────────────────────────────────────────────────────────────
# Download Section
# ─────────────────────────────────────────────────────────────────────────────

def render_download_section(resume: ResumeData, selected_template: str = "modern"):
    """Renders the PDF download button."""
    if resume.is_empty():
        st.info("Complete your resume above to enable download.")
        return

    safe_name = resume.name.replace(" ", "_") if resume.name else "resume"
    resume_signature = hashlib.sha256(
        f"{selected_template}\n{resume.to_json()}".encode("utf-8")
    ).hexdigest()

    if st.session_state.get("pdf_signature") != resume_signature:
        st.session_state["pdf_bytes"] = None
        st.session_state["pdf_filename"] = None
        with st.spinner("Rendering PDF..."):
            try:
                html_str = render_template(selected_template, resume)
                pdf_bytes = html_to_pdf(html_str)
                st.session_state["pdf_bytes"] = pdf_bytes
                st.session_state["pdf_filename"] = f"{safe_name}_{selected_template}.pdf"
                st.session_state["pdf_signature"] = resume_signature
            except Exception as e:
                st.session_state["pdf_bytes"] = None
                st.session_state["pdf_filename"] = None
                st.session_state["pdf_signature"] = None
                st.error(f"PDF generation failed: {e}")

    if st.session_state.get("pdf_bytes"):
        st.download_button(
            label=f"Download PDF ({TEMPLATES[selected_template]['name']})",
            data=st.session_state["pdf_bytes"],
            file_name=st.session_state.get("pdf_filename", "resume.pdf"),
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info("Generating PDF — this takes a few seconds the first time.")
