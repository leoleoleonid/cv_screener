from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.core.deps import get_rag_service
from app.services.rag import RAGConfigurationError, RAGIndexNotFoundError, RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    question = payload.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        response_text = rag_service.answer(question)
        return ChatResponse(response=response_text)
    except RAGConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RAGIndexNotFoundError:
        raise HTTPException(status_code=400, detail="RAG index is missing. Please ingest CVs first.") from None
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to generate chat response.") from exc
