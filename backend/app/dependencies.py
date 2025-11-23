from functools import lru_cache

from app.config import Settings
from app.domain.cv.service import CVService
from app.domain.storage import CVStorage, PhotoStorage
from app.infrastructure.cv.image.gemini_provider import GeminiImageGenerator
from app.infrastructure.cv.image.mock_provider import MockImageGenerator
from app.infrastructure.cv.text.gemini_provider import GeminiCVTextGenerator
from app.infrastructure.cv.text.mock_provider import MockCVTextGenerator
from app.infrastructure.storage.filesystem import FileSystemCVStorage, FileSystemPhotoStorage
from app.services.cvs_preprocessing_service import CVSPreprocessingService
from app.domain.rag.service import RAGService
from app.use_cases.chat_with_rag import ChatWithRagUseCase
from app.use_cases.generate_cv import GenerateCvUseCase
from app.use_cases.generate_mock_cv import GenerateMockCvUseCase
from app.use_cases.get_cv_texts import GetCvTextsUseCase
from app.use_cases.ingest_rag import IngestRagUseCase
from app.use_cases.list_static_files import ListStaticFilesUseCase


@lru_cache
def get_settings() -> Settings:
    return Settings.load()


@lru_cache
def get_cv_storage() -> CVStorage:
    settings = get_settings()
    return FileSystemCVStorage(settings.static_dir)


@lru_cache
def get_photo_storage() -> PhotoStorage:
    settings = get_settings()
    return FileSystemPhotoStorage(settings.photos_dir, keep_filenames={"placeholder.png"})


@lru_cache
def get_cv_text_generator():
    settings = get_settings()
    return GeminiCVTextGenerator(
        api_key=settings.google_genai_api_key,
        model_name=settings.google_genai_model_name,
    )


@lru_cache
def get_photo_generator():
    settings = get_settings()
    photo_storage = get_photo_storage()
    return GeminiImageGenerator(
        api_key=settings.google_genai_api_key,
        model_name=settings.google_genai_image_model_name,
        photos_dir=photo_storage.directory,
    )


@lru_cache
def get_cv_service() -> CVService:
    return CVService(
        output_dir=get_cv_storage().directory,
        text_generator=get_cv_text_generator(),
        image_generator=get_photo_generator(),
        photo_keep_names=get_photo_storage().keep_filenames,
    )


@lru_cache
def get_mock_cv_service() -> CVService:
    return CVService(
        output_dir=get_cv_storage().directory,
        text_generator=MockCVTextGenerator(),
        image_generator=MockImageGenerator(photos_dir=get_photo_storage().directory),
        photo_keep_names=get_photo_storage().keep_filenames,
    )


@lru_cache
def get_cv_preprocessing_service() -> CVSPreprocessingService:
    return CVSPreprocessingService(static_dir=get_cv_storage().directory)


@lru_cache
def get_rag_service() -> RAGService:
    settings = get_settings()
    return RAGService(
        cv_service=get_cv_preprocessing_service(),
        index_dir=settings.rag_index_dir,
        embedding_model=settings.google_rag_embedding_model,
        chat_model=settings.google_rag_chat_model,
        google_api_key=settings.google_genai_api_key,
    )


@lru_cache
def get_generate_cv_use_case() -> GenerateCvUseCase:
    return GenerateCvUseCase(service=get_cv_service())


@lru_cache
def get_generate_mock_cv_use_case() -> GenerateMockCvUseCase:
    return GenerateMockCvUseCase(service=get_mock_cv_service())


@lru_cache
def get_list_static_files_use_case() -> ListStaticFilesUseCase:
    return ListStaticFilesUseCase(storage=get_cv_storage())


@lru_cache
def get_cv_texts_use_case() -> GetCvTextsUseCase:
    return GetCvTextsUseCase(service=get_cv_preprocessing_service())


@lru_cache
def get_ingest_rag_use_case() -> IngestRagUseCase:
    return IngestRagUseCase(service=get_rag_service())


@lru_cache
def get_chat_use_case() -> ChatWithRagUseCase:
    return ChatWithRagUseCase(service=get_rag_service())
