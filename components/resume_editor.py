"""
resume_editor.py — Streamlit component for editing parsed resume data.

Renders editable fields for every section of a ResumeData object and
returns an updated ResumeData after the user makes changes.
"""

import streamlit as st
from models.resume_schema import ResumeData, ExperienceEntry, EducationEntry
from utils.validators import validate_email, validate_phone


def _section_header(icon: str, title: str):
    st.markdown(f"#### {icon} {title}")
    st.divider()


def render_resume_editor(resume: ResumeData) -> ResumeData:
    """
    Renders form fields pre-populated with `resume` data.
    Returns a new ResumeData populated from the edited values.
    """
    st.markdown("### ✏️ Edit Your Resume")
    st.caption("All fields are editable. Changes are reflected instantly in the preview.")

    # ── Contact Info ──────────────────────────────────────────────────────────
    _section_header("👤", "Contact Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", value=resume.name, key="ed_name")
        email = st.text_input("Email *", value=resume.email, key="ed_email")
        _, email_msg = validate_email(email)
        if email_msg:
            st.caption(f"⚠️ {email_msg}")
    with col2:
        phone = st.text_input("Phone", value=resume.phone, key="ed_phone")
        _, phone_msg = validate_phone(phone)
        if phone_msg:
            st.caption(f"⚠️ {phone_msg}")
        location = st.text_input("Location", value=resume.location, key="ed_location")

    col3, col4 = st.columns(2)
    with col3:
        linkedin = st.text_input("LinkedIn URL", value=resume.linkedin, key="ed_linkedin")
    with col4:
        website = st.text_input("Website / Portfolio", value=resume.website, key="ed_website")

    # ── Summary ───────────────────────────────────────────────────────────────
    _section_header("📝", "Professional Summary")
    summary = st.text_area(
        "Summary",
        value=resume.summary,
        height=140,
        key="ed_summary",
        label_visibility="collapsed",
        help="A 3-4 sentence overview of your career.",
    )

    # ── Skills ────────────────────────────────────────────────────────────────
    _section_header("🛠️", "Skills")
    skills_raw = st.text_area(
        "Skills (one per line or comma-separated)",
        value="\n".join(resume.skills),
        height=120,
        key="ed_skills",
        label_visibility="collapsed",
    )
    skills = [s.strip() for s in skills_raw.replace(",", "\n").splitlines() if s.strip()]

    # ── Experience ────────────────────────────────────────────────────────────
    _section_header("💼", "Work Experience")

    if "experience_count" not in st.session_state:
        st.session_state["experience_count"] = max(1, len(resume.experience))

    exp_count = st.session_state["experience_count"]
    experiences = []

    for i in range(exp_count):
        existing = resume.experience[i] if i < len(resume.experience) else ExperienceEntry()
        with st.expander(
            f"Experience {i + 1}: {existing.title or 'New Entry'} @ {existing.company or '…'}",
            expanded=(i == 0),
        ):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Job Title", value=existing.title, key=f"exp_title_{i}")
                company = st.text_input("Company", value=existing.company, key=f"exp_company_{i}")
            with c2:
                exp_location = st.text_input("Location", value=existing.location, key=f"exp_loc_{i}")
                c_start, c_end = st.columns(2)
                with c_start:
                    start = st.text_input("Start Date", value=existing.start_date, key=f"exp_start_{i}", placeholder="Jan 2020")
                with c_end:
                    end = st.text_input("End Date", value=existing.end_date, key=f"exp_end_{i}", placeholder="Present")

            bullets_raw = st.text_area(
                "Bullet Points (one per line)",
                value="\n".join(existing.bullets),
                height=120,
                key=f"exp_bullets_{i}",
            )
            bullets = [b.strip() for b in bullets_raw.splitlines() if b.strip()]

            experiences.append(ExperienceEntry(
                title=title, company=company, location=exp_location,
                start_date=start, end_date=end, bullets=bullets,
            ))

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("＋ Add Experience", use_container_width=True):
            st.session_state["experience_count"] += 1
            st.rerun()
    with col_remove:
        if exp_count > 1 and st.button("－ Remove Last", use_container_width=True):
            st.session_state["experience_count"] -= 1
            experiences = experiences[:-1]
            st.rerun()

    # ── Education ─────────────────────────────────────────────────────────────
    _section_header("🎓", "Education")

    if "education_count" not in st.session_state:
        st.session_state["education_count"] = max(1, len(resume.education))

    edu_count = st.session_state["education_count"]
    educations = []

    for i in range(edu_count):
        existing_edu = resume.education[i] if i < len(resume.education) else EducationEntry()
        with st.expander(
            f"Education {i + 1}: {existing_edu.degree or 'New Entry'} @ {existing_edu.institution or '…'}",
            expanded=(i == 0),
        ):
            c1, c2 = st.columns(2)
            with c1:
                institution = st.text_input("Institution", value=existing_edu.institution, key=f"edu_inst_{i}")
                degree = st.text_input("Degree", value=existing_edu.degree, key=f"edu_deg_{i}", placeholder="B.S., M.S., Ph.D…")
            with c2:
                field = st.text_input("Field of Study", value=existing_edu.field_of_study, key=f"edu_field_{i}")
                gpa = st.text_input("GPA (optional)", value=existing_edu.gpa, key=f"edu_gpa_{i}")
            c_start, c_end, c_honors = st.columns(3)
            with c_start:
                edu_start = st.text_input("Start", value=existing_edu.start_date, key=f"edu_start_{i}")
            with c_end:
                edu_end = st.text_input("End", value=existing_edu.end_date, key=f"edu_end_{i}")
            with c_honors:
                honors = st.text_input("Honors", value=existing_edu.honors, key=f"edu_honors_{i}")

            educations.append(EducationEntry(
                institution=institution, degree=degree, field_of_study=field,
                start_date=edu_start, end_date=edu_end, gpa=gpa, honors=honors,
            ))

    if st.button("＋ Add Education", use_container_width=False):
        st.session_state["education_count"] += 1
        st.rerun()

    # ── Certifications & Languages ────────────────────────────────────────────
    _section_header("📜", "Certifications & Languages")
    c1, c2 = st.columns(2)
    with c1:
        certs_raw = st.text_area(
            "Certifications (one per line)",
            value="\n".join(resume.certifications),
            height=100,
            key="ed_certs",
        )
        certs = [c.strip() for c in certs_raw.splitlines() if c.strip()]
    with c2:
        langs_raw = st.text_area(
            "Languages (one per line)",
            value="\n".join(resume.languages),
            height=100,
            key="ed_langs",
        )
        langs = [l.strip() for l in langs_raw.splitlines() if l.strip()]

    # ── Return updated model ──────────────────────────────────────────────────
    return ResumeData(
        name=name, email=email, phone=phone, location=location,
        linkedin=linkedin, website=website, summary=summary,
        skills=skills, experience=experiences, education=educations,
        certifications=certs, languages=langs,
    )
