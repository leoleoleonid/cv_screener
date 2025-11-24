from pathlib import Path
from typing import List

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CORS = ["http://localhost:3000", "http://127.0.0.1:3000"]
DEFAULT_RAG_CHUNK_SIZE = 1000
DEFAULT_RAG_CHUNK_OVERLAP = 200
DEFAULT_RAG_RETRIEVAL_K = 4


class AppSettings(BaseSettings):
    """Central application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "AI CV Screener API"
    cors_origins: List[str] = Field(default_factory=lambda: DEFAULT_CORS)

    # Directories
    static_dir: Path = BASE_DIR / "static"
    rag_index_dir: Path = BASE_DIR / "cv_faiss_index"
    photos_dir: Path = BASE_DIR / "photos"
    placeholder_photo: str = "placeholder.png"
    use_mock_generators: bool = False

    # Gemini / Google GenAI
    google_genai_api_key: str = ""
    google_genai_model_name: str = "gemini-2.0-flash"
    google_genai_image_model_name: str = "imagen-4.0-fast-generate-001"
    google_rag_embedding_model: str = "models/text-embedding-004"
    google_rag_chat_model: str = "gemini-2.0-flash"

    # RAG
    rag_chunk_size: int = DEFAULT_RAG_CHUNK_SIZE
    rag_chunk_overlap: int = DEFAULT_RAG_CHUNK_OVERLAP
    rag_retriever_k: int = DEFAULT_RAG_RETRIEVAL_K

    # Celery / infrastructure
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "db+postgresql+psycopg2://ai:ai@postgres:5432/ai_cv"

    @model_validator(mode="after")
    def _normalize_paths(self) -> "AppSettings":
        for attr in ("static_dir", "rag_index_dir", "photos_dir"):
            path = Path(getattr(self, attr))
            if not path.is_absolute():
                path = (BASE_DIR / path).resolve()
            setattr(self, attr, path)
        return self

    @model_validator(mode="after")
    def _split_cors(self) -> "AppSettings":
        raw = self.cors_origins
        if isinstance(raw, str):
            self.cors_origins = [item.strip() for item in raw.split(",") if item.strip()]
        return self

    def ensure_directories(self) -> None:
        """Create required directories up front."""
        for path in (self.static_dir, self.rag_index_dir, self.photos_dir):
            Path(path).mkdir(parents=True, exist_ok=True)
