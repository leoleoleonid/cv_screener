import logging
from pathlib import Path
from typing import Dict

from PyPDF2 import PdfReader


class CVSPreprocessingService:
    """Extracts plain text from PDF CVs stored inside a directory."""

    def __init__(self, static_dir: Path) -> None:
        self._static_dir = static_dir
        self._logger = logging.getLogger(self.__class__.__name__)

    def extract_texts(self) -> Dict[str, str]:
        """Return mapping of PDF filename to extracted text."""
        texts: Dict[str, str] = {}
        for pdf_path in sorted(self._static_dir.glob("*.pdf")):
            if not pdf_path.is_file():
                continue
            texts[pdf_path.name] = self._extract_pdf_text(pdf_path)
        return texts

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        try:
            with pdf_path.open("rb") as file_obj:
                reader = PdfReader(file_obj)
                chunks = []
                for page in reader.pages:
                    text = page.extract_text() or ""
                    if text:
                        chunks.append(text.strip())
                return "\n\n".join(chunks).strip()
        except Exception:  # pragma: no cover - defensive logging
            self._logger.exception("Failed to extract text from %s", pdf_path)
            return ""
