"""
AI Resume Builder application entrypoint.
"""

from __future__ import annotations

import streamlit as st

from components.resume_editor import render_resume_editor
from components.resume_generator import (
    render_download_section,
    render_job_tailor,
    render_resume_generator,
    render_template_selector,
)
from components.resume_input import render_resume_input
from components.resume_parser import parse_resume
from utils.ai_provider import commit_active_provider, get_active_provider, has_provider_key, render_provider_selector
from utils.email_gate import render_email_gate
from utils.rate_limiter import check_limit, increment, render_usage_banner
from utils.validators import validate_resume_data


st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


FORM_STEPS = ["Mode", "Fill", "Preview"]
SMART_STEPS = ["Mode", "AI Setup", "Import", "Parse", "Edit", "Tailor", "Preview"]

AI_ACTION_OPTIONS = {
    "skip": "Skip AI and go to preview",
    "improve": "Improve resume with AI",
    "tailor": "Tailor resume to a job",
}


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
          --blue: #0055FF;
          --blue-dark: #0037A6;
          --cyan: #00C8FF;
          --green: #00A76F;
          --ink: #0D1628;
          --ink-soft: #51627E;
          --ink-muted: #8091AD;
          --rule: #C8D4E8;
          --bg: #F6F9FF;
          --card: #FFFFFF;
        }

        html, body, [class*="css"], .stApp {
          font-family: 'Space Grotesk', sans-serif !important;
          background: var(--bg) !important;
          color: var(--ink-soft);
        }

        [data-testid="stSidebar"] {
          display: none !important;
        }

        .block-container {
          padding-top: 1.6rem;
          padding-bottom: 3rem;
          max-width: 1120px;
        }

        .kmx-header {
          position: relative;
          background: linear-gradient(135deg, #0055FF 0%, #0037A6 100%);
          padding: 36px 42px 32px;
          margin-bottom: 1.2rem;
          overflow: hidden;
        }

        .kmx-header::before {
          content: '';
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
          background-size: 28px 28px;
        }

        .kmx-header .mono-tag {
          position: relative;
          display: inline-block;
          margin-bottom: 10px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: var(--cyan);
        }

        .kmx-header h1 {
          position: relative;
          margin: 0 0 6px;
          font-size: 2.4rem;
          font-weight: 700;
          letter-spacing: -0.03em;
          color: #fff;
        }

        .kmx-header h1 em {
          color: var(--cyan);
          font-style: normal;
        }

        .kmx-header p {
          position: relative;
          margin: 0;
          color: rgba(255,255,255,0.8);
          font-size: 15px;
        }

        .sticky-step-wrap {
          position: sticky;
          top: 0.4rem;
          z-index: 40;
          background: linear-gradient(180deg, rgba(246,249,255,0.98) 0%, rgba(246,249,255,0.95) 100%);
          padding: 14px 0 12px;
          margin-bottom: 1.1rem;
          backdrop-filter: blur(8px);
        }

        .step-bar {
          display: grid;
          gap: 8px;
        }

        .step-bar.cols-3 {
          grid-template-columns: repeat(3, 1fr);
        }

        .step-bar.cols-6 {
          grid-template-columns: repeat(7, minmax(0, 1fr));
        }

        .step {
          padding: 10px 8px;
          border: 1px solid var(--rule);
          background: var(--card);
          color: var(--ink-muted);
          text-align: center;
          font-family: 'JetBrains Mono', monospace;
          font-size: 9px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          white-space: nowrap;
        }

        .step-active {
          background: var(--blue);
          border-color: var(--blue);
          color: #fff;
        }

        .step-done {
          background: #E7FFF5;
          border-color: var(--green);
          color: var(--green);
        }

        .step-shell {
          background: var(--card);
          border: 1px solid var(--rule);
          padding: 20px 22px 26px;
        }

        .step-heading {
          margin-bottom: 0.75rem;
        }

        .step-heading h3 {
          margin-bottom: 0.2rem;
        }

        .stButton > button {
          border-radius: 0 !important;
          font-weight: 600 !important;
          color: var(--ink) !important;
        }

        .stButton > button[kind="primary"] {
          background: var(--blue) !important;
          border-color: var(--blue) !important;
          color: #FFFFFF !important;
        }

        .stButton > button:disabled,
        .stButton > button[disabled] {
          background: #EAF0FF !important;
          border-color: var(--rule) !important;
          color: var(--ink-muted) !important;
          opacity: 1 !important;
        }

        .stAlert {
          border-radius: 0 !important;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
          border-radius: 0 !important;
        }

        div[role="radiogroup"] {
          gap: 0.6rem;
        }

        div[role="radiogroup"] label {
          border: 1px solid var(--rule) !important;
          background: #FFFFFF !important;
          padding: 0.55rem 0.9rem !important;
          border-radius: 999px !important;
          min-height: auto !important;
        }

        div[role="radiogroup"] label:has(input:checked) {
          background: #EAF0FF !important;
          border-color: var(--blue) !important;
          box-shadow: inset 0 0 0 1px var(--blue);
        }

        div[role="radiogroup"] label p {
          color: var(--ink) !important;
          font-weight: 600 !important;
          margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session() -> None:
    defaults = {
        "resume_data": None,
        "original_resume": None,
        "raw_text": None,
        "step": 1,
        "processing_mode": "form",
        "mode_selector": "form",
        "selected_mode_confirmed": False,
        "ai_setup_complete": False,
        "selected_template": "modern",
        "template_selector_choice": "modern",
        "pdf_bytes": None,
        "pdf_filename": None,
        "pdf_signature": None,
        "ai_action_choice": "skip",
        "experience_count": 1,
        "education_count": 1,
        "confirmed_paste": None,
        "_last_mode": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_header() -> None:
    st.markdown(
        """
        <div class="kmx-header">
          <span class="mono-tag">Klaymatrix Data Labs · AI Resume Builder</span>
          <h1>AI <em>Resume</em> Builder</h1>
          <p>Build a professional resume with a lighter, step-by-step workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _step_labels(mode: str) -> list[str]:
    return FORM_STEPS if mode == "form" else SMART_STEPS


def _max_unlocked_step(mode: str) -> int:
    if mode == "form":
        if not st.session_state.get("selected_mode_confirmed"):
            return 1
        if st.session_state.get("resume_data"):
            return 3
        return 2

    if not st.session_state.get("selected_mode_confirmed"):
        return 1
    if not st.session_state.get("ai_setup_complete"):
        return 2
    if not st.session_state.get("raw_text"):
        return 3
    if not st.session_state.get("resume_data"):
        return 4
    return 7


def _set_step(step: int, mode: str) -> None:
    st.session_state["step"] = max(1, min(step, _max_unlocked_step(mode)))


def _sync_step(mode: str) -> int:
    current = st.session_state.get("step", 1)
    _set_step(current, mode)
    return st.session_state["step"]


def _render_step_bar(mode: str, current: int) -> None:
    labels = _step_labels(mode)
    bar_class = "cols-3" if len(labels) <= 4 else "cols-6"
    html = [f'<div class="sticky-step-wrap"><div class="step-bar {bar_class}">']
    for index, label in enumerate(labels, start=1):
        state_class = "step"
        if index < current:
            state_class += " step-done"
        elif index == current:
            state_class += " step-active"
        html.append(f'<div class="{state_class}">{index}. {label}</div>')
    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _step_shell(title: str, subtitle: str) -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="step-shell"><div class="step-heading"><h3>{title}</h3>{subtitle_html}</div></div>',
        unsafe_allow_html=True,
    )


def _close_step_shell() -> None:
    return None


def _reset_flow_state(target_mode: str) -> None:
    st.session_state["processing_mode"] = target_mode
    st.session_state["resume_data"] = None
    st.session_state["original_resume"] = None
    st.session_state["raw_text"] = None
    st.session_state["pdf_bytes"] = None
    st.session_state["pdf_filename"] = None
    st.session_state["pdf_signature"] = None
    st.session_state["selected_template"] = "modern"
    st.session_state["template_selector_choice"] = "modern"
    st.session_state["ai_action_choice"] = "skip"
    st.session_state["committed_provider_choice"] = ""
    st.session_state["committed_provider_key"] = ""
    st.session_state["selected_mode_confirmed"] = True
    st.session_state["ai_setup_complete"] = target_mode == "form"
    st.session_state["step"] = 2
    st.session_state["_last_mode"] = target_mode


def _parse_current_resume(provider) -> bool:
    allowed, message = check_limit("ai_parses")
    if not allowed:
        st.warning(message)
        return False
    if provider is None:
        st.error("No AI provider configured. Go back and set up your provider.")
        return False

    result = parse_resume(st.session_state.get("raw_text", ""), provider)
    if not result:
        return False

    increment("ai_parses")
    st.session_state["resume_data"] = result
    st.session_state["original_resume"] = result
    st.session_state["experience_count"] = max(1, len(result.experience))
    st.session_state["education_count"] = max(1, len(result.education))
    st.session_state["pdf_bytes"] = None
    st.session_state["pdf_filename"] = None
    st.session_state["pdf_signature"] = None
    return True


def _render_nav(
    mode: str,
    current: int,
    allow_next: bool,
    next_label: str = "Next",
    on_next=None,
) -> None:
    step_count = len(_step_labels(mode))
    prev_disabled = current <= 1
    next_disabled = (current >= step_count) or (not allow_next)

    left, _, right = st.columns([1, 2, 1])
    with left:
        if st.button("Back", use_container_width=True, disabled=prev_disabled, key=f"back_{mode}_{current}"):
            _set_step(current - 1, mode)
            st.rerun()
    with right:
        if st.button(next_label, type="primary", use_container_width=True, disabled=next_disabled, key=f"next_{mode}_{current}"):
            if on_next is not None and not on_next():
                st.stop()
            if mode == "ai" and current == 2:
                st.session_state["ai_setup_complete"] = True
            _set_step(current + 1, mode)
            st.rerun()


def _render_mode_selector(step_key: str) -> str:
    selected = st.radio(
        "Choose how to build your resume",
        options=["form", "ai"],
        format_func=lambda value: (
            "Form Mode"
            if value == "form"
            else "Smart Mode"
        ),
        horizontal=True,
        key=step_key,
        label_visibility="collapsed",
    )
    st.caption("Form Mode: enter all resume details manually from scratch.")
    st.caption("Smart Mode: import an existing resume and refine it with AI.")
    return selected


def _render_mode_continue_button(button_key: str, selected: str, expected_mode: str) -> None:
    left, right = st.columns([8, 1])
    with right:
        if st.button("Next", type="primary", key=button_key):
            target_mode = "ai" if selected != "form" else "form"
            if expected_mode == "ai":
                target_mode = "form" if selected != "ai" else "ai"
            _reset_flow_state(target_mode)
            st.rerun()


def _render_form_mode(current_step: int) -> None:
    from components.resume_form import render_resume_form

    _render_step_bar("form", current_step)

    if current_step == 1:
        _step_shell("Choose Mode", "Start by deciding whether you want the manual form flow or the AI-assisted flow.")
        selected = _render_mode_selector("mode_selector")
        _render_mode_continue_button("continue_mode_form", selected, "form")
        _close_step_shell()
        return

    if current_step == 2:
        _step_shell("Fill", "Enter your details directly. No AI settings are shown in Form Mode.")
        result = render_resume_form()
        if result:
            allowed, message = check_limit("form_uses")
            if not allowed:
                st.warning(message)
            else:
                increment("form_uses")
                st.session_state["resume_data"] = result
                st.session_state["pdf_bytes"] = None
                st.session_state["pdf_filename"] = None
                st.session_state["step"] = 3
                st.success(f"Resume built for {result.name}.")
                st.rerun()
        left, _, _ = st.columns([1, 2, 1])
        with left:
            if st.button("Back", use_container_width=True, key="back_form_fill"):
                st.session_state["selected_mode_confirmed"] = False
                st.session_state["step"] = 1
                st.rerun()
        _close_step_shell()
        return

    resume = st.session_state.get("resume_data")
    if not resume:
        _set_step(2, "form")
        st.rerun()

    if current_step == 3:
        _step_shell("Preview", "Choose a template, review it, and download from the same section.")
        selected_template = render_template_selector(resume)
        st.caption(f"Current template: {selected_template}")
        render_download_section(resume, selected_template)
        _close_step_shell()
        return


def _render_smart_mode(current_step: int) -> None:
    _render_step_bar("ai", current_step)
    if current_step == 1:
        _step_shell("Choose Mode", "Start by deciding whether you want the manual form flow or the AI-assisted flow.")
        selected = _render_mode_selector("mode_selector")
        _render_mode_continue_button("continue_mode_ai", selected, "ai")
        _close_step_shell()
        return

    provider = render_provider_selector() if current_step == 2 else get_active_provider()

    if current_step == 2:
        _step_shell("API Key", "")
        if provider is not None:
            st.success(f"Provider ready: {provider.name}")
        elif has_provider_key():
            st.info("API key detected. You can continue to import your resume.")
        can_continue = has_provider_key()
        _render_nav(
            "ai",
            current_step,
            allow_next=can_continue,
            next_label="Import",
            on_next=commit_active_provider,
        )
        _close_step_shell()
        return

    if not st.session_state.get("ai_setup_complete"):
        _set_step(2, "ai")
        st.rerun()

    if current_step == 3:
        raw_text = render_resume_input()
        if raw_text:
            st.session_state["raw_text"] = raw_text
        if st.session_state.get("raw_text"):
            st.success("Resume content is ready for parsing.")
        _render_nav("ai", current_step, allow_next=bool(st.session_state.get("raw_text")))
        return

    if not st.session_state.get("raw_text"):
        _set_step(3, "ai")
        st.rerun()

    if current_step == 4:
        _step_shell("Parse", "Turn your imported text into structured resume data.")
        render_usage_banner()
        if provider is not None:
            st.caption(f"Using provider: {provider.name}")
        else:
            choice = st.session_state.get("committed_provider_choice") or st.session_state.get("provider_choice")
            if choice:
                st.warning(
                    "Your provider choice is remembered, but the API key is not available in this step. "
                    "Go back to Import, re-enter the key once, then continue."
                )
        can_continue = st.session_state.get("resume_data") is not None
        next_label = "Next" if can_continue else "Parse & Continue"
        _render_nav(
            "ai",
            current_step,
            allow_next=bool(st.session_state.get("raw_text")),
            next_label=next_label,
            on_next=lambda: can_continue or _parse_current_resume(provider),
        )
        _close_step_shell()
        return

    resume = st.session_state.get("resume_data")
    if not resume:
        _set_step(4, "ai")
        st.rerun()

    if current_step == 5:
        _step_shell("Edit", "Make structured changes before running any AI rewrite or tailoring.")
        updated = render_resume_editor(resume)
        st.session_state["resume_data"] = updated

        _, warnings = validate_resume_data(updated.to_dict())
        if warnings:
            with st.expander(f"{len(warnings)} suggestion(s)", expanded=False):
                for warning in warnings:
                    st.markdown(f"- {warning}")

        st.radio(
            "Choose the next AI action",
            options=list(AI_ACTION_OPTIONS.keys()),
            format_func=lambda key: AI_ACTION_OPTIONS[key],
            horizontal=True,
            key="ai_action_choice",
        )

        next_label = "Preview" if st.session_state.get("ai_action_choice") == "skip" else "Next"
        _render_nav("ai", current_step, allow_next=True, next_label=next_label)
        _close_step_shell()
        return

    if current_step == 6:
        ai_action = st.session_state.get("ai_action_choice", "skip")
        if ai_action == "skip":
            st.session_state["step"] = 7
            st.rerun()

        _step_shell("Tailor", "Run the AI action you selected in the previous step.")
        render_usage_banner()
        if ai_action == "tailor":
            render_job_tailor(st.session_state["resume_data"], provider)
        else:
            render_resume_generator(st.session_state["resume_data"], provider)
        _render_nav("ai", current_step, allow_next=True)
        _close_step_shell()
        return

    if current_step == 7:
        _step_shell("Preview", "Choose a template, review it, and download from the same section.")
        selected_template = render_template_selector(st.session_state["resume_data"])
        st.caption(f"Current template: {selected_template}")
        render_download_section(st.session_state["resume_data"], selected_template)
        _close_step_shell()
        return


def main() -> None:
    _init_session()
    render_email_gate()
    _inject_styles()
    mode = st.session_state.get("processing_mode", "form")

    current_step = _sync_step(mode)
    if current_step == 1:
        _render_header()

    if mode == "form":
        _render_form_mode(current_step)
    else:
        _render_smart_mode(current_step)


if __name__ == "__main__":
    main()
