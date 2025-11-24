import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from google import genai
from google.genai import types as genai_types
from PIL import Image, ImageDraw

from app.domain.models import CandidateProfile
from app.services.cv_generator import CandidateImageGenerator


class MockImageGenerator(CandidateImageGenerator):
    """Local placeholder image provider used for development and tests."""

    def __init__(self, photos_dir: Path, seed_file: Optional[Path] = None) -> None:
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.seed_file = seed_file or self.photos_dir / "placeholder.png"
        if not self.seed_file.exists():
            self._create_seed_file()
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate(self, profile: CandidateProfile) -> Path:
        self._logger.info("Using mock image generator.")
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
    """Gemini-powered headshot generator."""

    def __init__(self, api_key: str, model_name: str, photos_dir: Path) -> None:
        self.photos_dir = Path(photos_dir)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.client = genai.Client(api_key=api_key) if api_key and model_name else None
        self._logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name

    def generate(self, profile: CandidateProfile) -> Path:
        if not self.client or not self.model_name:
            raise RuntimeError("Gemini credentials are not configured; cannot generate photo.")

        self._logger.info("Generating candidate photo via Gemini image model.")
        descriptor = self._gender_descriptor(profile.gender)
        prompt = (
            f"Professional corporate headshot of a {descriptor}, medium close-up, neutral background, "
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
        except Exception as exc:
            self._logger.exception("Gemini image generation failed.")
            raise RuntimeError("Failed to generate photo via Gemini.") from exc
        raise RuntimeError("Gemini returned no images for the request.")

    def _placeholder_photo(self, profile: CandidateProfile) -> Path:
        filename = self.photos_dir / f"placeholder-{uuid4().hex[:8]}.png"
        image = Image.new("RGB", (512, 512), color=(40, 70, 120))
        draw = ImageDraw.Draw(image)
        draw.ellipse((120, 80, 392, 420), fill=(217, 180, 145))
        draw.rectangle((60, 330, 452, 520), fill=(20, 45, 90))
        draw.text((160, 230), profile.title[:10], fill=(255, 255, 255))
        image.save(filename)
        return filename

    def _gender_descriptor(self, gender: Optional[str]) -> str:
        normalized = (gender or "").strip().lower()
        if normalized in {"female", "woman", "female-presenting"}:
            return "female professional"
        if normalized in {"male", "man", "male-presenting"}:
            return "male professional"
        if normalized in {"non-binary", "nonbinary", "genderqueer"}:
            return "non-binary professional"
        return "professional candidate"
