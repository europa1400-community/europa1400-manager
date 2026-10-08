"""Third-party patches: a single file (simple) or files taken from an archive (archive)."""

from __future__ import annotations

import tempfile
from pathlib import Path, PurePosixPath

from europa1400_manager.core import download
from europa1400_manager.core.errors import PatchError
from europa1400_manager.core.handlers.base import Handler, Progress
from europa1400_manager.core.install_state import Transaction
from europa1400_manager.i18n import tr


def _as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


class SimpleHandler(Handler):
    @property
    def target(self) -> str:
        names = _as_list(self.patch.file_name)
        return names[0] if names else download.file_name_of(self.patch.url)

    async def install(
        self, transaction: Transaction, progress: Progress | None
    ) -> None:
        source = await self.fetch(progress)
        transaction.write_file(source, self.target)
        _file_operations(self, transaction)

    def present_unmanaged(self) -> bool:
        return (self.game.path / self.target).exists()


class ArchiveHandler(Handler):
    """file_name: target paths in the game folder; archive_file_name: matching paths in the archive (path suffixes)."""

    @property
    def targets(self) -> list[str]:
        return _as_list(self.patch.file_name) or _as_list(self.patch.archive_file_name)

    @property
    def sources(self) -> list[str]:
        return _as_list(self.patch.archive_file_name) or _as_list(self.patch.file_name)

    async def install(
        self, transaction: Transaction, progress: Progress | None
    ) -> None:
        if not self.targets or len(self.targets) != len(self.sources):
            raise PatchError(tr("error.patch_definition", patch=self.patch.id))
        archive = await self.fetch(progress)
        if not download.is_archive(archive):
            raise PatchError(tr("error.not_an_archive", patch=self.patch.id))
        with tempfile.TemporaryDirectory(prefix="e1400-") as temporary:
            root = Path(
                temporary
            ).resolve()  # long path names (temp folders can be 8.3 short names)
            files = download.extract(archive, root)
            for source, target in zip(self.sources, self.targets):
                transaction.write_file(
                    _find(files, root, source, self.patch.id), target
                )
        _file_operations(self, transaction)

    def present_unmanaged(self) -> bool:
        return bool(self.targets) and all(
            (self.game.path / t).exists() for t in self.targets
        )


def _find(files: list[Path], root: Path, wanted: str, patch_id: str) -> Path:
    """The extracted file whose path ends with wanted (whole path components, case-insensitive)."""
    parts = tuple(p.lower() for p in PurePosixPath(wanted.replace("\\", "/")).parts)
    matches = [
        f
        for f in files
        if tuple(p.lower() for p in f.relative_to(root).parts[-len(parts) :]) == parts
    ]
    if len(matches) != 1:
        raise PatchError(
            tr("error.archive_member", patch=patch_id, file=wanted, count=len(matches))
        )
    return matches[0]


def _file_operations(handler: Handler, transaction: Transaction) -> None:
    for operation in handler.patch.file_operations or []:
        if operation.type != "ini" or not (
            operation.file_name and operation.section and operation.key
        ):
            raise PatchError(tr("error.patch_definition", patch=handler.patch.id))
        value = operation.value
        text = (
            None
            if value is None
            else ("1" if value is True else "0" if value is False else str(value))
        )
        transaction.set_ini(operation.file_name, operation.section, operation.key, text)
