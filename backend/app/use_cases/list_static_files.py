from app.domain.storage import CVStorage


class ListStaticFilesUseCase:
    def __init__(self, storage: CVStorage) -> None:
        self._storage = storage

    def execute(self) -> list[str]:
        return sorted(path.name for path in self._storage.list_pdfs())
