import logging
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
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

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI()

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


@app.get("/static-files")
def list_static_files():
    files = sorted(file.name for file in STATIC_DIR.glob("*.pdf") if file.is_file())
    return {"files": files}


class ChatMessage(BaseModel):
    message: str


RESPONSES = [
    "Thanks for reaching out! We'll review your message shortly.",
    "Got it! Our AI team will get back to you with insights soon.",
    "Message received. Expect a follow-up once processing is complete.",
]

photos_dir = STATIC_DIR / "photos"
photos_dir.mkdir(parents=True, exist_ok=True)

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
    MockImageGenerator(photos_dir=photos_dir)
    if use_mock_image
    else GeminiImageGenerator(api_key=api_key, model_name=image_model_name, photos_dir=photos_dir)
)
logger.info("Image generator configured: %s", image_generator.__class__.__name__)

cv_generator = CVGenerator(
    output_dir=STATIC_DIR,
    text_generator=text_generator,
    image_generator=image_generator,
)


@app.post("/chat")
def chat(message: ChatMessage):
    response_text = random.choice(RESPONSES)
    return {"response": response_text}


@app.post("/static-files/generate")
def generate_static_file():
    pdf_path = cv_generator.generate()
    return {"message": "Generated CV", "file": pdf_path.name}


@app.get("/health")
def health():
    return {"message": "Hello from FastAPI backend 👋"}
