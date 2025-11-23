from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_rag_service
from app.services.rag import RAGConfigurationError, RAGEmptyCorpusError, RAGService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest")
def ingest_rag(
    rag_service: RAGService = Depends(get_rag_service),
):
    try:
        documents = rag_service.ingest()
        return {"message": "RAG index rebuilt.", "documents": documents}
    except (RAGConfigurationError, RAGEmptyCorpusError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to ingest CVs.") from exc
