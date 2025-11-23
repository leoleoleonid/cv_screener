import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat, cv, health, rag
from app.core.config import Settings
from app.core.deps import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings: Settings = get_settings()

tags_metadata = [
    {"name": "CV", "description": "Manage CV PDFs and extracted text."},
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

app.include_router(cv.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(health.router)
