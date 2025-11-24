from app.core.config import AppSettings
from app.services.cv_generator import CVGeneratorService
from app.services.providers.cv_image import GeminiImageGenerator, MockImageGenerator
from app.services.providers.cv_text import GeminiCVTextGenerator, MockCVTextGenerator
from app.services.rag import CVTextExtractor, RAGService


def build_cv_generator(settings: AppSettings) -> CVGeneratorService:
    settings.ensure_directories()
    if settings.use_mock_generators or not settings.google_genai_api_key:
        return build_mock_cv_generator(settings)

    return CVGeneratorService(
        storage_dir=settings.static_dir,
        text_generator=GeminiCVTextGenerator(
            api_key=settings.google_genai_api_key,
            model_name=settings.google_genai_model_name,
        ),
        image_generator=GeminiImageGenerator(
            api_key=settings.google_genai_api_key,
            model_name=settings.google_genai_image_model_name,
            photos_dir=settings.photos_dir,
        ),
        photo_dir=settings.photos_dir,
        photo_keep_names={settings.placeholder_photo},
    )


def build_mock_cv_generator(settings: AppSettings) -> CVGeneratorService:
    settings.ensure_directories()
    return CVGeneratorService(
        storage_dir=settings.static_dir,
        text_generator=MockCVTextGenerator(),
        image_generator=MockImageGenerator(photos_dir=settings.photos_dir),
        photo_dir=settings.photos_dir,
        photo_keep_names={settings.placeholder_photo},
    )


def build_rag_service(settings: AppSettings) -> RAGService:
    settings.ensure_directories()
    return RAGService(
        text_extractor=CVTextExtractor(static_dir=settings.static_dir),
        index_dir=settings.rag_index_dir,
        embedding_model=settings.google_rag_embedding_model,
        chat_model=settings.google_rag_chat_model,
        google_api_key=settings.google_genai_api_key,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        retriever_k=settings.rag_retriever_k,
    )
