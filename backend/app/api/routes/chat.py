from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_rag_service
from app.services.rag import RAGConfigurationError, RAGIndexNotFoundError, RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    message: str


@router.post("")
def chat(
    payload: ChatMessage,
    rag_service: RAGService = Depends(get_rag_service),
):
    question = payload.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        response_text = rag_service.answer(question)
        return {"response": response_text}
    except RAGConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RAGIndexNotFoundError:
        raise HTTPException(status_code=400, detail="RAG index is missing. Please ingest CVs first.") from None
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to generate chat response.") from exc
