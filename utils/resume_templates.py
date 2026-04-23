"""
resume_templates.py — Three PDF-quality resume templates for WeasyPrint.

Strict rules for perfect PDF output:
  - NO flexbox (display:flex) anywhere — breaks WeasyPrint page layout
  - NO Google Fonts — system fonts only (Georgia serif, Helvetica/Arial sans)
  - NO vh / vw / dvh units — pt, mm, % only
  - @page { size: A4; margin: 10mm; } on every template
  - Two-column layouts use <table> exclusively
  - Contact row = inline <span> elements separated by bullets (no flex row)
  - display:inline-block pills for skills — confirmed working in WeasyPrint
  - Solid colour backgrounds only; no linear-gradient on structural containers
  - Skills shown as CATEGORY pills via skill_categorizer.py

Typography system (consistent across all templates):
  - Name:           Georgia serif,  20-22pt, bold
  - Section titles: Georgia serif,  8.5-9pt, bold, ALL CAPS, letter-spaced
  - Job titles:     Georgia serif,  11pt,    bold
  - Body / bullets: Helvetica/Arial sans,  9.5-10pt, regular
  - Meta (dates):   Helvetica/Arial sans,  8.5pt,    regular, muted
"""

from __future__ import annotations
from models.resume_schema import ResumeData
from utils.skill_categorizer import categorize

PAGE_MARGIN_MM = 10

# ── low-level helpers ─────────────────────────────────────────────────────────

def _e(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _dr(start: str, end: str) -> str:
    return " \u2013 ".join(p for p in [start, end] if p)

def _ul(bullets: list[str]) -> str:
    if not bullets:
        return ""
    return "<ul>" + "".join(f"<li>{_e(b)}</li>" for b in bullets) + "</ul>"

def _contact_row(resume: ResumeData, color: str, size: str = "8.5pt", mt: str = "8pt") -> str:
    """Inline contact info — no flexbox, just spans separated by a bullet character."""
    parts = [_e(p) for p in [
        resume.email, resume.phone, resume.location,
        resume.linkedin, resume.website
    ] if p]
    if not parts:
        return ""
    sep = f" <span style='opacity:0.5;'>&bull;</span> "
    return (
        f"<p style='font-family:Helvetica Neue,Arial,sans-serif;"
        f"font-size:{size};color:{color};margin-top:{mt};line-height:1.9;'>"
        + sep.join(parts) + "</p>"
    )

def _pills(items: list[str], bg: str, fg: str, border: str, size: str = "8pt") -> str:
    """Render a list of strings as pill/tag spans — display:inline-block is WeasyPrint-safe."""
    if not items:
        return ""
    spans = "".join(
        f"<span style='display:inline-block;background:{bg};color:{fg};"
        f"border:0.5pt solid {border};padding:3pt 9pt;border-radius:20pt;"
        f"font-family:Helvetica Neue,Arial,sans-serif;font-size:{size};"
        f"font-weight:bold;margin:2.5pt 3pt 2.5pt 0;'>{_e(s)}</span>"
        for s in items
    )
    return f"<div style='line-height:2.2;'>{spans}</div>"

# ── section title styles ──────────────────────────────────────────────────────

def _sec(title: str, color: str, border_color: str, mt: str = "18pt") -> str:
    """Standard section heading: Georgia serif, ALL CAPS, coloured underline."""
    return (
        f"<div style='font-family:Georgia,serif;font-size:8.5pt;font-weight:bold;"
        f"text-transform:uppercase;letter-spacing:2pt;color:{color};"
        f"margin:{mt} 0 9pt;padding-bottom:4pt;"
        f"border-bottom:1.5pt solid {border_color};'>{title}</div>"
    )

def _sec_sb(title: str, color: str, border: str, mt: str = "16pt") -> str:
    """Sidebar section heading: smaller, tighter."""
    return (
        f"<div style='font-family:Georgia,serif;font-size:7.5pt;font-weight:bold;"
        f"text-transform:uppercase;letter-spacing:1.8pt;color:{color};"
        f"margin:{mt} 0 7pt;border-bottom:0.5pt solid {border};padding-bottom:3pt;'>"
        f"{title}</div>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE 1 — Executive
# Dark navy sidebar (table td) | white main content
# ─────────────────────────────────────────────────────────────────────────────

def template_executive(resume: ResumeData) -> str:
    cat_skills = categorize(resume.skills)
    skills_html   = _pills(cat_skills, "#1e3a5f", "#93c5fd", "#2d4f7a", "8pt")
    certs_html    = "".join(
        f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;"
        f"padding:3pt 0;border-bottom:0.4pt solid #1e3a5f;color:#cbd5e1;'>{_e(c)}</div>"
        for c in resume.certifications
    )
    langs_html    = "".join(
        f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;"
        f"padding:3pt 0;border-bottom:0.4pt solid #1e3a5f;color:#cbd5e1;'>{_e(l)}</div>"
        for l in resume.languages
    )

    exp_html = ""
    for exp in resume.experience:
        exp_html += f"""
<table style='width:100%;border-collapse:collapse;margin-bottom:4pt;'>
  <tr>
    <td style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#111827;padding:0;vertical-align:top;'>{_e(exp.title)}</td>
    <td style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;color:#6b7280;white-space:nowrap;text-align:right;padding:0 0 0 6pt;vertical-align:top;'>{_e(_dr(exp.start_date,exp.end_date))}</td>
  </tr>
</table>
<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#4b5563;margin-bottom:5pt;'>{_e(exp.company)}{(" &bull; "+_e(exp.location)) if exp.location else ""}</div>
{_ul(exp.bullets)}
<div style='margin-bottom:12pt;'></div>"""

    edu_html = ""
    for edu in resume.education:
        gpa = f" &bull; GPA {_e(edu.gpa)}" if edu.gpa else ""
        edu_html += f"""
<table style='width:100%;border-collapse:collapse;margin-bottom:3pt;'>
  <tr>
    <td style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#111827;padding:0;vertical-align:top;'>{_e(edu.degree)}{(" in "+_e(edu.field_of_study)) if edu.field_of_study else ""}</td>
    <td style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;color:#6b7280;white-space:nowrap;text-align:right;padding:0 0 0 6pt;vertical-align:top;'>{_e(_dr(edu.start_date,edu.end_date))}</td>
  </tr>
</table>
<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#4b5563;margin-bottom:12pt;'>{_e(edu.institution)}{gpa}</div>"""

    sb_contact = "".join(
        f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8pt;"
        f"margin-bottom:5pt;color:#cbd5e1;word-break:break-all;'>{_e(p)}</div>"
        for p in [resume.email, resume.phone, resume.location, resume.linkedin, resume.website] if p
    )

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
@page {{ size: A4; margin: {PAGE_MARGIN_MM}mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #fff; font-size: 10pt; color: #374151; line-height: 1.55; overflow-wrap: anywhere; }}
table.outer {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
td.sidebar {{ width: 185pt; background: #0f2240; color: #e2e8f0; padding: 24pt 14pt 28pt 15pt; vertical-align: top; }}
td.main {{ padding: 24pt 24pt 24pt 22pt; vertical-align: top; }}
ul {{ padding-left: 13pt; margin: 2pt 0 0; }}
ul li {{ font-family: Helvetica Neue, Arial, sans-serif; font-size: 9.5pt; color: #374151; line-height: 1.6; margin-bottom: 2pt; }}
</style></head><body>
<table class="outer"><tr>
  <td class="sidebar">
    <div style="font-family:Georgia,'Times New Roman',serif;font-size:19pt;font-weight:bold;color:#fff;line-height:1.25;">{_e(resume.name)}</div>
    <div style="margin-top:14pt;">{sb_contact}</div>
    {(_sec_sb("Skills","#60a5fa","#1e3a5f","14pt")+skills_html) if cat_skills else ""}
    {(_sec_sb("Certifications","#60a5fa","#1e3a5f")+certs_html) if resume.certifications else ""}
    {(_sec_sb("Languages","#60a5fa","#1e3a5f")+langs_html) if resume.languages else ""}
  </td>
  <td class="main">
    {(_sec("Profile","#0f2240","#0f2240","0")+f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:10pt;color:#374151;line-height:1.72;'>{_e(resume.summary)}</div>") if resume.summary else ""}
    {(_sec("Experience","#0f2240","#0f2240")+exp_html) if resume.experience else ""}
    {(_sec("Education","#0f2240","#0f2240")+edu_html) if resume.education else ""}
  </td>
</tr></table>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE 2 — Modern
# Solid teal header bar | single-column body with generous padding
# ─────────────────────────────────────────────────────────────────────────────

def template_modern(resume: ResumeData) -> str:
    cat_skills = categorize(resume.skills)
    skills_pills = _pills(cat_skills, "#f0fdf9", "#0f766e", "#6ee7b7", "8.5pt")

    exp_html = ""
    for exp in resume.experience:
        exp_html += f"""
<div style='margin-bottom:16pt;padding-bottom:16pt;border-bottom:0.5pt solid #e5e7eb;'>
  <table style='width:100%;border-collapse:collapse;margin-bottom:3pt;'>
    <tr>
      <td style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#111827;padding:0;vertical-align:top;'>{_e(exp.title)}</td>
      <td style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;color:#9ca3af;white-space:nowrap;text-align:right;padding:0 0 0 8pt;vertical-align:top;'>{_e(_dr(exp.start_date,exp.end_date))}</td>
    </tr>
  </table>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#6b7280;margin-bottom:6pt;'>{_e(exp.company)}{(" &middot; "+_e(exp.location)) if exp.location else ""}</div>
  {_ul(exp.bullets)}
</div>"""

    edu_html = ""
    for edu in resume.education:
        gpa = f" &middot; GPA {_e(edu.gpa)}" if edu.gpa else ""
        edu_html += f"""
<div style='margin-bottom:12pt;'>
  <table style='width:100%;border-collapse:collapse;margin-bottom:2pt;'>
    <tr>
      <td style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#111827;padding:0;vertical-align:top;'>{_e(edu.degree)}{(" &middot; "+_e(edu.field_of_study)) if edu.field_of_study else ""}</td>
      <td style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;color:#9ca3af;white-space:nowrap;text-align:right;padding:0 0 0 8pt;vertical-align:top;'>{_e(_dr(edu.start_date,edu.end_date))}</td>
    </tr>
  </table>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#6b7280;'>{_e(edu.institution)}{gpa}</div>
</div>"""

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
@page {{ size: A4; margin: {PAGE_MARGIN_MM}mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #fff; font-size: 10pt; color: #374151; line-height: 1.6; overflow-wrap: anywhere; }}
ul {{ padding-left: 14pt; margin: 4pt 0 0; }}
ul li {{ font-family: Helvetica Neue, Arial, sans-serif; font-size: 9.5pt; color: #4b5563; line-height: 1.65; margin-bottom: 2.5pt; }}
</style></head><body>
<div style="background:#0d9488;color:white;padding:26pt 34pt 22pt;">
  <div style="font-family:Georgia,'Times New Roman',serif;font-size:22pt;font-weight:bold;letter-spacing:-0.3pt;">{_e(resume.name)}</div>
  {_contact_row(resume,"rgba(255,255,255,0.88)","8.5pt","9pt")}
</div>
<div style="padding:8pt 34pt 28pt;">
  {(_sec("About","#0d9488","#99f6e4","18pt")+f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:10pt;color:#374151;line-height:1.75;'>{_e(resume.summary)}</div>") if resume.summary else ""}
  {(_sec("Skills","#0d9488","#99f6e4")+skills_pills) if cat_skills else ""}
  {(_sec("Experience","#0d9488","#99f6e4")+exp_html) if resume.experience else ""}
  {(_sec("Education","#0d9488","#99f6e4")+edu_html) if resume.education else ""}
</div>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE 3 — Creative
# Solid indigo header | stacked highlight panels + timeline content
# Avoids a single large table row so PDF pagination can split naturally
# ─────────────────────────────────────────────────────────────────────────────

def template_creative(resume: ResumeData) -> str:
    cat_skills  = categorize(resume.skills)
    skills_html = _pills(cat_skills, "#ede9fe", "#4338ca", "#a5b4fc", "8pt")
    certs_html  = "".join(
        f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;"
        f"color:#312e81;font-weight:600;padding:3.5pt 0;border-bottom:0.5pt solid #ede9fe;'>"
        f"{_e(c)}</div>" for c in resume.certifications
    )
    langs_html  = "".join(
        f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8.5pt;"
        f"color:#312e81;font-weight:600;padding:3.5pt 0;border-bottom:0.5pt solid #ede9fe;'>"
        f"{_e(l)}</div>" for l in resume.languages
    )

    exp_html = ""
    for exp in resume.experience:
        exp_html += f"""
<div style='border-left:3pt solid #6366f1;padding-left:11pt;margin-bottom:15pt;'>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8pt;color:#7c3aed;font-weight:bold;text-transform:uppercase;letter-spacing:0.9pt;margin-bottom:2pt;'>{_e(_dr(exp.start_date,exp.end_date))}</div>
  <div style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#1e1b4b;'>{_e(exp.title)}</div>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#6b7280;margin:2pt 0 5pt;'>{_e(exp.company)}{(" &middot; "+_e(exp.location)) if exp.location else ""}</div>
  {_ul(exp.bullets)}
</div>"""

    edu_html = ""
    for edu in resume.education:
        edu_html += f"""
<div style='border-left:3pt solid #6366f1;padding-left:11pt;margin-bottom:14pt;'>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:8pt;color:#7c3aed;font-weight:bold;text-transform:uppercase;letter-spacing:0.9pt;margin-bottom:2pt;'>{_e(_dr(edu.start_date,edu.end_date))}</div>
  <div style='font-family:Georgia,serif;font-size:11pt;font-weight:bold;color:#1e1b4b;'>{_e(edu.degree)}{(" &middot; "+_e(edu.field_of_study)) if edu.field_of_study else ""}</div>
  <div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:9pt;color:#6b7280;margin-top:2pt;'>{_e(edu.institution)}</div>
</div>"""

    highlight_sections = ""
    if cat_skills:
        highlight_sections += (
            f"<div class='panel'>"
            f"{_sec_sb('Skills','#4f46e5','#c4b5fd','0')}"
            f"{skills_html}"
            f"</div>"
        )
    if resume.languages:
        highlight_sections += (
            f"<div class='panel'>"
            f"{_sec_sb('Languages','#4f46e5','#c4b5fd','0')}"
            f"{langs_html}"
            f"</div>"
        )
    if resume.certifications:
        highlight_sections += (
            f"<div class='panel'>"
            f"{_sec_sb('Certifications','#4f46e5','#c4b5fd','0')}"
            f"{certs_html}"
            f"</div>"
        )

    exp_block = ""
    if resume.experience:
        exp_entries = exp_html.replace(
            "<div style='border-left:3pt solid #6366f1;",
            "<div class='entry' style='border-left:3pt solid #6366f1;",
        )
        exp_block = _sec("Experience", "#4f46e5", "#c4b5fd") + exp_entries

    edu_block = ""
    if resume.education:
        edu_entries = edu_html.replace(
            "<div style='border-left:3pt solid #6366f1;",
            "<div class='entry' style='border-left:3pt solid #6366f1;",
        )
        edu_block = _sec("Education", "#4f46e5", "#c4b5fd") + edu_entries

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
@page {{ size: A4; margin: {PAGE_MARGIN_MM}mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #fff; font-size: 10pt; color: #374151; line-height: 1.55; overflow-wrap: anywhere; }}
.content {{ padding: 18pt 18pt 10pt; }}
.highlight-band {{ margin: 0 18pt 10pt; padding: 12pt 14pt 4pt; background:#f5f3ff; border:0.5pt solid #ddd6fe; }}
.panel {{ margin-bottom: 12pt; page-break-inside: avoid; }}
.entry {{ page-break-inside: avoid; }}
ul {{ padding-left: 13pt; margin: 3pt 0 0; }}
ul li {{ font-family: Helvetica Neue, Arial, sans-serif; font-size: 9.5pt; color: #4b5563; line-height: 1.6; margin-bottom: 2pt; }}
</style></head><body>
<div style="background:#312e81;color:white;padding:24pt 20pt 18pt;">
  <div style="font-family:Georgia,'Times New Roman',serif;font-size:21pt;font-weight:bold;letter-spacing:-0.3pt;">{_e(resume.name)}</div>
  {_contact_row(resume,"rgba(255,255,255,0.82)","8.5pt","8pt")}
</div>
{(f"<div class='highlight-band'>{highlight_sections}</div>") if highlight_sections else ""}
<div class="content">
  {(_sec("About","#4f46e5","#c4b5fd","0")+f"<div style='font-family:Helvetica Neue,Arial,sans-serif;font-size:10pt;color:#374151;line-height:1.75;'>{_e(resume.summary)}</div>") if resume.summary else ""}
  {exp_block}
  {edu_block}
</div>
</body></html>"""


# ── Registry ──────────────────────────────────────────────────────────────────

TEMPLATES = {
    "executive": {
        "name": "Executive",
        "description": "Classic corporate: navy sidebar, serif headings",
        "emoji": "🏛️",
        "fn": template_executive,
    },
    "modern": {
        "name": "Modern",
        "description": "Clean minimalist with teal accent header",
        "emoji": "💎",
        "fn": template_modern,
    },
    "creative": {
        "name": "Creative",
        "description": "Bold indigo header, timeline accents, two-column",
        "emoji": "🎨",
        "fn": template_creative,
    },
}


def render_template(template_key: str, resume: ResumeData) -> str:
    tpl = TEMPLATES.get(template_key)
    if not tpl:
        raise ValueError(f"Unknown template: {template_key!r}")
    return tpl["fn"](resume)
