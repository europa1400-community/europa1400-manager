import shutil
import tempfile
from pathlib import Path

import aiohttp

from europa1400_manager.patches.base_patch import BasePatch


class SimplePatch(BasePatch):
    """Simple file download and place patch."""

    @property
    def file_name(self) -> str:
        """Name of the file in the game directory."""
        return Path(self.game_patch.url).name

    @property
    def file_path(self) -> Path:
        """Path to the file in the game directory."""
        return self.config.game_path / self.file_name

    @property
    def is_installed(self) -> bool:
        """Check if the patch is installed."""
        return self.file_path.exists()

    async def install(self) -> None:
        """Install the patch."""

        with tempfile.TemporaryDirectory() as tmp:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.game_patch.url) as resp:
                    if resp.status != 200:
                        raise Exception(
                            f"Failed to download {self.friendly_name}: HTTP {resp.status}"
                        )
                    file_path = Path(tmp) / Path(self.game_patch.url).name
                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(32_768):
                            f.write(chunk)
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(self.file_path))

        await self.execute_file_operations()

    async def uninstall(self) -> None:
        """Uninstall the patch."""
        self.file_path.unlink(missing_ok=True)
