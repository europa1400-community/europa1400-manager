"""europa1400-patches: the patch loader (e1400patch/) and its patch modules (patches/<id>/, mods/<id>/).

The loader archive is extracted into the game folder; game.ini [Network] Server= is pointed to the loader's server.dll
(the previous value is restored on uninstall). e1400patch.ini [install]/[loader] are filled like `e1400patch.exe
install` does, so the loader's own tool can uninstall it too.
"""

from __future__ import annotations

import configparser
import shutil
import tempfile
from pathlib import Path

from europa1400_manager.core import download, ini
from europa1400_manager.core.errors import PatchError
from europa1400_manager.core.handlers.base import Handler, Progress
from europa1400_manager.core.install_state import Transaction
from europa1400_manager.i18n import tr

LOADER_DIR = "e1400patch"
SHIM_ENTRY = "e1400patch\\server.dll"
DEFAULT_SERVER = "Server\\server.dll"


def is_shim_entry(value: str | None) -> bool:
    return value is not None and value.replace("/", "\\").lower().endswith(SHIM_ENTRY)


class E1400PatchLoaderHandler(Handler):
    async def install(
        self, transaction: Transaction, progress: Progress | None
    ) -> None:
        archive = await self.fetch(progress)
        game_ini = self.game.game_ini
        previous = ini.get(game_ini, "Network", "Server") or DEFAULT_SERVER
        if is_shim_entry(
            previous
        ):  # loader installed before without a record: keep its remembered entry
            remembered = ini.get(
                self.game.path / LOADER_DIR / "e1400patch.ini",
                "install",
                "previous_server",
            )
            previous = remembered or DEFAULT_SERVER
        with tempfile.TemporaryDirectory(prefix="e1400-") as temporary:
            root = Path(
                temporary
            ).resolve()  # long path names (temp folders can be 8.3 short names)
            files = download.extract(archive, root)
            if not (root / LOADER_DIR / "server.dll").exists():
                raise PatchError(
                    tr("error.archive_layout", patch=self.patch.id, folder=LOADER_DIR)
                )
            config = root / LOADER_DIR / "e1400patch.ini"
            existing = self.game.path / LOADER_DIR / "e1400patch.ini"
            if existing.exists():
                shutil.copy2(existing, config)  # keep the player's loader settings
            elif (root / LOADER_DIR / "e1400patch.ini.default").exists():
                shutil.copy2(root / LOADER_DIR / "e1400patch.ini.default", config)
            ini.set_values(
                config,
                {
                    ("install", "previous_server"): previous,
                    ("loader", "original_server"): self._original_server(
                        previous, root / LOADER_DIR / "builds"
                    ),
                },
            )
            if config not in files:
                files.append(config)
            transaction.own_dir(LOADER_DIR)
            for file in files:
                transaction.write_file(file, file.relative_to(root).as_posix())
        transaction.set_ini("game.ini", "Network", "Server", SHIM_ENTRY)

    def _original_server(self, previous: str, builds: Path) -> str:
        """The previous entry if it is a known original server.dll, else the game's own server.dll."""
        known = set()
        for table in builds.glob("*.ini"):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.read(table, encoding="utf-8")
            if parser.get("build", "target", fallback="") == "server":
                known.add(parser.get("build", "sha256", fallback="").lower())
        for candidate in (previous, DEFAULT_SERVER):
            path = (
                Path(candidate)
                if Path(candidate).is_absolute()
                else self.game.path / candidate
            )
            if path.is_file() and download.sha256_of(path) in known:
                return candidate
        return DEFAULT_SERVER

    def present_unmanaged(self) -> bool:
        return (self.game.path / LOADER_DIR / "server.dll").exists() and is_shim_entry(
            ini.get(self.game.game_ini, "Network", "Server")
        )

    def can_remove_unmanaged(self) -> bool:
        return True

    def remove_unmanaged(self) -> None:
        if is_shim_entry(ini.get(self.game.game_ini, "Network", "Server")):
            config = self.game.path / LOADER_DIR / "e1400patch.ini"
            previous = ini.get(config, "install", "previous_server") or DEFAULT_SERVER
            ini.set_value(self.game.game_ini, "Network", "Server", previous)
        shutil.rmtree(self.game.path / LOADER_DIR, ignore_errors=True)


class E1400PatchModuleHandler(Handler):
    """The database id is the module id; the archive contains patches/<id>/ (or mods/<id>/)."""

    def _folder(self) -> Path | None:
        for kind in ("patches", "mods"):
            folder = self.game.path / kind / self.patch.id
            if (folder / "patch.ini").exists():
                return folder
        return None

    async def install(
        self, transaction: Transaction, progress: Progress | None
    ) -> None:
        archive = await self.fetch(progress)
        with tempfile.TemporaryDirectory(prefix="e1400-") as temporary:
            root = Path(
                temporary
            ).resolve()  # long path names (temp folders can be 8.3 short names)
            files = download.extract(archive, root)
            kind = next(
                (
                    k
                    for k in ("patches", "mods")
                    if (root / k / self.patch.id / "patch.ini").exists()
                ),
                None,
            )
            if kind is None:
                raise PatchError(
                    tr(
                        "error.archive_layout",
                        patch=self.patch.id,
                        folder=f"patches/{self.patch.id}",
                    )
                )
            transaction.own_dir(f"{kind}/{self.patch.id}")
            for file in files:
                relative = file.relative_to(root).as_posix()
                if relative.startswith(f"{kind}/{self.patch.id}/"):
                    transaction.write_file(file, relative)

    def present_unmanaged(self) -> bool:
        return self._folder() is not None

    def can_remove_unmanaged(self) -> bool:
        return True

    def remove_unmanaged(self) -> None:
        folder = self._folder()
        if folder:
            shutil.rmtree(folder, ignore_errors=True)
            try:
                folder.parent.rmdir()
            except OSError:
                pass
