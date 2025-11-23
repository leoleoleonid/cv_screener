from pathlib import Path

from app.domain.cv.service import CVService


class GenerateCvUseCase:
    def __init__(self, service: CVService) -> None:
        self._service = service

    def execute(self) -> Path:
        return self._service.generate()
