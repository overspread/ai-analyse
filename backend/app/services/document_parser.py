import fitz
import docx
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        if doc.page_count == 0:
            raise ValueError("PDF file has no pages")
        text = ""
        for page in doc:
            page_text = page.get_text()
            if not page_text.strip():
                continue
            text += page_text
        doc.close()
        if not text.strip():
            raise ValueError("No text could be extracted from PDF")
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        if len(doc.paragraphs) == 0:
            raise ValueError("DOCX file has no paragraphs")
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            raise ValueError("No text could be extracted from DOCX")
        return "\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
