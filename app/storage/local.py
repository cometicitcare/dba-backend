from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO


class LocalStorage:
    """Minimal helper to persist uploaded files on the local filesystem."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_fileobj(self, file_obj: BinaryIO, relative_path: str | Path) -> str:
        """Persist the given file object under the storage directory.

        Returns the saved path relative to the storage root (POSIX style) so it
        can be stored in the database and later re-composed into a URL.
        """
        path = self.base_dir / Path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_obj.seek(0)
        with path.open("wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return path.relative_to(self.base_dir).as_posix()
