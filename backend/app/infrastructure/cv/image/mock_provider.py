import logging
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from app.domain.cv.interfaces import CandidateImageGenerator
from app.domain.cv.models import CandidateProfile


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
