from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_ingest_rag_use_case
from app.domain.rag.service import (
    RAGConfigurationError,
    RAGEmptyCorpusError,
)
from app.use_cases.ingest_rag import IngestRagUseCase

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest")
def ingest_rag(
    use_case: IngestRagUseCase = Depends(get_ingest_rag_use_case),
):
    try:
        documents = use_case.execute()
        return {"message": "RAG index rebuilt.", "documents": documents}
    except (RAGConfigurationError, RAGEmptyCorpusError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to ingest CVs.") from exc
