import logging
import unicodedata
from pathlib import Path
from typing import Iterable, Optional, Protocol
from uuid import uuid4

from fpdf import FPDF

from app.models.cv import CandidateProfile


class CVTextGenerator(Protocol):
    def generate(self) -> CandidateProfile:
        ...


class CandidateImageGenerator(Protocol):
    def generate(self, profile: CandidateProfile) -> Optional[Path]:
        ...


class CVGeneratorService:
    """High-level CV workflow used by HTTP handlers."""

    def __init__(
        self,
        storage_dir: Path,
        text_generator: CVTextGenerator,
        image_generator: CandidateImageGenerator,
        photo_dir: Path,
        photo_keep_names: Optional[Iterable[str]] = None,
    ) -> None:
        self.output_dir = Path(storage_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.text_generator = text_generator
        self.image_generator = image_generator
        self._photo_dir = Path(photo_dir)
        self._photo_dir.mkdir(parents=True, exist_ok=True)
        self._photo_keep_names = set(photo_keep_names or [])
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate(self) -> Path:
        self._logger.info("Starting CV generation pipeline.")
        profile = self.text_generator.generate()
        profile.photo_path = self.image_generator.generate(profile)
        pdf_path = self._render_pdf(profile)
        self._cleanup_photo(profile.photo_path)
        self._logger.info("Generated CV at %s", pdf_path)
        return pdf_path

    def list_pdf_files(self) -> list[str]:
        return sorted(path.name for path in self.output_dir.glob("*.pdf"))

    def _render_pdf(self, profile: CandidateProfile) -> Path:
        filename = f"{profile.name.replace(' ', '_')}-{uuid4().hex[:8]}.pdf"
        path = self.output_dir / filename

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        photo_inserted = False
        if profile.photo_path and Path(profile.photo_path).exists():
            try:
                pdf.image(str(profile.photo_path), x=150, y=20, w=40, h=40)
                photo_inserted = True
            except RuntimeError:
                pass

        pdf.set_xy(10, 20)
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(120, 12, self._safe_text(profile.name), ln=1)
        pdf.set_font("Helvetica", "", 14)
        pdf.cell(120, 10, self._safe_text(profile.title), ln=1)

        pdf.set_font("Helvetica", size=11)
        contact_line = (
            f"{profile.contact.get('email', '')} | "
            f"{profile.contact.get('phone', '')} | "
            f"{profile.contact.get('location', '')}"
        )
        pdf.multi_cell(120, 6, self._safe_text(contact_line))
        pdf.ln(2 if photo_inserted else 5)

        if photo_inserted and pdf.get_y() < 65:
            pdf.set_xy(10, 65)

        self._section_header(pdf, "Summary")
        pdf.multi_cell(0, 6, self._safe_text(profile.summary))
        pdf.ln(2)

        self._section_header(pdf, "Experience")
        for job in profile.experience:
            pdf.set_font("Helvetica", "B", 11)
            job_header = f"{job.get('role', '')} - {job.get('company', '')}"
            pdf.cell(0, 6, self._safe_text(job_header), ln=1)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 5, self._safe_text(job.get("duration", "")), ln=1)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, self._safe_text(job.get("achievements", "")))
            pdf.ln(1)

        self._section_header(pdf, "Skills")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, self._safe_text(", ".join(profile.skills)))
        pdf.ln(2)

        self._section_header(pdf, "Education")
        for edu in profile.education:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, self._safe_text(edu.get("institution", "")), ln=1)
            pdf.set_font("Helvetica", "", 10)
            degree = f"{edu.get('degree', '')} - {edu.get('graduation_year', '')}"
            pdf.multi_cell(0, 5, self._safe_text(degree))
            pdf.ln(1)

        self._section_header(pdf, "Languages")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, self._safe_text(", ".join(profile.languages)))

        pdf.output(path)
        return path

    def _section_header(self, pdf: FPDF, title: str) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, self._safe_text(title), ln=1)
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

    def _cleanup_photo(self, photo_path: Optional[Path]) -> None:
        if not photo_path:
            return
        try:
            photo_path = Path(photo_path)
            if not photo_path.exists():
                return
            if photo_path.name in self._photo_keep_names:
                return
            photo_path.unlink()
        except OSError:
            self._logger.warning("Failed to delete temp photo %s", photo_path)

    def _safe_text(self, value: Optional[str]) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_bytes = normalized.encode("latin-1", "ignore")
        return ascii_bytes.decode("latin-1")
