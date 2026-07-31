from pypdf import PdfReader


def extract_resume_text(pdf_file):
    """
    Extract text from an uploaded PDF resume.
    """

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()