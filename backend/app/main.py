import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.cv_generator import (
    CVGenerator,
    GeminiCVTextGenerator,
    GeminiImageGenerator,
    MockCVTextGenerator,
    MockImageGenerator,
)
from app.services.rag_service import (
    RAGConfigurationError,
    RAGEmptyCorpusError,
    RAGIndexNotFoundError,
    RAGService,
)
from app.services.cvs_preprocessing_service import CVSPreprocessingService

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / ".env")


def _resolve_dir(env_var: str, default_relative: str) -> Path:
    """Ensure directories can be overridden via env while supporting relative paths."""
    env_value = os.getenv(env_var)
    if env_value:
        candidate = Path(env_value)
        if not candidate.is_absolute():
            candidate = BASE_DIR / env_value
    else:
        candidate = BASE_DIR / default_relative
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
STATIC_DIR = _resolve_dir("STATIC_DIR", "static")
RAG_INDEX_DIR = _resolve_dir("RAG_INDEX_DIR", "cv_faiss_index")
PHOTOS_DIR = _resolve_dir("PHOTOS_DIR", "photos")

tags_metadata = [
    {"name": "Static Files", "description": "List and generate CV PDFs stored on disk."},
    {"name": "CV Texts", "description": "Read extracted text from stored CV PDFs."},
    {"name": "RAG", "description": "Ingest CV data and power chat responses via retrieval."},
    {"name": "Chat", "description": "Ask questions answered through RAG context."},
    {"name": "Health", "description": "Check backend status."},
]

app = FastAPI(
    title="AI CV Screener API",
    description="Endpoints for CV generation, PDF ingestion, and Gemini-powered RAG chat.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/static-files", tags=["Static Files"])
def list_static_files():
    files = sorted(file.name for file in STATIC_DIR.glob("*.pdf") if file.is_file())
    return {"files": files}


class ChatMessage(BaseModel):
    message: str


api_key = os.getenv("GOOGLE_GENAI_API_KEY", "")
text_model_name = os.getenv("GOOGLE_GENAI_MODEL_NAME", "gemini-2.0-flash")
image_model_name = os.getenv("GOOGLE_GENAI_IMAGE_MODEL_NAME", "imagen-4.0-fast-generate-001")
use_mock_text = os.getenv("MOCK_TEXT_GENERATION", "false").lower() == "true"
use_mock_image = os.getenv("MOCK_IMAGE_GENERATION", "false").lower() == "true"

text_generator = (
    MockCVTextGenerator()
    if use_mock_text
    else GeminiCVTextGenerator(api_key=api_key, model_name=text_model_name)
)
logger.info("Text generator configured: %s", text_generator.__class__.__name__)

image_generator = (
    MockImageGenerator(photos_dir=PHOTOS_DIR)
    if use_mock_image
    else GeminiImageGenerator(api_key=api_key, model_name=image_model_name, photos_dir=PHOTOS_DIR)
)
logger.info("Image generator configured: %s", image_generator.__class__.__name__)

cv_generator = CVGenerator(
    output_dir=STATIC_DIR,
    text_generator=text_generator,
    image_generator=image_generator,
    photo_keep_names={"placeholder.png"},
)

cv_preprocessing_service = CVSPreprocessingService(static_dir=STATIC_DIR)

rag_embedding_model = (
    os.getenv("GOOGLE_RAG_EMBEDDING_MODEL")
    or os.getenv("GOOGLE_GENAI_EMBEDDING_MODEL_NAME")
    or "models/text-embedding-004"
)
rag_chat_model = os.getenv("GOOGLE_RAG_CHAT_MODEL") or text_model_name
rag_service = RAGService(
    cv_service=cv_preprocessing_service,
    index_dir=RAG_INDEX_DIR,
    embedding_model=rag_embedding_model,
    chat_model=rag_chat_model,
    google_api_key=api_key,
)


@app.post("/chat", tags=["Chat"])
def chat(message: ChatMessage):
    question = message.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        response_text = rag_service.answer(question)
        return {"response": response_text}
    except RAGConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RAGIndexNotFoundError:
        raise HTTPException(status_code=400, detail="RAG index is missing. Please ingest CVs first.")
    except Exception:
        logger.exception("RAG chat failed.")
        raise HTTPException(status_code=500, detail="Failed to generate chat response.")


@app.post("/static-files/generate", tags=["Static Files"])
def generate_static_file():
    pdf_path = cv_generator.generate()
    return {"message": "Generated CV", "file": pdf_path.name}


@app.get("/cv-files/text", tags=["CV Texts"])
def get_cv_file_texts():
    try:
        return cv_preprocessing_service.extract_texts()
    except Exception:
        logger.exception("Failed to extract text from CV files.")
        raise HTTPException(status_code=500, detail="Failed to read CV files")


@app.post("/rag/ingest", tags=["RAG"])
def ingest_rag():
    try:
        ingested = rag_service.ingest()
    except RAGConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RAGEmptyCorpusError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Failed to ingest CVs into RAG index.")
        raise HTTPException(status_code=500, detail="Failed to ingest CVs.")

    return {"message": "RAG index rebuilt.", "documents": ingested}


@app.get("/health", tags=["Health"])
def health():
    return {"message": "Hello from FastAPI backend 👋"}
