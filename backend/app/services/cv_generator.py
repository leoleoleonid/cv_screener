import json
import logging
import random
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from uuid import uuid4

from google import genai
from google.genai import types as genai_types
from fpdf import FPDF
from PIL import Image, ImageDraw

@dataclass
class CandidateProfile:
    name: str
    title: str
    summary: str
    contact: Dict[str, str]
    experience: List[Dict[str, str]]
    education: List[Dict[str, str]]
    skills: List[str]
    languages: List[str]
    photo_path: Optional[Path] = None


class CVTextGenerator(ABC):
    @abstractmethod
    def generate(self) -> CandidateProfile:
        raise NotImplementedError


class CandidateImageGenerator(ABC):
    @abstractmethod
    def generate(self, profile: CandidateProfile) -> Path:
        raise NotImplementedError


class MockCVTextGenerator(CVTextGenerator):
    def __init__(self) -> None:
        self._random = random.Random()

    def generate(self) -> CandidateProfile:
        first_names = ["Avery", "Kai", "Morgan", "Sage", "River"]
        last_names = ["Singh", "Garcia", "Turner", "Patel", "Davis"]
        roles = [
            "Machine Learning Engineer",
            "Frontend Engineer",
            "Product Manager",
            "AI Researcher",
            "Security Analyst",
        ]
        locations = ["Berlin, Germany", "Austin, TX", "Toronto, Canada", "Remote"]

        name = f"{self._random.choice(first_names)} {self._random.choice(last_names)}"
        role = self._random.choice(roles)
        skills = [
            "Python",
            "TypeScript",
            "Prompt Engineering",
            "Generative AI",
            "Kubernetes",
            "LLM Fine-tuning",
        ]

        return CandidateProfile(
            name=name,
            title=role,
            summary=(
                f"{name} is a {role} with a strong record of shipping AI-powered products "
                "and mentoring cross-functional teams."
            ),
            contact={
                "email": f"{name.replace(' ', '.').lower()}@example.com",
                "phone": "+1 (555) 555-1212",
                "location": self._random.choice(locations),
            },
            experience=[
                {
                    "company": "NovaTech Labs",
                    "role": role,
                    "duration": "2021 - Present",
                    "achievements": "Leads delivery of intelligent features that increased adoption by 30%.",
                },
                {
                    "company": "Quantum Solutions",
                    "role": f"Senior {role}",
                    "duration": "2018 - 2021",
                    "achievements": "Introduced experimentation practices that cut cycle time by 20%.",
                },
            ],
            education=[
                {
                    "institution": "Metropolitan Institute of Technology",
                    "degree": "MSc Computer Science",
                    "graduation_year": 2018,
                }
            ],
            skills=skills,
            languages=["English", "German"],
        )


class GeminiCVTextGenerator(CVTextGenerator):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        fallback: Optional[CVTextGenerator] = None,
    ) -> None:
        self._client = genai.Client(api_key=api_key) if api_key and model_name else None
        self._model_name = model_name
        self._fallback = fallback or MockCVTextGenerator()
        self._logger = logging.getLogger(__name__)

    def generate(self) -> CandidateProfile:
        if not self._client or not self._model_name:
            self._logger.info("GeminiCVTextGenerator falling back to mock implementation.")
            return self._fallback.generate()

        config = genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self._get_schema(),
        )

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=self._prompt(),
                config=config,
            )
            
            payload = self._extract_json(response)
            if payload:
                return self._profile_from_payload(payload)
        except Exception:
            self._logger.exception("Gemini text generation failed, falling back to mock.")
        return self._fallback.generate()

    def _profile_from_payload(self, payload: Dict[str, object]) -> CandidateProfile:
        def _ensure_list(value: object) -> List:
            if isinstance(value, list):
                return value
            if value is None:
                return []
            return [value]

        contact = payload.get("contact") if isinstance(payload.get("contact"), dict) else {}
        experience = [item for item in _ensure_list(payload.get("experience")) if isinstance(item, dict)]
        education = [item for item in _ensure_list(payload.get("education")) if isinstance(item, dict)]
        skills = [str(skill) for skill in _ensure_list(payload.get("skills"))]
        languages = [str(lang) for lang in _ensure_list(payload.get("languages"))]

        return CandidateProfile(
            name=str(payload.get("name", "Jordan Doe")),
            title=str(payload.get("title", "AI Specialist")),
            summary=str(
                payload.get(
                    "summary",
                    "Seasoned professional experienced in AI product delivery.",
                )
            ),
            contact={
                "email": str(contact.get("email", "jordan.doe@example.com")),
                "phone": str(contact.get("phone", "+1 (555) 000-0000")),
                "location": str(contact.get("location", "Remote")),
            },
            experience=experience or [
                {
                    "company": "NovaTech Labs",
                    "role": "AI Specialist",
                    "duration": "2020 - Present",
                    "achievements": "Delivered automation with measurable business outcomes.",
                }
            ],
            education=education or [
                {
                    "institution": "Metropolitan Institute of Technology",
                    "degree": "MSc Computer Science",
                    "graduation_year": 2018,
                }
            ],
            skills=skills or ["Python", "Prompt Engineering"],
            languages=languages or ["English"],
        )

    def _prompt(self) -> str:
        return (
            "You are a CV-writing assistant. Produce a single JSON object "
            "containing all the details for a skilled professional candidate."
        )

    def _get_schema(self) -> genai_types.Schema:
        return genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                "name": genai_types.Schema(type=genai_types.Type.STRING),
                "title": genai_types.Schema(type=genai_types.Type.STRING),
                "summary": genai_types.Schema(type=genai_types.Type.STRING),
                "contact": genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "email": genai_types.Schema(type=genai_types.Type.STRING),
                        "phone": genai_types.Schema(type=genai_types.Type.STRING),
                        "location": genai_types.Schema(type=genai_types.Type.STRING),
                    },
                ),
                "experience": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "company": genai_types.Schema(type=genai_types.Type.STRING),
                            "role": genai_types.Schema(type=genai_types.Type.STRING),
                            "duration": genai_types.Schema(type=genai_types.Type.STRING),
                            "achievements": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                    ),
                ),
                "education": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "institution": genai_types.Schema(type=genai_types.Type.STRING),
                            "degree": genai_types.Schema(type=genai_types.Type.STRING),
                            "graduation_year": genai_types.Schema(type=genai_types.Type.INTEGER),
                        },
                    ),
                ),
                "skills": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(type=genai_types.Type.STRING),
                ),
                "languages": genai_types.Schema(
                    type=genai_types.Type.ARRAY,
                    items=genai_types.Schema(type=genai_types.Type.STRING),
                ),
            },
        )

    def _extract_json(self, response) -> Optional[Dict[str, object]]:
        if hasattr(response, "text") and response.text:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                self._logger.error("Gemini returned INVALID JSON *even with schema*. Raw text: %s", response.text)
                return None
        return None

class MockImageGenerator(CandidateImageGenerator):
    def __init__(self, photos_dir: Path, seed_file: Optional[Path] = None) -> None:
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.seed_file = seed_file or self.photos_dir / "placeholder.png"
        if not self.seed_file.exists():
            self._create_seed_file()

    def generate(self, profile: CandidateProfile) -> Path:
        logging.getLogger(__name__).info("Using mock image generator.")
        return self.seed_file

    def _create_seed_file(self) -> None:
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (512, 512), color=(70, 90, 140))
        draw = ImageDraw.Draw(image)
        draw.ellipse((110, 60, 402, 452), fill=(205, 170, 140))
        draw.rectangle((80, 360, 432, 520), fill=(40, 60, 110))
        draw.text((180, 230), "Mock", fill=(255, 255, 255))
        image.save(self.seed_file)


class GeminiImageGenerator(CandidateImageGenerator):
    def __init__(self, api_key: str, model_name: str, photos_dir: Path) -> None:
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.client = genai.Client(api_key=api_key) if api_key and model_name else None
        self._logger = logging.getLogger(__name__)
        self.model_name = model_name

    def generate(self, profile: CandidateProfile) -> Path:
        if not self.client or not self.model_name:
            self._logger.info("Gemini image generator missing client/model, using placeholder.")
            return self._placeholder_photo(profile)

        self._logger.info("Generating candidate photo via Gemini image model.")
        prompt = (
            "Professional corporate headshot, medium close-up, neutral background, "
            f"role: {profile.title}."
        )
        try:
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=genai_types.GenerateImagesConfig(number_of_images=1),
            )
            for generated_image in getattr(response, "generated_images", []) or []:
                image_obj = getattr(generated_image, "image", None)
                if hasattr(image_obj, "save"):
                    filename = self.photos_dir / f"photo-{uuid4().hex[:8]}.png"
                    image_obj.save(filename)
                    return filename
        except Exception:
            self._logger.exception("Gemini image generation failed, using placeholder.")
            pass
        return self._placeholder_photo(profile)

    def _placeholder_photo(self, profile: CandidateProfile) -> Path:
        filename = self.photos_dir / f"placeholder-{uuid4().hex[:8]}.png"
        image = Image.new("RGB", (512, 512), color=(40, 70, 120))
        draw = ImageDraw.Draw(image)
        draw.ellipse((120, 80, 392, 420), fill=(217, 180, 145))
        draw.rectangle((60, 330, 452, 520), fill=(20, 45, 90))
        draw.text((160, 230), profile.title[:10], fill=(255, 255, 255))
        image.save(filename)
        return filename


class CVGenerator:
    def __init__(
        self,
        output_dir: Path,
        text_generator: CVTextGenerator,
        image_generator: CandidateImageGenerator,
        photo_keep_names: Optional[Set[str]] = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.text_generator = text_generator
        self.image_generator = image_generator
        self._photo_keep_names = set(photo_keep_names or [])

    def generate(self) -> Path:
        logging.getLogger(__name__).info("Starting CV generation pipeline.")
        profile = self.text_generator.generate()
        profile.photo_path = self.image_generator.generate(profile)
        pdf_path = self._render_pdf(profile)
        self._cleanup_photo(profile.photo_path)
        logging.getLogger(__name__).info("Generated CV at %s", pdf_path)
        return pdf_path

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
            logging.getLogger(__name__).warning("Failed to delete temp photo %s", photo_path)

    def _safe_text(self, value: Optional[str]) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_bytes = normalized.encode("latin-1", "ignore")
        return ascii_bytes.decode("latin-1")
