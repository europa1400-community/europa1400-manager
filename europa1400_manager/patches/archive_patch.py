import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import aiohttp

from europa1400_manager.patches.base_patch import BasePatch


class ArchivePatch(BasePatch):
    """Archive download, extract and place patch."""

    def _normalize_file_names(self, file_names: str | list[str] | None) -> list[str]:
        """Normalize file names to always return a list."""
        if file_names is None:
            return []
        if isinstance(file_names, str):
            return [file_names]
        return file_names

    def _get_file_names(self) -> list[str]:
        """Get file names, preferring file_name over archive_file_name."""
        file_names = self._normalize_file_names(self.game_patch.file_name)
        if file_names:
            return file_names

        archive_file_names = self._normalize_file_names(
            self.game_patch.archive_file_name
        )
        if archive_file_names:
            return archive_file_names

        raise ValueError(
            f"file_name or archive_file_name must be set for archive patch {self.game_patch.id}"
        )

    def _get_archive_file_names(self) -> list[str]:
        """Get archive file names, preferring archive_file_name over file_name."""
        archive_file_names = self._normalize_file_names(
            self.game_patch.archive_file_name
        )
        if archive_file_names:
            return archive_file_names

        file_names = self._normalize_file_names(self.game_patch.file_name)
        if file_names:
            return file_names

        raise ValueError(
            f"file_name or archive_file_name must be set for archive patch {self.game_patch.id}"
        )

    @property
    def file_paths(self) -> list[Path]:
        """Names of the files in the game directory."""
        file_names = self._get_file_names()
        return [self.config.game_path / Path(file_name) for file_name in file_names]

    @property
    def archive_file_paths(self) -> list[Path]:
        """Names of the archive files."""
        archive_file_names = self._get_archive_file_names()
        return [Path(archive_file_name) for archive_file_name in archive_file_names]

    @property
    def target_file_paths(self) -> list[Path]:
        """Paths to the target files in the game directory."""
        return self.file_paths

    @property
    def is_installed(self) -> bool:
        """Check if the patch is installed by verifying all target files exist."""
        target_file_paths = self.target_file_paths
        return all(target_file_path.exists() for target_file_path in target_file_paths)

    async def install(self) -> None:
        """Install the patch by downloading and extracting the archive."""
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

            archive_file_paths = self.archive_file_paths
            target_file_paths = self.target_file_paths

            for archive_file_path, target_file_path in zip(
                archive_file_paths, target_file_paths
            ):
                target_file_source = self._find_file_in_extracted_contents(
                    extract_path, archive_file_path
                )

                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(target_file_source), str(target_file_path))

        await self.execute_file_operations()

    def _find_file_in_extracted_contents(
        self, extract_path: Path, archive_file_path: Path
    ) -> Path:
        """Find the target file in the extracted archive contents by matching path suffix."""
        matching_files = []

        for file_path in extract_path.rglob("*"):
            if file_path.is_file():
                try:
                    relative_path = file_path.relative_to(extract_path)
                    if str(relative_path).endswith(str(archive_file_path)) or str(
                        relative_path
                    ).endswith(str(archive_file_path).replace("\\", "/")):
                        relative_parts = relative_path.parts
                        target_parts = archive_file_path.parts
                        if len(relative_parts) >= len(target_parts):
                            if relative_parts[-len(target_parts) :] == target_parts:
                                matching_files.append(file_path)
                except ValueError:
                    continue

        if len(matching_files) == 0:
            raise FileNotFoundError(
                f"Could not find any file ending with '{archive_file_path}' in archive {self.game_patch.url}"
            )
        elif len(matching_files) > 1:
            matching_paths = [str(f.relative_to(extract_path)) for f in matching_files]
            raise ValueError(
                f"Found multiple files ending with '{archive_file_path}' in archive {self.game_patch.url}: {matching_paths}"
            )

        return matching_files[0]

    async def uninstall(self) -> None:
        """Uninstall the patch by removing all target files."""
        target_file_paths = self.target_file_paths
        for target_file_path in target_file_paths:
            target_file_path.unlink(missing_ok=True)
