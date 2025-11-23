from pathlib import Path
from typing import Protocol


class CVStorage(Protocol):
    """Storage interface for CV PDF files."""

    def list_pdfs(self) -> list[Path]:
        ...

    @property
    def directory(self) -> Path:
        ...


class PhotoStorage(Protocol):
    """Storage interface for candidate photos."""

    @property
    def directory(self) -> Path:
        ...

    @property
    def keep_filenames(self) -> set[str]:
        ...
