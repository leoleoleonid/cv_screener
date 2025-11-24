from pathlib import Path

from fpdf import FPDF

from app.domain.models import CandidateProfile
from app.services.cv_generator import CVGeneratorService
from app.services.rag import CVTextExtractor


class DummyTextGenerator:
    def __init__(self, name: str = "Jordan Doe") -> None:
        self._name = name

    def generate(self) -> CandidateProfile:
        return CandidateProfile(
            name=self._name,
            title="AI Engineer",
            summary="Builds delightful AI products.",
            contact={"email": "jordan@example.com", "phone": "+1", "location": "Remote"},
            experience=[
                {
                    "company": "NovaTech",
                    "role": "Engineer",
                    "duration": "2020 - Present",
                    "achievements": "Ships things.",
                }
            ],
            education=[
                {"institution": "Uni", "degree": "MSc", "graduation_year": 2019},
            ],
            skills=["Python", "FastAPI"],
            languages=["English"],
        )


class DummyImageGenerator:
    def __init__(self, photos_dir: Path) -> None:
        self.photos_dir = photos_dir

    def generate(self, profile: CandidateProfile) -> Path:
        return self.photos_dir / "placeholder.png"


def build_service(static_dir: Path, photos_dir: Path) -> CVGeneratorService:
    return CVGeneratorService(
        storage_dir=static_dir,
        text_generator=DummyTextGenerator(),
        image_generator=DummyImageGenerator(photos_dir),
        photo_dir=photos_dir,
        photo_keep_names={"placeholder.png"},
    )


def test_cv_generator_lists_sorted_files(tmp_path):
    static_dir = tmp_path / "static"
    photos_dir = tmp_path / "photos"
    static_dir.mkdir()
    photos_dir.mkdir()
    (static_dir / "b.pdf").write_bytes(b"pdf")
    (static_dir / "a.pdf").write_bytes(b"pdf")

    service = build_service(static_dir, photos_dir)
    assert service.list_pdf_files() == ["a.pdf", "b.pdf"]


def test_cv_generator_generate_creates_pdf(tmp_path):
    static_dir = tmp_path / "static"
    photos_dir = tmp_path / "photos"

    service = build_service(static_dir, photos_dir)
    generated = service.generate()
    assert generated.exists()
    assert generated.suffix == ".pdf"
    assert generated.name in service.list_pdf_files()


def test_cv_text_extractor_reads_text(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    pdf_path = static_dir / "cv.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Hello FastAPI")
    pdf.output(pdf_path)

    extractor = CVTextExtractor(static_dir=static_dir)
    texts = extractor.extract_texts()
    assert "cv.pdf" in texts
    assert "Hello" in texts["cv.pdf"]
