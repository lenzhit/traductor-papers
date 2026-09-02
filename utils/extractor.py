import io
from typing import Optional
import pypdf
import docx

def extract_text_from_file(file_obj, filename: str) -> str:
    """
    Extrae texto de un archivo subido (PDF, DOCX o TXT).
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_obj)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_obj)
    elif ext in ['txt', 'md', 'tex']:
        return extract_text_from_plain(file_obj)
    else:
        raise ValueError(f"Formato de archivo no soportado: .{ext}")

def extract_text_from_pdf(file_obj) -> str:
    """Extrae texto página por página de un PDF."""
    reader = pypdf.PdfReader(file_obj)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())
    return "\n\n".join(pages_text)

def extract_text_from_docx(file_obj) -> str:
    """Extrae texto de un documento DOCX."""
    doc = docx.Document(file_obj)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

def extract_text_from_plain(file_obj) -> str:
    """Extrae texto de archivos de texto plano (TXT, MD, TEX)."""
    if isinstance(file_obj, (bytes, bytearray)):
        return file_obj.decode("utf-8", errors="replace")
    content = file_obj.read()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return str(content)
