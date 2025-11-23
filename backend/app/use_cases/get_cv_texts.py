from typing import Dict

from app.services.cvs_preprocessing_service import CVSPreprocessingService


class GetCvTextsUseCase:
    def __init__(self, service: CVSPreprocessingService) -> None:
        self._service = service

    def execute(self) -> Dict[str, str]:
        return self._service.extract_texts()
