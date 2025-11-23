from pathlib import Path

import pytest

from app.use_cases.chat_with_rag import ChatWithRagUseCase
from app.use_cases.generate_cv import GenerateCvUseCase
from app.use_cases.generate_mock_cv import GenerateMockCvUseCase
from app.use_cases.get_cv_texts import GetCvTextsUseCase
from app.use_cases.ingest_rag import IngestRagUseCase
from app.use_cases.list_static_files import ListStaticFilesUseCase


class FakeStorage:
    def __init__(self, files: list[Path]) -> None:
        self._files = files

    def list_pdfs(self) -> list[Path]:
        return self._files

    @property
    def directory(self) -> Path:
        return Path("/tmp")


class FakeCvService:
    def __init__(self, path: Path) -> None:
        self._path = path

    def generate(self) -> Path:
        return self._path


class FakeCvTextExtractor:
    def __init__(self, payload: dict[str, str]) -> None:
        self._payload = payload

    def extract_texts(self) -> dict[str, str]:
        return self._payload


class FakeRagService:
    def __init__(self, answer: str = "ok", documents: int = 0, error: Exception | None = None) -> None:
        self._answer = answer
        self._documents = documents
        self._error = error

    def ingest(self) -> int:
        if self._error:
            raise self._error
        return self._documents

    def answer(self, question: str) -> str:
        if self._error:
            raise self._error
        return f"{self._answer}:{question}"


def test_list_static_files_use_case_returns_names_sorted():
    files = [Path("/tmp/b.pdf"), Path("/tmp/a.pdf")]
    use_case = ListStaticFilesUseCase(storage=FakeStorage(files))
    assert use_case.execute() == ["a.pdf", "b.pdf"]


def test_generate_cv_use_cases_return_paths():
    expected = Path("/tmp/generated.pdf")
    use_case = GenerateCvUseCase(service=FakeCvService(expected))
    assert use_case.execute() == expected

    mock_use_case = GenerateMockCvUseCase(service=FakeCvService(expected))
    assert mock_use_case.execute() == expected


def test_get_cv_texts_use_case_returns_payload():
    payload = {"file.pdf": "content"}
    use_case = GetCvTextsUseCase(service=FakeCvTextExtractor(payload))
    assert use_case.execute() == payload


def test_chat_use_case_returns_formatted_answer():
    rag_service = FakeRagService(answer="answer")
    use_case = ChatWithRagUseCase(service=rag_service)
    assert use_case.execute("Who?") == "answer:Who?"


def test_chat_use_case_propagates_errors():
    rag_service = FakeRagService(error=ValueError("boom"))
    use_case = ChatWithRagUseCase(service=rag_service)
    with pytest.raises(ValueError):
        use_case.execute("test")


def test_ingest_rag_use_case_returns_document_count():
    rag_service = FakeRagService(documents=3)
    use_case = IngestRagUseCase(service=rag_service)
    assert use_case.execute() == 3
