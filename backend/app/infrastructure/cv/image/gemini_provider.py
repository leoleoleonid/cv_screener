import logging
from pathlib import Path
from uuid import uuid4

from google import genai
from google.genai import types as genai_types
from PIL import Image, ImageDraw

from app.domain.cv.interfaces import CandidateImageGenerator
from app.domain.cv.models import CandidateProfile


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
