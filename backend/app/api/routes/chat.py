from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_chat_use_case
from app.domain.rag.service import (
    RAGConfigurationError,
    RAGIndexNotFoundError,
)
from app.use_cases.chat_with_rag import ChatWithRagUseCase

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    message: str


@router.post("")
def chat(
    payload: ChatMessage,
    use_case: ChatWithRagUseCase = Depends(get_chat_use_case),
):
    question = payload.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        response_text = use_case.execute(question)
        return {"response": response_text}
    except RAGConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RAGIndexNotFoundError:
        raise HTTPException(status_code=400, detail="RAG index is missing. Please ingest CVs first.") from None
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to generate chat response.") from exc
