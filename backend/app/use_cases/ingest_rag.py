from app.domain.rag.service import RAGService


class IngestRagUseCase:
    def __init__(self, service: RAGService) -> None:
        self._service = service

    def execute(self) -> int:
        return self._service.ingest()
