from app.core.config import settings

from .local import LocalStorage

local_storage = LocalStorage(settings.STORAGE_DIR)

__all__ = ["LocalStorage", "local_storage"]
