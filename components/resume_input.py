"""
resume_input.py — Streamlit component for accepting resume input.

Three input modes:
  1. File upload (PDF / DOCX)
  2. Paste plain text
  3. LinkedIn URL (placeholder — scraping requires auth)
"""

import streamlit as st
from utils.file_reader import read_uploaded_file
from utils.validators import MAX_RESUME_TEXT_CHARS, validate_resume_text, validate_linkedin_url


def render_resume_input() -> str | None:
    """
    Renders the three-tab input panel and returns extracted raw text,
    or None if no valid input has been provided yet.
    """
    st.caption(f"Supports PDF and DOCX. Under {MAX_RESUME_TEXT_CHARS:,} characters for best results.")

    tab_upload, tab_paste, tab_linkedin = st.tabs([
        "📎 Upload File",
        "✏️  Paste Text",
        "🔗 LinkedIn URL",
    ])

    raw_text: str | None = None

    # ── Tab 1: File Upload ────────────────────────────────────────────────────
    with tab_upload:
        uploaded = st.file_uploader(
            "Choose file",
            type=["pdf", "docx"],
            key="resume_file_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            with st.spinner("Extracting text from file…"):
                try:
                    raw_text = read_uploaded_file(uploaded)
                    ok, msg = validate_resume_text(raw_text)
                    if ok:
                        st.success(f"✅ Extracted {len(raw_text):,} characters from **{uploaded.name}**")
                        with st.expander("Preview extracted text"):
                            st.text(raw_text[:2000] + ("…" if len(raw_text) > 2000 else ""))
                    else:
                        st.warning(f"⚠️ {msg}")
                        raw_text = None
                except Exception as e:
                    st.error(f"❌ Failed to read file: {e}")
                    raw_text = None

    # ── Tab 2: Paste Text ─────────────────────────────────────────────────────
    with tab_paste:
        pasted = st.text_area(
            "Resume text",
            height=320,
            placeholder="Paste your full resume here…",
            key="resume_paste_input",
            label_visibility="collapsed",
        )

        if pasted and pasted.strip():
            ok, msg = validate_resume_text(pasted)
            if ok:
                st.session_state["confirmed_paste"] = pasted.strip()
            else:
                st.session_state.pop("confirmed_paste", None)
                st.warning(f"⚠️ {msg}")
        elif st.session_state.get("resume_paste_input", "").strip() == "":
            st.session_state.pop("confirmed_paste", None)

        if st.session_state.get("confirmed_paste"):
            raw_text = st.session_state["confirmed_paste"]
            st.success(f"✅ {len(raw_text):,} characters ready to parse.")

    # ── Tab 3: LinkedIn URL ───────────────────────────────────────────────────
    with tab_linkedin:
        st.caption("Full scraping requires browser auth. Paste your resume text in the Paste Text tab for best results.")
        li_url = st.text_input(
            "LinkedIn URL",
            placeholder="https://linkedin.com/in/alex-carter",
            key="linkedin_url_input",
            label_visibility="collapsed",
        )
        if li_url:
            ok, msg = validate_linkedin_url(li_url)
            if ok:
                st.info("URL noted. Use the Paste Text tab to add your resume content.")
            else:
                st.warning(f"⚠️ {msg}")

    return raw_text
