import random
import shutil
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
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


@app.post("/chat")
def chat(message: ChatMessage):
    response_text = random.choice(RESPONSES)
    return {"response": response_text}


@app.post("/static-files/generate")
def generate_static_file():
    pdf_files = list(STATIC_DIR.glob("*.pdf"))
    if not pdf_files:
        return {"message": "No source PDF available to copy."}

    source = random.choice(pdf_files)
    timestamp = int(time.time())
    new_name = f"Generated-{timestamp}.pdf"
    destination = STATIC_DIR / new_name
    shutil.copy(source, destination)
    return {"message": "Generated new PDF", "file": new_name}


@app.get("/health")
def health():
    return {"message": "Hello from FastAPI backend 👋"}
