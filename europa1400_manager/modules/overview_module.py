import platform
import subprocess
from pathlib import Path

import typer

from europa1400_manager.config import Config
from europa1400_manager.const import AppMode
from europa1400_manager.database import Database
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.modules.info_module import InfoModule
from europa1400_manager.utils import DialogUtils


class OverviewModule(BaseModule):
    NAME = "overview"
    FRIENDLY_NAME = "Overview"

    def __init__(
        self, config: Config, database: Database, info_module: InfoModule
    ) -> None:
        super().__init__(config, database)
        self.info_module = info_module

    async def start_game(self) -> None:
        """Launch the main game executable."""
        if not self.info_module._executable_path:
            raise RuntimeError("Game executable path is not set.")
        await self._launch_executable(self.info_module._executable_path, "Legacy Game")

    async def start_game_tl(self) -> None:
        """Launch the T&L game executable."""
        if not self.info_module._tl_executable_path:
            raise RuntimeError("Game tl executable path is not set.")
        await self._launch_executable(self.info_module._tl_executable_path, "T&L Game")

    async def _launch_executable(self, executable_path: Path, game_name: str) -> None:
        """Launch the specified executable."""
        if self.config.app_mode is AppMode.CLI:
            typer.echo(f"Launching {game_name}...")

        try:
            subprocess.Popen(
                [str(executable_path)],
                cwd=self.config.game_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (PermissionError, OSError) as permission_error:
            needs_elevation = (
                isinstance(permission_error, OSError)
                and hasattr(permission_error, "winerror")
                and permission_error.winerror == 740
            ) or isinstance(permission_error, PermissionError)

            if needs_elevation and platform.system() == "Windows":
                if self.config.app_mode is AppMode.CLI:
                    typer.echo(
                        f"Admin privileges required. Launching {game_name} with elevated privileges..."
                    )

                try:
                    subprocess.Popen(
                        [
                            "powershell",
                            "-Command",
                            "Start-Process",
                            f'"{executable_path}"',
                            "-Verb",
                            "RunAs",
                            "-WorkingDirectory",
                            f'"{self.config.game_path}"',
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception as elevated_error:
                    error_message = f"Failed to launch {game_name} with elevated privileges: {elevated_error}"
                    if self.config.app_mode is AppMode.CLI:
                        typer.echo(error_message, err=True)
                    else:
                        DialogUtils.tell(self.config.app_mode, error_message)
                        raise RuntimeError(error_message)
            else:
                error_message = f"Permission denied when launching {game_name}. Please run with appropriate privileges."
                if self.config.app_mode is AppMode.CLI:
                    typer.echo(error_message, err=True)
                else:
                    DialogUtils.tell(self.config.app_mode, error_message)
                    raise RuntimeError(error_message)
        except Exception as execution_error:
            error_message = f"Failed to launch {game_name}: {execution_error}"
            if self.config.app_mode is AppMode.CLI:
                typer.echo(error_message, err=True)
            else:
                DialogUtils.tell(self.config.app_mode, error_message)
                raise RuntimeError(error_message)
