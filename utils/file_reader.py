"""
file_reader.py — Extracts plain text from uploaded PDF and DOCX files.
"""

import io
from typing import Optional


def read_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file given its raw bytes.
    Uses PyMuPDF (fitz) for reliable text extraction.
    Falls back to pdfminer if fitz is unavailable.
    """
    text_parts = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts).strip()
    except ImportError:
        pass

    # Fallback: pdfminer.six
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams

        output = io.StringIO()
        extract_text_to_fp(
            io.BytesIO(file_bytes),
            output,
            laparams=LAParams(),
            output_type="text",
            codec="utf-8",
        )
        return output.getvalue().strip()
    except Exception as e:
        raise RuntimeError(f"Could not extract text from PDF: {e}")


def read_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file given its raw bytes.
    Preserves paragraph structure.
    """
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        raise RuntimeError(f"Could not extract text from DOCX: {e}")


def read_uploaded_file(file_obj) -> Optional[str]:
    """
    Dispatch to the correct reader based on file extension.

    Args:
        file_obj: A Streamlit UploadedFile object.

    Returns:
        Extracted text string, or None on failure.
    """
    if file_obj is None:
        return None

    file_bytes = file_obj.read()
    name = file_obj.name.lower()

    if name.endswith(".pdf"):
        return read_pdf(file_bytes)
    elif name.endswith(".docx"):
        return read_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_obj.name}")
