# AI Resume Builder

A production-quality Streamlit application that parses, edits, and AI-enhances resumes.

## Features

- **Three import modes**: Upload PDF/DOCX, paste text, or enter a LinkedIn URL
- **AI-powered parsing**: Extracts name, email, phone, summary, skills, experience, and education via Claude
- **Full inline editing**: Every field is editable directly in the UI
- **AI enhancement**: Rewrites bullet points and summary with strong action verbs and quantifiable results
- **Target role tailoring**: Optionally tailor improvements for a specific job title
- **Download as text**: Clean, ATS-friendly plain-text export
- **Live preview sidebar**: See the formatted resume update in real time

## Project Structure

```
ai-resume-builder/
├── app.py                        # Main Streamlit entry point
├── requirements.txt
├── models/
│   ├── __init__.py
│   └── resume_schema.py          # ResumeData, ExperienceEntry, EducationEntry dataclasses
├── components/
│   ├── __init__.py
│   ├── resume_input.py           # Three-tab import panel
│   ├── resume_parser.py          # Claude API → ResumeData
│   ├── resume_editor.py          # Editable form for all resume fields
│   └── resume_generator.py      # AI enhancement + text download
└── utils/
    ├── __init__.py
    ├── file_reader.py            # PDF and DOCX text extraction
    ├── prompt_templates.py       # Centralised AI prompts
    └── validators.py             # Email, phone, URL, and data validators
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or create `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Usage Workflow

1. **Import** — Upload a PDF/DOCX or paste resume text
2. **Parse** — Click "Parse Resume" to extract structured data via Claude
3. **Edit** — Review and edit all extracted fields inline
4. **Enhance** — Click "Improve with AI" to upgrade bullet points and summary
5. **Download** — Export as a clean `.txt` file

## Multi-user Support

Streamlit's session state is isolated per browser session, so multiple users can run the app simultaneously without interfering with each other. Each user's resume data is scoped to their own session.

## Extending the App

- **Add JSON/Markdown export**: Extend `render_download_section()` in `resume_generator.py`
- **Add a cover letter generator**: Create `components/cover_letter.py` using `prompt_templates.py`
- **Persist data**: Connect session state to a database (e.g. SQLite, Supabase) by serialising `resume.to_dict()`
- **LinkedIn scraping**: Implement `utils/linkedin_scraper.py` using Playwright with authenticated sessions

## Requirements

- Python 3.10+
- Anthropic API key (Claude Sonnet access)
- Internet connection for font loading (Google Fonts)
