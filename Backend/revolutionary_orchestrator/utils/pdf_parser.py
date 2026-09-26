import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file page by page."""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()
