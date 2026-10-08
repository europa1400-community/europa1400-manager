"""How each patch type is installed. Handlers only write through a Transaction (backups, rollback, uninstall)."""

from __future__ import annotations

from europa1400_manager.core.handlers.base import Handler, Progress
from europa1400_manager.core.handlers.e1400patch import (
    E1400PatchLoaderHandler,
    E1400PatchModuleHandler,
)
from europa1400_manager.core.handlers.files import ArchiveHandler, SimpleHandler
from europa1400_manager.core.models import PatchType

HANDLERS: dict[PatchType, type[Handler]] = {
    PatchType.SIMPLE: SimpleHandler,
    PatchType.ARCHIVE: ArchiveHandler,
    PatchType.E1400PATCH_LOADER: E1400PatchLoaderHandler,
    PatchType.E1400PATCH_MODULE: E1400PatchModuleHandler,
}

__all__ = ["HANDLERS", "Handler", "Progress"]
