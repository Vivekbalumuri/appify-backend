import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes and cleans it."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    # Basic cleaning
    text = re.sub(r'\n+', '\n', text)
    text = text.strip()
    return text
