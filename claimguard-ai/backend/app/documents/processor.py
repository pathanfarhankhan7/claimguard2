from pathlib import Path
from typing import Any

import fitz
from docx import Document


def extract_text_from_pdf(path: Path) -> str:
    text = ''
    with fitz.open(path) as doc:
        for p in doc:
            text += p.get_text() + '\n'
    return text.strip()


def extract_text_from_docx(path: Path) -> str:
    d = Document(path)
    return '\n'.join(p.text for p in d.paragraphs).strip()


def extract_text(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        txt = extract_text_from_pdf(path)
    elif suffix == '.docx':
        txt = extract_text_from_docx(path)
    elif suffix in {'.txt', '.md'}:
        txt = path.read_text(encoding='utf-8', errors='ignore')
    elif suffix in {'.png', '.jpg', '.jpeg'}:
        txt = ''
    else:
        raise ValueError('Unsupported document type')
    return {'filename': path.name, 'content_type': suffix, 'extracted_text': txt}
