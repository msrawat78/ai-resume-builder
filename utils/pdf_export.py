"""
pdf_export.py — Converts HTML resume templates to downloadable PDFs.
Uses WeasyPrint (preferred), xhtml2pdf as secondary, and ReportLab as a
pure-Python fallback for cloud environments.
"""

from __future__ import annotations

from html import unescape
import io
import re


def _html_to_plain_lines(html: str) -> list[str]:
    """Convert resume HTML into readable plain lines for the ReportLab fallback."""
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)

    replacements = {
        r"(?i)<br\s*/?>": "\n",
        r"(?i)</p>": "\n\n",
        r"(?i)</div>": "\n",
        r"(?i)</h[1-6]>": "\n",
        r"(?i)<li[^>]*>": "\n• ",
        r"(?i)</li>": "",
        r"(?i)</tr>": "\n",
        r"(?i)</table>": "\n",
        r"(?i)</ul>": "\n",
        r"(?i)</ol>": "\n",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r"(?s)<[^>]+>", "", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [line.strip() for line in text.split("\n")]
    return [line for line in lines if line]


def _reportlab_pdf(html: str) -> bytes:
    """Build a simple, reliable PDF when HTML renderers are unavailable."""
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=HexColor("#243447"),
        spaceAfter=5,
    )
    heading_style = ParagraphStyle(
        "ResumeHeading",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=HexColor("#0D1628"),
        spaceBefore=4,
        spaceAfter=6,
    )
    name_style = ParagraphStyle(
        "ResumeName",
        parent=heading_style,
        fontSize=16,
        leading=20,
        spaceAfter=8,
    )

    story = []
    for index, line in enumerate(_html_to_plain_lines(html)):
        escaped = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        if index == 0:
            story.append(Paragraph(escaped, name_style))
            continue
        if line.isupper() and len(line) <= 40 and "@" not in line:
            story.append(Spacer(1, 4))
            story.append(Paragraph(escaped, heading_style))
            continue
        story.append(Paragraph(escaped, body_style))

    doc.build(story)
    return buffer.getvalue()


def html_to_pdf(html: str) -> bytes:
    """
    Convert an HTML string to PDF bytes.
    Tries WeasyPrint first, falls back to xhtml2pdf, then ReportLab.
    """
    try:
        from weasyprint import HTML, CSS

        extra_css = CSS(string="""
            @page { size: A4; margin: 10mm; }
            html, body { width: 100%; }
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        """)
        return HTML(string=html).write_pdf(stylesheets=[extra_css])
    except ImportError:
        pass
    except Exception as e:
        print(f"[WeasyPrint] {e}")

    try:
        from xhtml2pdf import pisa

        buf = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buf)
        if result.err:
            raise RuntimeError(f"xhtml2pdf error code {result.err}")
        return buf.getvalue()
    except ImportError:
        pass
    except Exception as e:
        print(f"[xhtml2pdf] {e}")

    try:
        return _reportlab_pdf(html)
    except Exception as e:
        raise RuntimeError(
            f"No PDF library available. WeasyPrint/xhtml2pdf/reportlab failed: {e}"
        ) from e
