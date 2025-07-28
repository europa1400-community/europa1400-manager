import typer

from europa1400_manager.config import Config
from europa1400_manager.const import PatchType
from europa1400_manager.database import Database
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.patches.base_patch import BasePatch
from europa1400_manager.patches.ddrawcompat_patch import DDrawCompatPatch
from europa1400_manager.utils import DialogUtils


class PatchModule(BaseModule):
    NAME = "patch"
    FRIENDLY_NAME = "Patches"

    def __init__(self, config: Config, database: Database) -> None:
        super().__init__(config, database)

        self.patches: dict[PatchType, BasePatch] = {
            PatchType.DDRAWCOMPAT: DDrawCompatPatch(self.config),
        }

    @property
    def installed_patches(self) -> dict[PatchType, BasePatch]:
        """Get a list of installed patches."""
        return {
            patch_type: patch
            for patch_type, patch in self.patches.items()
            if patch.is_installed
        }

    async def install(
        self, patch_name: PatchType | None = typer.Argument(default=None)
    ) -> None:
        """Install the patches."""
        if patch_name is None:
            DialogUtils.tell(self.config.app_mode, "Please specify a patch to install.")
            return

        return await self._install_patch(patch_name)

    async def uninstall(
        self, patch_name: PatchType | None = typer.Argument(default=None)
    ) -> None:
        """Uninstall the patches."""
        if patch_name is None:
            DialogUtils.tell(
                self.config.app_mode, "Please specify a patch to uninstall."
            )
            return

        return await self._uninstall_patch(patch_name)

    async def _install_patch(self, patch_type: PatchType) -> None:
        """Install a specific patch."""
        patch = self.patches.get(patch_type)

        if patch is None:
            DialogUtils.tell(
                self.config.app_mode, f"Patch {patch_type} is not supported."
            )
            return

        if patch.is_installed:
            DialogUtils.tell(
                self.config.app_mode,
                f"{patch.FRIENDLY_NAME} is already installed.",
            )
            return

        await patch.install()

        DialogUtils.tell(
            self.config.app_mode,
            f"{patch.FRIENDLY_NAME} has been installed successfully.",
        )

    async def _uninstall_patch(self, patch_type: PatchType) -> None:
        """Uninstall a specific patch."""
        patch = self.patches.get(patch_type)

        if patch is None:
            DialogUtils.tell(
                self.config.app_mode, f"Patch {patch_type} is not supported."
            )
            return

        if not patch.is_installed:
            DialogUtils.tell(
                self.config.app_mode,
                f"{patch.FRIENDLY_NAME} is not installed.",
            )
            return

        await patch.uninstall()

        DialogUtils.tell(
            self.config.app_mode,
            f"{patch.FRIENDLY_NAME} has been uninstalled successfully.",
        )
