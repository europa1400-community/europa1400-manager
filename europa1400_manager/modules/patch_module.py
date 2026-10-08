import typer

from europa1400_manager.config import Config
from europa1400_manager.const import PatchType
from europa1400_manager.database import Database
from europa1400_manager.models import GameE1400PatchTable, GamePatch, GamePatchTable
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.patches.archive_patch import ArchivePatch
from europa1400_manager.patches.base_patch import BasePatch
from europa1400_manager.patches.e1400patch_patch import (
    E1400PatchLoaderPatch,
    E1400PatchModulePatch,
)
from europa1400_manager.patches.simple_patch import SimplePatch
from europa1400_manager.utils import DialogUtils


class PatchModule(BaseModule):
    NAME = "patch"
    FRIENDLY_NAME = "Patches"
    PATCH_TYPE_TO_CLASS: dict[PatchType, type[BasePatch]] = {
        PatchType.SIMPLE: SimplePatch,
        PatchType.ARCHIVE: ArchivePatch,
        PatchType.E1400PATCH_LOADER: E1400PatchLoaderPatch,
        PatchType.E1400PATCH_MODULE: E1400PatchModulePatch,
    }

    def __init__(self, config: Config, database: Database) -> None:
        super().__init__(config, database)

        self.game_patches = database.get_table_elements(
            GamePatchTable, GamePatch
        ) + database.get_table_elements(GameE1400PatchTable, GamePatch)

        self.patches = [
            self.PATCH_TYPE_TO_CLASS[game_patch.type](config, game_patch)
            for game_patch in self.game_patches
            if game_patch.type in self.PATCH_TYPE_TO_CLASS
        ]

    async def install(
        self, patch_name: str | None = typer.Argument(default=None)
    ) -> None:
        """Install the patches."""
        if patch_name is None:
            DialogUtils.tell(self.config.app_mode, "Please specify a patch to install.")
            return

        return await self._install_patch(patch_name)

    async def uninstall(
        self, patch_name: str | None = typer.Argument(default=None)
    ) -> None:
        """Uninstall the patches."""
        if patch_name is None:
            DialogUtils.tell(
                self.config.app_mode, "Please specify a patch to uninstall."
            )
            return

        return await self._uninstall_patch(patch_name)

    def _get_patch_by_id(self, patch_id: str) -> BasePatch | None:
        """Get a patch by its ID."""
        return next((p for p in self.patches if p.name == patch_id), None)

    async def install_requirements(
        self, patch: BasePatch, seen: set[str] | None = None
    ) -> None:
        """Install the patches a patch requires (recursively) that are not installed yet."""
        seen = seen if seen is not None else {patch.name}
        for required_id in patch.game_patch.requires or []:
            if required_id in seen:
                continue
            seen.add(required_id)
            required = self._get_patch_by_id(required_id)
            if required is None:
                raise Exception(
                    f"{patch.friendly_name} requires {required_id}, which is not available."
                )
            if not required.is_installed:
                await self.install_requirements(required, seen)
                await required.install()

    async def _install_patch(self, patch_id: str) -> None:
        """Install a specific patch."""
        patch = self._get_patch_by_id(patch_id)
        if patch is None:
            DialogUtils.tell(
                self.config.app_mode, f"Patch {patch_id} is not supported."
            )
            return

        if patch.is_installed:
            DialogUtils.tell(
                self.config.app_mode,
                f"{patch.friendly_name} is already installed.",
            )
            return

        await self.install_requirements(patch)
        await patch.install()

        DialogUtils.tell(
            self.config.app_mode,
            f"{patch.friendly_name} has been installed successfully.",
        )

    async def _uninstall_patch(self, patch_id: str) -> None:
        """Uninstall a specific patch."""
        patch = self._get_patch_by_id(patch_id)
        if patch is None:
            DialogUtils.tell(
                self.config.app_mode, f"Patch {patch_id} is not supported."
            )
            return

        if not patch.is_installed:
            DialogUtils.tell(
                self.config.app_mode,
                f"{patch.friendly_name} is not installed.",
            )
            return

        await patch.uninstall()

        DialogUtils.tell(
            self.config.app_mode,
            f"{patch.friendly_name} has been uninstalled successfully.",
        )
