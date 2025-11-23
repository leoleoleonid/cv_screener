from pathlib import Path
from typing import Iterable, List, Set

from app.domain.storage import CVStorage, PhotoStorage


class FileSystemCVStorage(CVStorage):
    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._directory.mkdir(parents=True, exist_ok=True)

    @property
    def directory(self) -> Path:
        return self._directory

    def list_pdfs(self) -> List[Path]:
        return sorted(self._directory.glob("*.pdf"))


class FileSystemPhotoStorage(PhotoStorage):
    def __init__(self, directory: Path, keep_filenames: Iterable[str] | None = None) -> None:
        self._directory = directory
        self._directory.mkdir(parents=True, exist_ok=True)
        self._keep_filenames: Set[str] = set(keep_filenames or [])

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def keep_filenames(self) -> Set[str]:
        return self._keep_filenames
