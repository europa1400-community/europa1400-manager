"""Patches of europa1400-patches: the patch loader and its patch modules.

Release archives are extracted into the game directory as they are:

- the loader archive contains ``e1400patch/`` (server.dll shim, loader, tool, build tables, default configuration);
  installing it points ``game.ini [Network] Server=`` to ``e1400patch\\server.dll`` and keeps the previous entry in
  ``e1400patch\\e1400patch.ini [install] previous_server`` (the same as ``e1400patch.exe install``), uninstalling
  restores it. No game file is replaced.
- a module archive contains ``patches/<id>/`` (or ``mods/<id>/``); the loader picks it up the next time the game hosts.
"""

from __future__ import annotations

import configparser
import hashlib
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import aiohttp

from europa1400_manager.patches.base_patch import BasePatch
from europa1400_manager.utils import PreservingIniUtils

LOADER_DIR = "e1400patch"
SHIM_ENTRY = "e1400patch\\server.dll"
DEFAULT_SERVER = "Server\\Server.DLL"


async def download_and_extract(url: str, destination: Path) -> None:
    """Download an archive and extract all of it into destination (paths must stay inside it)."""
    with tempfile.TemporaryDirectory() as tmp:
        archive_path = Path(tmp) / Path(url).name
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download {url}: HTTP {response.status}")
                with open(archive_path, "wb") as file:
                    async for chunk in response.content.iter_chunked(32_768):
                        file.write(chunk)
        root = destination.resolve()
        if archive_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                for member in archive.namelist():
                    if not (root / member).resolve().is_relative_to(root):
                        raise ValueError(f"Unsafe path in archive {url}: {member}")
                archive.extractall(root)
        else:
            with tarfile.open(archive_path, "r:*") as archive:
                archive.extractall(root, filter="data")


class E1400PatchLoaderPatch(BasePatch):
    """The patch loader (europa1400-patches)."""

    @property
    def loader_path(self) -> Path:
        return self.config.game_path / LOADER_DIR

    @property
    def game_ini_path(self) -> Path:
        return self.config.game_path / "game.ini"

    @property
    def config_path(self) -> Path:
        return self.loader_path / "e1400patch.ini"

    @staticmethod
    def _is_shim_entry(value: str | None) -> bool:
        return value is not None and value.replace("/", "\\").lower().endswith(
            SHIM_ENTRY
        )

    @property
    def is_installed(self) -> bool:
        entry = PreservingIniUtils.get_value(self.game_ini_path, "Network", "Server")
        return (self.loader_path / "server.dll").exists() and self._is_shim_entry(entry)

    def _known_server_hashes(self) -> set[str]:
        hashes = set()
        for table in (self.loader_path / "builds").glob("*.ini"):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.read(table, encoding="utf-8")
            if parser.get("build", "target", fallback="") == "server":
                hashes.add(parser.get("build", "sha256", fallback="").lower())
        return hashes

    def _original_server(self, previous: str) -> str:
        """The previous entry when it is a known original server.dll, else the default location."""
        known = self._known_server_hashes()
        for candidate in (previous, "Server\\server.dll"):
            path = (
                Path(candidate)
                if Path(candidate).is_absolute()
                else self.config.game_path / candidate
            )
            if (
                path.is_file()
                and hashlib.sha256(path.read_bytes()).hexdigest() in known
            ):
                return candidate
        candidate_path = (
            Path(previous)
            if Path(previous).is_absolute()
            else self.config.game_path / previous
        )
        return previous if candidate_path.is_file() else "Server\\server.dll"

    async def install(self) -> None:
        await download_and_extract(self.game_patch.url, self.config.game_path)
        if (
            not self.config_path.exists()
            and (self.loader_path / "e1400patch.ini.default").exists()
        ):
            shutil.copy2(self.loader_path / "e1400patch.ini.default", self.config_path)
        previous = (
            PreservingIniUtils.get_value(self.game_ini_path, "Network", "Server")
            or DEFAULT_SERVER
        )
        if not self._is_shim_entry(previous):
            PreservingIniUtils.set_value(
                self.config_path, "install", "previous_server", previous
            )
            PreservingIniUtils.set_value(
                self.config_path,
                "loader",
                "original_server",
                self._original_server(previous),
            )
            PreservingIniUtils.set_value(
                self.game_ini_path, "Network", "Server", SHIM_ENTRY
            )
        await self.execute_file_operations()

    async def uninstall(self) -> None:
        entry = PreservingIniUtils.get_value(self.game_ini_path, "Network", "Server")
        if self._is_shim_entry(entry):
            previous = (
                PreservingIniUtils.get_value(
                    self.config_path, "install", "previous_server"
                )
                or DEFAULT_SERVER
            )
            PreservingIniUtils.set_value(
                self.game_ini_path, "Network", "Server", previous
            )
        shutil.rmtree(self.loader_path, ignore_errors=True)


class E1400PatchModulePatch(BasePatch):
    """A patch module (patches/<id>/) or mod (mods/<id>/) of europa1400-patches; the database id is the module id."""

    @property
    def module_path(self) -> Path:
        for kind_dir in ("patches", "mods"):
            path = self.config.game_path / kind_dir / self.game_patch.id
            if path.exists():
                return path
        return self.config.game_path / "patches" / self.game_patch.id

    @property
    def is_installed(self) -> bool:
        return (self.module_path / "patch.ini").exists()

    async def install(self) -> None:
        await download_and_extract(self.game_patch.url, self.config.game_path)
        if not self.is_installed:
            raise Exception(
                f"{self.game_patch.url} did not contain patches/{self.game_patch.id}/patch.ini"
            )
        await self.execute_file_operations()

    async def uninstall(self) -> None:
        shutil.rmtree(self.module_path, ignore_errors=True)
