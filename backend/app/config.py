import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / ".env")


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

    @staticmethod
    def _env(key: str, default: str = "") -> str:
        return os.getenv(key, default)

    @classmethod
    def load(cls) -> "Settings":
        static_dir = cls._resolve_dir(cls._env("STATIC_DIR", "static"))
        rag_index_dir = cls._resolve_dir(cls._env("RAG_INDEX_DIR", "cv_faiss_index"))
        photos_dir = cls._resolve_dir(cls._env("PHOTOS_DIR", "photos"))
        cors_origins = [
            origin.strip()
            for origin in cls._env(
                "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ]

        return cls(
            static_dir=static_dir,
            rag_index_dir=rag_index_dir,
            photos_dir=photos_dir,
            cors_origins=cors_origins,
            google_genai_api_key=cls._env("GOOGLE_GENAI_API_KEY", ""),
            google_genai_model_name=cls._env("GOOGLE_GENAI_MODEL_NAME", "gemini-2.0-flash"),
            google_genai_image_model_name=cls._env("GOOGLE_GENAI_IMAGE_MODEL_NAME", "imagen-4.0-fast-generate-001"),
            google_rag_embedding_model=cls._env(
                "GOOGLE_RAG_EMBEDDING_MODEL",
                cls._env("GOOGLE_GENAI_EMBEDDING_MODEL_NAME", "models/text-embedding-004"),
            ),
            google_rag_chat_model=cls._env("GOOGLE_RAG_CHAT_MODEL", cls._env("GOOGLE_GENAI_MODEL_NAME", "gemini-2.0-flash")),
        )

    @staticmethod
    def _resolve_dir(path_value: str) -> Path:
        path = Path(path_value)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.mkdir(parents=True, exist_ok=True)
        return path
