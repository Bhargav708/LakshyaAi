import PyPDF2
from docx import Document
import io


def read_file(filename: str, content: bytes):
    # PDF
    if filename.endswith(".pdf"):
        pdf = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

        return text

    # DOCX
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])

    # TXT
    else:
        return content.decode("utf-8", errors="ignore")