import os
import shutil
import tempfile
import zipfile

import requests

from europa1400_manager.config import Config
from europa1400_manager.tools.base_tool import BaseTool


class DDrawCompatTool(BaseTool):
    """Class to manage the DDrawCompat tool."""

    NAME = "ddrawcompat"
    FRIENDLY_NAME = "DDrawCompat"

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    @property
    def is_installed(self) -> bool:
        """Check if DDrawCompat is installed."""
        return (self.config.game_path / "ddraw.dll").exists()

    async def install(self) -> None:
        """Download and install DDrawCompat."""
        url = "https://github.com/narzoul/DDrawCompat/releases/download/v0.6.0/DDrawCompat-v0.6.0.zip"

        # Create a temporary workdir
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "ddrawcompat.zip")

            # Download ZIP
            resp = requests.get(url, stream=True)
            if resp.status_code != 200:
                raise Exception(
                    f"Failed to download DDrawCompat: HTTP {resp.status_code}"
                )
            with open(zip_path, "wb") as f:
                for chunk in resp.iter_content(32_768):
                    f.write(chunk)

            # Extract everything
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmp)

            # Find the DLL anywhere under tmp/
            dll_src = None
            for root, dirs, files in os.walk(tmp):
                if "ddraw.dll" in files:
                    dll_src = os.path.join(root, "ddraw.dll")
                    break

            if not dll_src:
                raise FileNotFoundError(f"Could not find ddraw.dll in {tmp!r}")

            # Ensure game_path exists
            self.config.game_path.mkdir(parents=True, exist_ok=True)
            dll_dest = self.config.game_path / "ddraw.dll"

            # Move into place
            shutil.move(dll_src, dll_dest)
