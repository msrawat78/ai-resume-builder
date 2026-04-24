"""
resume_form.py — Structured input form for Form Mode (no AI).

User fills in every field directly. Output is a ResumeData object
identical to what the AI parser produces — so all downstream steps
(templates, PDF, download) work without any changes.

Session state keys used (prefixed with "frm_" to avoid clashing
with the editor's "ed_" and "exp_" keys):
  frm_exp_count   — number of experience rows shown
  frm_edu_count   — number of education rows shown
"""

import streamlit as st
from models.resume_schema import ResumeData, ExperienceEntry, EducationEntry
from utils.validators import validate_email, validate_phone


# ── helpers ───────────────────────────────────────────────────────────────────

def _section(title: str, subtitle: str = ""):
    """Renders an Electric Blueprint style section header."""
    st.markdown(
        f"<div style='"
        f"font-family:Space Grotesk,sans-serif;"
        f"font-size:11px;font-weight:700;"
        f"text-transform:uppercase;letter-spacing:0.14em;"
        f"color:#0055FF;margin:28px 0 4px;'>"
        f"{title}</div>"
        f"<div style='width:40px;height:2px;background:#0055FF;margin-bottom:14px;'></div>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.caption(subtitle)


def _field_note(msg: str):
    st.markdown(
        f"<div style='font-size:11px;color:#8494AD;margin-top:-8px;"
        f"margin-bottom:8px;font-family:JetBrains Mono,monospace;'>"
        f"{msg}</div>",
        unsafe_allow_html=True,
    )


# ── main form ─────────────────────────────────────────────────────────────────

def render_resume_form() -> ResumeData | None:
    """
    Renders the full structured input form.
    Returns a populated ResumeData when the user clicks Next,
    or None while the form is still being filled.
    """

    # ── 1. Contact ────────────────────────────────────────────────────────────
    _section("Contact Information")

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(
            "Full Name *",
            placeholder="Alex Carter",
            key="frm_name",
        )
        email = st.text_input(
            "Email *",
            placeholder="alex.carter@example.com",
            key="frm_email",
        )
        _, email_msg = validate_email(st.session_state.get("frm_email", ""))
        if email_msg:
            _field_note(f"⚠ {email_msg}")

    with c2:
        phone = st.text_input(
            "Phone",
            placeholder="+1 555 010 2020",
            key="frm_phone",
        )
        _, phone_msg = validate_phone(st.session_state.get("frm_phone", ""))
        if phone_msg:
            _field_note(f"⚠ {phone_msg}")

        location = st.text_input(
            "Location",
            placeholder="Bengaluru, India",
            key="frm_location",
        )

    c3, c4 = st.columns(2)
    with c3:
        linkedin = st.text_input(
            "LinkedIn URL",
            placeholder="linkedin.com/in/alex-carter",
            key="frm_linkedin",
        )
    with c4:
        website = st.text_input(
            "Website / Portfolio",
            placeholder="alexcarter.dev",
            key="frm_website",
        )

    # ── 2. Summary ────────────────────────────────────────────────────────────
    _section(
        "Professional Summary",
        "3–4 sentences: who you are, what you do, what you bring.",
    )
    summary = st.text_area(
        "Summary",
        height=130,
        placeholder=(
            "Software engineer with 6 years of experience building scalable web "
            "applications and data pipelines. Strong background in Python, cloud "
            "infrastructure, and cross-functional team collaboration."
        ),
        key="frm_summary",
        label_visibility="collapsed",
    )

    # ── 3. Skills ─────────────────────────────────────────────────────────────
    _section(
        "Skills",
        "One skill per line, or comma-separated. "
        "Use broad categories (e.g. 'Data Engineering') or specific tools.",
    )
    skills_raw = st.text_area(
        "Skills",
        height=110,
        placeholder="Python\nJavaScript\nReact\nPostgreSQL\nAWS\nDocker",
        key="frm_skills",
        label_visibility="collapsed",
    )
    skills = [
        s.strip()
        for s in skills_raw.replace(",", "\n").splitlines()
        if s.strip()
    ]

    # ── 4. Experience ─────────────────────────────────────────────────────────
    _section("Work Experience")

    if "frm_exp_count" not in st.session_state:
        st.session_state["frm_exp_count"] = 1

    exp_count   = st.session_state["frm_exp_count"]
    experiences = []

    for i in range(exp_count):
        label = f"Position {i + 1}"
        if st.session_state.get(f"frm_exp_title_{i}"):
            co = st.session_state.get(f"frm_exp_company_{i}", "")
            label = f"{st.session_state[f'frm_exp_title_{i}']}"
            if co:
                label += f"  ·  {co}"

        with st.expander(label, expanded=(i == 0)):
            ca, cb = st.columns(2)
            with ca:
                st.text_input(
                    "Job Title *",
                    placeholder="Senior Software Engineer",
                    key=f"frm_exp_title_{i}",
                )
                st.text_input(
                    "Company *",
                    placeholder="Acme Solutions",
                    key=f"frm_exp_company_{i}",
                )
            with cb:
                st.text_input(
                    "Location",
                    placeholder="Bengaluru / Remote",
                    key=f"frm_exp_loc_{i}",
                )
                cs, ce = st.columns(2)
                with cs:
                    st.text_input(
                        "Start",
                        placeholder="Jan 2020",
                        key=f"frm_exp_start_{i}",
                    )
                with ce:
                    st.text_input(
                        "End",
                        placeholder="Present",
                        key=f"frm_exp_end_{i}",
                    )

            st.text_area(
                "Key achievements — one bullet per line",
                height=120,
                placeholder=(
                    "Built real-time dashboard serving 50,000+ daily active users\n"
                    "Reduced API response time by 35% via caching and query optimization\n"
                    "Mentored team of 4 engineers and led weekly code reviews"
                ),
                key=f"frm_exp_bullets_{i}",
            )

        # Collect values
        experiences.append(
            ExperienceEntry(
                title      = st.session_state.get(f"frm_exp_title_{i}",    ""),
                company    = st.session_state.get(f"frm_exp_company_{i}",  ""),
                location   = st.session_state.get(f"frm_exp_loc_{i}",      ""),
                start_date = st.session_state.get(f"frm_exp_start_{i}",    ""),
                end_date   = st.session_state.get(f"frm_exp_end_{i}",      ""),
                bullets    = [
                    b.strip()
                    for b in st.session_state.get(
                        f"frm_exp_bullets_{i}", ""
                    ).splitlines()
                    if b.strip()
                ],
            )
        )

    # Add / remove experience rows
    ca, cb = st.columns([1, 1])
    with ca:
        if st.button("＋ Add Position", key="frm_add_exp", use_container_width=True):
            st.session_state["frm_exp_count"] += 1
            st.rerun()
    with cb:
        if exp_count > 1 and st.button(
            "－ Remove Last", key="frm_rem_exp", use_container_width=True
        ):
            st.session_state["frm_exp_count"] -= 1
            experiences = experiences[:-1]
            st.rerun()

    # ── 5. Education ──────────────────────────────────────────────────────────
    _section("Education")

    if "frm_edu_count" not in st.session_state:
        st.session_state["frm_edu_count"] = 1

    edu_count  = st.session_state["frm_edu_count"]
    educations = []

    for i in range(edu_count):
        label = f"Education {i + 1}"
        if st.session_state.get(f"frm_edu_deg_{i}"):
            inst = st.session_state.get(f"frm_edu_inst_{i}", "")
            label = st.session_state[f"frm_edu_deg_{i}"]
            if inst:
                label += f"  ·  {inst}"

        with st.expander(label, expanded=(i == 0)):
            ca, cb = st.columns(2)
            with ca:
                st.text_input(
                    "Degree *",
                    placeholder="B.E. / B.Tech. / M.S.",
                    key=f"frm_edu_deg_{i}",
                )
                st.text_input(
                    "Field of Study",
                    placeholder="Computer Science / Information Systems",
                    key=f"frm_edu_field_{i}",
                )
            with cb:
                st.text_input(
                    "Institution *",
                    placeholder="PES University / BITS Pilani",
                    key=f"frm_edu_inst_{i}",
                )
                st.text_input(
                    "GPA / Grade (optional)",
                    placeholder="8.5 / 10",
                    key=f"frm_edu_gpa_{i}",
                )

            cs, ce, ch = st.columns(3)
            with cs:
                st.text_input("Start Year", placeholder="2018", key=f"frm_edu_start_{i}")
            with ce:
                st.text_input("End Year",   placeholder="2022", key=f"frm_edu_end_{i}")
            with ch:
                st.text_input("Honors",     placeholder="Distinction", key=f"frm_edu_honors_{i}")

        educations.append(
            EducationEntry(
                institution  = st.session_state.get(f"frm_edu_inst_{i}",   ""),
                degree       = st.session_state.get(f"frm_edu_deg_{i}",    ""),
                field_of_study = st.session_state.get(f"frm_edu_field_{i}", ""),
                start_date   = st.session_state.get(f"frm_edu_start_{i}",  ""),
                end_date     = st.session_state.get(f"frm_edu_end_{i}",    ""),
                gpa          = st.session_state.get(f"frm_edu_gpa_{i}",    ""),
                honors       = st.session_state.get(f"frm_edu_honors_{i}", ""),
            )
        )

    if st.button("＋ Add Education", key="frm_add_edu"):
        st.session_state["frm_edu_count"] += 1
        st.rerun()

    # ── 6. Certifications & Languages ─────────────────────────────────────────
    _section("Certifications & Languages")

    ca, cb = st.columns(2)
    with ca:
        certs_raw = st.text_area(
            "Certifications (one per line)",
            height=100,
            placeholder="AWS Solutions Architect – Associate\nGoogle Professional Data Engineer",
            key="frm_certs",
        )
        certs = [c.strip() for c in certs_raw.splitlines() if c.strip()]
    with cb:
        langs_raw = st.text_area(
            "Languages (one per line)",
            height=100,
            placeholder="English\nHindi\nKannada",
            key="frm_langs",
        )
        langs = [l.strip() for l in langs_raw.splitlines() if l.strip()]

    # ── Submit ────────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    # Validation before allowing submit
    name_val  = st.session_state.get("frm_name",  "").strip()
    email_val = st.session_state.get("frm_email", "").strip()

    _, col_btn = st.columns([3, 1])
    with col_btn:
        submitted = st.button(
            "Next",
            type="primary",
            use_container_width=True,
            key="frm_submit",
        )

    if submitted:
        # Required field checks
        errors = []
        if not name_val:
            errors.append("Full Name is required.")
        if not email_val:
            errors.append("Email is required.")
        else:
            ok, msg = validate_email(email_val)
            if not ok:
                errors.append(msg)

        has_exp = any(
            st.session_state.get(f"frm_exp_title_{i}", "").strip()
            for i in range(exp_count)
        )
        if not has_exp:
            errors.append("Add at least one work experience entry.")

        if errors:
            for e in errors:
                st.error(e)
            return None

        # Build and return the ResumeData object
        return ResumeData(
            name           = name_val,
            email          = email_val,
            phone          = st.session_state.get("frm_phone",    "").strip(),
            location       = st.session_state.get("frm_location", "").strip(),
            linkedin       = st.session_state.get("frm_linkedin", "").strip(),
            website        = st.session_state.get("frm_website",  "").strip(),
            summary        = st.session_state.get("frm_summary",  "").strip(),
            skills         = skills,
            experience     = [e for e in experiences if e.title or e.company],
            education      = [e for e in educations  if e.institution or e.degree],
            certifications = certs,
            languages      = langs,
        )

    return None
