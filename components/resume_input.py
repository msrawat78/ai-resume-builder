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
    st.markdown("### 📄 Import Your Resume")
    st.caption(f"Use a resume with less than {MAX_RESUME_TEXT_CHARS:,} characters after extraction for best results.")

    tab_upload, tab_paste, tab_linkedin = st.tabs([
        "📎 Upload File",
        "✏️  Paste Text",
        "🔗 LinkedIn URL",
    ])

    raw_text: str | None = None

    # ── Tab 1: File Upload ────────────────────────────────────────────────────
    with tab_upload:
        st.markdown(
            "Upload your resume as a **PDF** or **DOCX** file. "
            "Text will be extracted automatically."
        )
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
        st.markdown("Paste your resume content below (plain text or copied from Word/Google Docs).")

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
        st.markdown(
            "Enter your LinkedIn profile URL. "
            "*(Full scraping requires browser auth — this demo uses a placeholder workflow.)*"
        )
        li_url = st.text_input(
            "LinkedIn URL",
            placeholder="https://linkedin.com/in/your-name",
            key="linkedin_url_input",
            label_visibility="collapsed",
        )
        if li_url:
            ok, msg = validate_linkedin_url(li_url)
            if ok:
                st.info(
                    "🔗 LinkedIn import noted. In a production deployment this would trigger "
                    "an authenticated scrape or the LinkedIn API. For now, please also paste "
                    "your resume text in the **Paste Text** tab."
                )
            else:
                st.warning(f"⚠️ {msg}")

    return raw_text
