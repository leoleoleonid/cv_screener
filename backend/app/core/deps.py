from functools import lru_cache

from fastapi import Depends

from app.core.config import AppSettings
from app.services.cv_generator import CVGeneratorService
from app.services.rag import RAGService
from app.wiring.container import build_cv_generator, build_mock_cv_generator, build_rag_service


@lru_cache
def get_settings() -> AppSettings:
    settings = AppSettings()
    settings.ensure_directories()
    return settings


def get_cv_generator(settings: AppSettings = Depends(get_settings)) -> CVGeneratorService:
    return build_cv_generator(settings)


def get_mock_cv_generator(settings: AppSettings = Depends(get_settings)) -> CVGeneratorService:
    return build_mock_cv_generator(settings)


def get_rag_service(settings: AppSettings = Depends(get_settings)) -> RAGService:
    return build_rag_service(settings)
