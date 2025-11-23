from app.domain.rag.service import RAGService


class ChatWithRagUseCase:
    def __init__(self, service: RAGService) -> None:
        self._service = service

    def execute(self, question: str) -> str:
        return self._service.answer(question)
