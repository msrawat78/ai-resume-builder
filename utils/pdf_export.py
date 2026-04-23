"""
pdf_export.py — Converts HTML resume templates to downloadable PDFs.
Uses WeasyPrint (preferred) with xhtml2pdf as fallback.
"""

from __future__ import annotations


def html_to_pdf(html: str) -> bytes:
    """
    Convert an HTML string to PDF bytes.
    Tries WeasyPrint first, falls back to xhtml2pdf.
    """
    # ── WeasyPrint (best quality) ─────────────────────────────────────────
    try:
        from weasyprint import HTML, CSS

        # Inject print-safe CSS reset
        extra_css = CSS(string="""
            @page { size: A4; margin: 10mm; }
            html, body { width: 100%; }
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        """)
        pdf_bytes = HTML(string=html).write_pdf(stylesheets=[extra_css])
        return pdf_bytes
    except ImportError:
        pass
    except Exception as e:
        # WeasyPrint installed but failed — fall through
        print(f"[WeasyPrint] {e}")

    # ── xhtml2pdf fallback ────────────────────────────────────────────────
    try:
        import io
        from xhtml2pdf import pisa

        buf = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buf)
        if result.err:
            raise RuntimeError(f"xhtml2pdf error code {result.err}")
        return buf.getvalue()
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library available. Install WeasyPrint: pip install weasyprint"
    )
