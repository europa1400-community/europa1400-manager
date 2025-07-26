import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

from europa1400_manager.config import Config
from europa1400_manager.patches.base_patch import BasePatch


class DDrawCompatPatch(BasePatch):
    """Class to manage the DDrawCompat patch."""

    NAME = "ddrawcompat"
    FRIENDLY_NAME = "DDrawCompat"

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    @property
    def dll_path(self) -> Path:
        """Path to the ddraw.dll in the game directory."""
        return self.config.game_path / "ddraw.dll"

    @property
    def is_installed(self) -> bool:
        """Check if DDrawCompat is installed."""
        return self.dll_path.exists()

    async def install(self) -> None:
        """Download and install DDrawCompat."""
        url = "https://github.com/narzoul/DDrawCompat/releases/download/v0.6.0/DDrawCompat-v0.6.0.zip"

        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "ddrawcompat.zip")

            resp = requests.get(url, stream=True)
            if resp.status_code != 200:
                raise Exception(
                    f"Failed to download DDrawCompat: HTTP {resp.status_code}"
                )
            with open(zip_path, "wb") as f:
                for chunk in resp.iter_content(32_768):
                    f.write(chunk)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmp)

            dll_src = None
            for root, dirs, files in os.walk(tmp):
                if "ddraw.dll" in files:
                    dll_src = os.path.join(root, "ddraw.dll")
                    break

            if not dll_src:
                raise FileNotFoundError(f"Could not find ddraw.dll in {tmp!r}")

            self.config.game_path.mkdir(parents=True, exist_ok=True)
            shutil.move(dll_src, self.dll_path)

    async def uninstall(self) -> None:
        """Uninstall DDrawCompat by removing the DLL."""
        self.dll_path.unlink(missing_ok=True)
