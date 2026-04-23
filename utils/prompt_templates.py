"""
prompt_templates.py — All AI prompt templates used across the application.
Centralising prompts makes them easy to version and tune.
"""


def get_parse_prompt(raw_text: str) -> str:
    """
    Prompt that instructs the model to extract structured resume data
    and return it as strict JSON matching the ResumeData schema.
    """
    return f"""You are an expert resume parser. Extract structured information from the resume text below.

Return ONLY a valid JSON object with these exact keys (no markdown, no explanation):
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "linkedin": "string",
  "website": "string",
  "summary": "string — professional summary paragraph",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {{
      "company": "string",
      "title": "string",
      "start_date": "string",
      "end_date": "string",
      "location": "string",
      "bullets": ["bullet1", "bullet2", ...]
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string",
      "start_date": "string",
      "end_date": "string",
      "gpa": "string",
      "honors": "string"
    }}
  ],
  "certifications": ["cert1", ...],
  "languages": ["lang1", ...]
}}

Rules:
- Use empty strings "" for missing scalar fields.
- Use empty arrays [] for missing list fields.
- Do NOT invent information not present in the text.
- Keep bullet points concise (one sentence each).
- Dates should be in "Mon YYYY" or "YYYY" format.

Resume text:
---
{raw_text}
---"""


def get_improve_prompt(resume_json: str, target_role: str = "") -> str:
    """
    Prompt that instructs the model to rewrite and enhance resume content
    while keeping it truthful to the original.
    """
    role_context = f" targeting the role of {target_role}" if target_role else ""

    return f"""You are a professional resume writer with 15 years of experience helping candidates land top jobs{role_context}.

Given the structured resume data below, rewrite and enhance it to:
1. Make the professional summary compelling and results-oriented (3-4 sentences).
2. Rewrite each experience bullet using strong action verbs and quantifiable achievements where possible.
3. Ensure a clean, consistent tone throughout.
4. Keep all facts truthful — do NOT invent numbers or companies.

Return ONLY a valid JSON object in the SAME schema as the input (no markdown, no explanation).

Resume JSON:
---
{resume_json}
---"""


def get_job_tailor_prompt(resume_json: str, job_title: str, job_description: str, company: str = "") -> str:
    """
    Prompt that rewrites the resume to match a specific job description.
    Reorders/highlights relevant skills, rewrites bullets to mirror JD language,
    and updates the summary for the target role.
    """
    company_line = f" at {company}" if company else ""
    return f"""You are an expert resume coach helping a candidate tailor their resume for a specific job.

Target Role: {job_title}{company_line}

Job Description:
---
{job_description}
---

Current Resume:
---
{resume_json}
---

Your task:
1. Rewrite the professional summary to speak directly to this role and company.
2. Reorder the skills list — put the most relevant ones first.
3. Rewrite experience bullet points to mirror language and keywords from the job description where truthful.
4. Add any implicit skills evident from the experience that match the JD.
5. Do NOT invent companies, titles, or dates.
6. Keep all facts truthful.

Return ONLY a valid JSON object in the same schema as the input resume (no markdown, no explanation)."""


def get_summary_prompt(name: str, skills: list, experience: list) -> str:
    """
    Focused prompt to regenerate just the professional summary.
    """
    skill_str = ", ".join(skills[:10]) if skills else "various professional skills"
    recent_title = experience[0].get("title", "professional") if experience else "professional"
    recent_company = experience[0].get("company", "") if experience else ""
    at_company = f" at {recent_company}" if recent_company else ""

    return f"""Write a compelling 3-sentence professional summary for a resume.

Candidate: {name}
Current/Most Recent Role: {recent_title}{at_company}
Key Skills: {skill_str}

Guidelines:
- Open with a strong identity statement (role + years of experience if inferable).
- Mention 2-3 core competencies.
- Close with a value proposition or career goal.
- Avoid clichés like "hard-working", "team player", "dynamic".
- Return ONLY the summary paragraph, no quotes, no labels."""
