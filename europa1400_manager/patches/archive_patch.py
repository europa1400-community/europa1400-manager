import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import aiohttp

from europa1400_manager.patches.base_patch import BasePatch


class ArchivePatch(BasePatch):
    """Archive download, extract and place patch."""

    @property
    def target_file_path(self) -> Path:
        """Path to the target file in the game directory."""
        if not self.game_patch.file_name:
            raise ValueError(
                f"file_name must be set for archive patch {self.game_patch.id}"
            )

        return (
            self.config.game_path
            / self.game_patch.relative_destination
            / self.game_patch.file_name
        )

    @property
    def is_installed(self) -> bool:
        """Check if the patch is installed by verifying the target file exists."""
        return self.target_file_path.exists()

    async def install(self) -> None:
        """Install the patch by downloading and extracting the archive."""
        if not self.game_patch.file_name:
            raise ValueError(
                f"file_name must be set for archive patch {self.game_patch.id}"
            )

        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / Path(self.game_patch.url).name
            async with aiohttp.ClientSession() as session:
                async with session.get(self.game_patch.url) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Failed to download {self.friendly_name}: HTTP {response.status}"
                        )
                    with open(archive_path, "wb") as file:
                        async for chunk in response.content.iter_chunked(32_768):
                            file.write(chunk)

            extract_path = Path(tmp) / "extracted"
            extract_path.mkdir()

            if archive_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_file:
                    zip_file.extractall(extract_path)
            elif (
                archive_path.suffix.lower() in [".tar", ".gz", ".bz2", ".xz"]
                or ".tar." in archive_path.name.lower()
            ):
                with tarfile.open(archive_path, "r:*") as tar_file:
                    tar_file.extractall(extract_path)
            else:
                raise ValueError(f"Unsupported archive format: {archive_path.suffix}")

            target_file_source = self._find_file_in_extracted_contents(
                extract_path, self.game_patch.file_name
            )
            if not target_file_source:
                raise FileNotFoundError(
                    f"Could not find file '{self.game_patch.file_name}' in archive {self.game_patch.url}"
                )

            self.target_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(target_file_source), str(self.target_file_path))

    def _find_file_in_extracted_contents(
        self, extract_path: Path, target_file_name: str
    ) -> Path | None:
        """Find the target file in the extracted archive contents."""
        for file_path in extract_path.rglob("*"):
            if file_path.is_file() and file_path.name == target_file_name:
                return file_path
        return None

    async def uninstall(self) -> None:
        """Uninstall the patch by removing the target file."""
        self.target_file_path.unlink(missing_ok=True)
