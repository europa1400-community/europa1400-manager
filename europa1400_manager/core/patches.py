"""Patch status, installing (with requirements and conflicts) and uninstalling for one game."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum

from europa1400_manager.core.database import Database
from europa1400_manager.core.errors import PatchError
from europa1400_manager.core.game import Game
from europa1400_manager.core.handlers import HANDLERS, Handler, Progress
from europa1400_manager.core.install_state import InstallState
from europa1400_manager.core.models import GamePatch
from europa1400_manager.i18n import tr

log = logging.getLogger(__name__)


class PatchState(StrEnum):
    AVAILABLE = "available"
    INSTALLED = "installed"
    UPDATE = "update"  # installed, the database has a newer version
    UNMANAGED = "unmanaged"  # present, but not installed by this manager (by hand or manager <= 1.2)


@dataclass
class PatchStatus:
    patch: GamePatch
    state: PatchState
    installed_version: str | None
    compatible: bool | None  # None: the database says nothing about this game version
    required_by: list[str]  # installed patches that need this one

    @property
    def installed(self) -> bool:
        return self.state in (
            PatchState.INSTALLED,
            PatchState.UPDATE,
            PatchState.UNMANAGED,
        )


class PatchService:
    def __init__(self, game: Game, database: Database) -> None:
        self.game = game
        self.database = database
        self.state = InstallState(game.path)

    def handler(self, patch: GamePatch) -> Handler:
        return HANDLERS[patch.type](patch, self.game)

    def get(self, patch_id: str) -> GamePatch:
        patch = self.database.patch(patch_id)
        if patch is None:
            raise PatchError(tr("error.unknown_patch", patch=patch_id))
        return patch

    # --- status ------------------------------------------------------------------------------------------------

    def compatible(self, patch: GamePatch) -> bool | None:
        mappings = [m for m in self.database.patch_mappings if m.patch == patch.id]
        if not mappings:
            return None
        return any(self.game.info.matches(vars(m.metadata)) for m in mappings)

    def status(self, patch: GamePatch) -> PatchStatus:
        record = self.state.patches.get(patch.id)
        if record is not None:
            update = bool(
                patch.version and record.version and patch.version != record.version
            )
            state = PatchState.UPDATE if update else PatchState.INSTALLED
        elif self.handler(patch).present_unmanaged():
            state = PatchState.UNMANAGED
        else:
            state = PatchState.AVAILABLE
        required_by = [
            p.id
            for p in self.database.patches
            if patch.id in (p.requires or [])
            and (p.id in self.state.patches or self.handler(p).present_unmanaged())
        ]
        return PatchStatus(
            patch,
            state,
            record.version if record else None,
            self.compatible(patch),
            required_by,
        )

    def statuses(self) -> list[PatchStatus]:
        return [self.status(p) for p in self.database.patches]

    # --- install -----------------------------------------------------------------------------------------------

    def install_order(self, patch_id: str) -> list[GamePatch]:
        """The patch and everything it needs, requirements first (only what is not installed yet)."""
        order: list[GamePatch] = []

        def visit(current: str, path: tuple[str, ...]) -> None:
            if current in path:
                raise PatchError(tr("error.requirement_cycle", patch=current))
            patch = self.get(current)
            for required in patch.requires or []:
                visit(required, (*path, current))
            if patch not in order and (
                current == patch_id or not self.status(patch).installed
            ):
                order.append(patch)

        visit(patch_id, ())
        return order

    def conflicts(self, patch: GamePatch) -> list[str]:
        installed = {s.patch.id for s in self.statuses() if s.installed}
        found = {c for c in patch.conflicts or [] if c in installed}
        found |= {
            p.id
            for p in self.database.patches
            if p.id in installed and patch.id in (p.conflicts or [])
        }
        return sorted(found)

    async def install(
        self, patch_id: str, progress: Progress | None = None
    ) -> list[str]:
        """Install a patch and its requirements; returns the ids installed."""
        self.game.ensure_not_running()
        self.game.check_writable()
        order = self.install_order(patch_id)
        for patch in order:
            if found := self.conflicts(patch):
                names = [p.name if (p := self.database.patch(c)) else c for c in found]
                raise PatchError(
                    tr("error.conflicts", patch=patch.name, others=", ".join(names))
                )
        installed = []
        for patch in order:
            status = self.status(patch)
            if status.state in (PatchState.INSTALLED,) and patch.id == patch_id:
                continue
            if status.state == PatchState.UPDATE:
                self.state.uninstall(patch.id)
            handler = self.handler(patch)
            if status.state == PatchState.UNMANAGED and handler.can_remove_unmanaged():
                handler.remove_unmanaged()  # take it over: a clean install with a record
            if progress:
                progress(tr("progress.installing", patch=patch.name), None)
            transaction = self.state.begin(patch.id, patch.version)
            try:
                await handler.install(transaction, progress)
                transaction.commit()
            except BaseException:
                log.exception("installing %s failed, rolling back", patch.id)
                transaction.rollback()
                raise
            installed.append(patch.id)
            log.info("installed %s %s", patch.id, patch.version or "")
        return installed

    # --- uninstall ---------------------------------------------------------------------------------------------

    def uninstall(self, patch_id: str, with_dependents: bool = False) -> list[str]:
        """Uninstall a patch; returns warnings. Installed patches that need it are removed first if with_dependents."""
        patch = self.get(patch_id)
        status = self.status(patch)
        if not status.installed:
            return []
        self.game.ensure_not_running()
        self.game.check_writable()
        if status.required_by and not with_dependents:
            raise PatchError(
                tr(
                    "error.required_by",
                    patch=patch.name,
                    others=", ".join(status.required_by),
                )
            )
        warnings: list[str] = []
        for dependent in status.required_by:
            warnings += self.uninstall(dependent, with_dependents=True)
        if patch_id in self.state.patches:
            warnings += self.state.uninstall(patch_id)
        else:
            handler = self.handler(patch)
            if not handler.can_remove_unmanaged():
                raise PatchError(tr("error.unmanaged_removal", patch=patch.name))
            handler.remove_unmanaged()
        log.info("uninstalled %s", patch_id)
        return warnings
