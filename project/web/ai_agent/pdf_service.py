from pathlib import Path

from pypdf import PdfReader


class PDFService:
    """
    Handles PDF validation and text extraction.
    """

    ALLOWED_EXTENSIONS = {".pdf"}

    MAX_PAGES = 10

    # --------------------------------------------------

    def validate(self, pdf_path: Path):

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"{pdf_path} does not exist."
            )

        if pdf_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Only PDF files are supported."
            )

        reader = PdfReader(str(pdf_path))

        if len(reader.pages) > self.MAX_PAGES:
            raise ValueError(
                f"PDF exceeds {self.MAX_PAGES} pages."
            )

        return True

    # --------------------------------------------------

    def extract_text(
        self,
        pdf_path: Path,
    ) -> str:

        self.validate(pdf_path)

        reader = PdfReader(str(pdf_path))

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return self.clean_text(
            "\n".join(pages)
        )

    # --------------------------------------------------

    def clean_text(
        self,
        text: str,
    ) -> str:

        text = text.replace("\t", " ")

        text = text.replace("\r", "\n")

        while "\n\n\n" in text:
            text = text.replace(
                "\n\n\n",
                "\n\n",
            )

        while "  " in text:
            text = text.replace(
                "  ",
                " ",
            )

        return text.strip()

    # --------------------------------------------------

    def page_count(
        self,
        pdf_path: Path,
    ) -> int:

        reader = PdfReader(str(pdf_path))

        return len(reader.pages)