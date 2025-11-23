from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.cv.models import CandidateProfile


class CVTextGenerator(ABC):
    @abstractmethod
    def generate(self) -> CandidateProfile:
        raise NotImplementedError


class CandidateImageGenerator(ABC):
    @abstractmethod
    def generate(self, profile: CandidateProfile) -> Path:
        raise NotImplementedError
