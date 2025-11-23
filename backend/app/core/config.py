import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
DEFAULT_CORS = ["http://localhost:3000", "http://127.0.0.1:3000"]
DEFAULT_PLACEHOLDER_PHOTO = "placeholder.png"
DEFAULT_RAG_CHUNK_SIZE = 1000
DEFAULT_RAG_CHUNK_OVERLAP = 200
DEFAULT_RAG_RETRIEVAL_K = 4

load_dotenv(ENV_PATH)


def _env(key: str, default: str = "") -> str:
    value = os.getenv(key, "").strip()
    return value or default


def _directory_env(key: str, fallback: str) -> Path:
    raw = _env(key, fallback)
    path = Path(raw)
    if not path.is_absolute():
        path = BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS")
    if not raw:
        return DEFAULT_CORS
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    static_dir: Path
    rag_index_dir: Path
    photos_dir: Path
    cors_origins: List[str]
    google_genai_api_key: str
    google_genai_model_name: str
    google_genai_image_model_name: str
    google_rag_embedding_model: str
    google_rag_chat_model: str
    placeholder_photo: str
    rag_chunk_size: int
    rag_chunk_overlap: int
    rag_retriever_k: int

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            static_dir=_directory_env("STATIC_DIR", "static"),
            rag_index_dir=_directory_env("RAG_INDEX_DIR", "cv_faiss_index"),
            photos_dir=_directory_env("PHOTOS_DIR", "photos"),
            cors_origins=_cors_origins(),
            google_genai_api_key=_env("GOOGLE_GENAI_API_KEY"),
            google_genai_model_name=_env("GOOGLE_GENAI_MODEL_NAME", "gemini-2.0-flash"),
            google_genai_image_model_name=_env(
                "GOOGLE_GENAI_IMAGE_MODEL_NAME", "imagen-4.0-fast-generate-001"
            ),
            google_rag_embedding_model=_env(
                "GOOGLE_RAG_EMBEDDING_MODEL",
                _env("GOOGLE_GENAI_EMBEDDING_MODEL_NAME", "models/text-embedding-004"),
            ),
            google_rag_chat_model=_env(
                "GOOGLE_RAG_CHAT_MODEL", _env("GOOGLE_GENAI_MODEL_NAME", "gemini-2.0-flash")
            ),
            placeholder_photo=DEFAULT_PLACEHOLDER_PHOTO,
            rag_chunk_size=int(_env("RAG_CHUNK_SIZE", str(DEFAULT_RAG_CHUNK_SIZE))),
            rag_chunk_overlap=int(_env("RAG_CHUNK_OVERLAP", str(DEFAULT_RAG_CHUNK_OVERLAP))),
            rag_retriever_k=int(_env("RAG_RETRIEVER_K", str(DEFAULT_RAG_RETRIEVAL_K))),
        )
