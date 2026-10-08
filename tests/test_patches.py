"""Detection and the patch service against a fake game folder; downloads are served from local files."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from europa1400_manager.core import download
from europa1400_manager.core.database import Database, parse_table
from europa1400_manager.core.detection import identify
from europa1400_manager.core.errors import PatchError
from europa1400_manager.core.game import Game
from europa1400_manager.core.models import (
    GameE1400PatchTable,
    GameFileTable,
    GameMetadataToPatchTable,
    GamePatchTable,
)
from europa1400_manager.core.patches import PatchService, PatchState


def _table(table_type: Any, elements: list[dict[str, Any]]) -> Any:
    return parse_table(
        table_type, yaml.safe_dump({"id": "t", "name": "t", "elements": elements})
    )


@pytest.fixture
def downloads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    files: dict[str, Path] = {}
    folder = tmp_path / "downloads"
    folder.mkdir()

    def add(name: str, entries: dict[str, bytes] | bytes) -> None:
        path = folder / name
        if isinstance(entries, bytes):
            path.write_bytes(entries)
        else:
            with zipfile.ZipFile(path, "w") as archive:
                for member, data in entries.items():
                    archive.writestr(member, data)
        files[f"https://example.org/{name}"] = path

    add("ddraw.zip", {"DDrawCompat-v0.6.0/ddraw.dll": b"compat"})
    add("plugin.asi", b"asi")
    add(
        "e1400patch.zip",
        {
            "e1400patch/server.dll": b"shim",
            "e1400patch/e1400patch.ini.default": b"[loader]\r\n",
        },
    )
    add(
        "netfix.zip",
        {
            "patches/netfix/patch.ini": b"[patch]\r\nid=netfix\r\n",
            "patches/netfix/netfix.dll": b"n",
        },
    )
    add("broken.zip", {"nothing.txt": b""})

    async def fake_download(
        url: str, sha256: str | None = None, progress: Any = None
    ) -> Path:
        return files[url]

    monkeypatch.setattr(download, "download", fake_download)
    return files


@pytest.fixture
def database(game_dir: Path) -> Database:
    server_sha = download.sha256_of(game_dir / "Server" / "server.dll")
    database = Database()
    database.tables[GameFileTable] = _table(
        GameFileTable,
        [
            {
                "id": "server-de",
                "sha256": server_sha,
                "file": "Server/server.dll",
                "role": "server",
                "metadata": {"edition": "gold", "version": "v2.06", "language": "de"},
            }
        ],
    )
    database.tables[GamePatchTable] = _table(
        GamePatchTable,
        [
            {
                "id": "ddraw_compat",
                "name": "DDrawCompat",
                "type": "archive",
                "url": "https://example.org/ddraw.zip",
                "file_name": "ddraw.dll",
                "version": "0.6.0",
            },
            {
                "id": "plugin",
                "name": "Plugin",
                "type": "simple",
                "url": "https://example.org/plugin.asi",
                "conflicts": ["netfix"],
            },
            {
                "id": "broken",
                "name": "Broken",
                "type": "archive",
                "url": "https://example.org/broken.zip",
                "file_name": "x.dll",
            },
            {
                "id": "future",
                "name": "Future",
                "type": "teleport",
                "url": "https://example.org/x",
            },
        ],
    )
    database.tables[GameE1400PatchTable] = _table(
        GameE1400PatchTable,
        [
            {
                "id": "e1400patch",
                "name": "Loader",
                "type": "e1400patch_loader",
                "url": "https://example.org/e1400patch.zip",
            },
            {
                "id": "netfix",
                "name": "Netfix",
                "type": "e1400patch_module",
                "url": "https://example.org/netfix.zip",
                "requires": ["e1400patch"],
            },
        ],
    )
    database.tables[GameMetadataToPatchTable] = _table(
        GameMetadataToPatchTable,
        [
            {
                "id": "m1",
                "patch": "netfix",
                "metadata": {"edition": "gold", "language": "de"},
            },
            {"id": "m2", "patch": "plugin", "metadata": {"language": "en"}},
        ],
    )
    return database


def test_identification(game_dir: Path, database: Database) -> None:
    info = identify(game_dir, database)
    assert info.metadata == {
        "edition": "gold",
        "version": "v2.06",
        "distribution": "gog",
        "language": "de",
        "drm": "none",
    }
    assert (
        info.sources["language"] == "hash"
        and info.sources["distribution"] == "heuristic"
    )
    assert [e.path.name for e in info.executables] == [
        "GildeGold_TL.exe",
        "GildeGold.exe",
    ]


def test_unknown_patch_type_is_skipped(database: Database) -> None:
    assert [p.id for p in database.patches] == [
        "ddraw_compat",
        "plugin",
        "broken",
        "e1400patch",
        "netfix",
    ]


async def test_install_with_requirement_and_uninstall(
    game_dir: Path, database: Database, downloads: Any
) -> None:
    service = PatchService(Game.open(game_dir, database), database)
    original_ini = (game_dir / "game.ini").read_bytes()
    assert service.compatible(service.get("netfix")) is True
    assert service.compatible(service.get("plugin")) is False
    assert await service.install("netfix") == ["e1400patch", "netfix"]
    assert (game_dir / "patches" / "netfix" / "netfix.dll").exists()
    assert b"Server=e1400patch\\server.dll" in (game_dir / "game.ini").read_bytes()
    assert service.status(service.get("e1400patch")).required_by == ["netfix"]

    with pytest.raises(PatchError):
        service.uninstall("e1400patch")  # netfix needs it
    with pytest.raises(PatchError):
        await service.install("plugin")  # conflicts with netfix
    service.uninstall("e1400patch", with_dependents=True)
    assert (game_dir / "game.ini").read_bytes() == original_ini
    assert (
        not (game_dir / "patches").exists() and not (game_dir / "e1400patch").exists()
    )


async def test_failed_install_rolls_back(
    game_dir: Path, database: Database, downloads: Any
) -> None:
    service = PatchService(Game.open(game_dir, database), database)
    with pytest.raises(PatchError):
        await service.install("broken")
    assert "broken" not in service.state.patches and not (game_dir / "x.dll").exists()


async def test_existing_file_is_restored_and_update(
    game_dir: Path, database: Database, downloads: Any
) -> None:
    (game_dir / "ddraw.dll").write_bytes(b"store")
    service = PatchService(Game.open(game_dir, database), database)
    assert service.status(service.get("ddraw_compat")).state == PatchState.UNMANAGED
    await service.install("ddraw_compat")
    assert service.status(service.get("ddraw_compat")).state == PatchState.INSTALLED
    service.get("ddraw_compat").version = "0.7.0"
    assert service.status(service.get("ddraw_compat")).state == PatchState.UPDATE
    await service.install("ddraw_compat")
    assert service.state.patches["ddraw_compat"].version == "0.7.0"
    service.uninstall("ddraw_compat")
    assert (game_dir / "ddraw.dll").read_bytes() == b"store"


async def test_unmanaged_loader_is_taken_over(
    game_dir: Path, database: Database, downloads: Any
) -> None:
    (game_dir / "e1400patch").mkdir()
    (game_dir / "e1400patch" / "server.dll").write_bytes(b"old shim")
    (game_dir / "e1400patch" / "e1400patch.ini").write_bytes(
        b"[install]\r\nprevious_server=Server\\server.dll\r\n"
    )
    game_ini = (game_dir / "game.ini").read_bytes()
    (game_dir / "game.ini").write_bytes(
        game_ini.replace(b"Server=Server\\server.dll", b"Server=e1400patch\\server.dll")
    )
    service = PatchService(Game.open(game_dir, database), database)
    assert service.status(service.get("e1400patch")).state == PatchState.UNMANAGED
    await service.install("e1400patch")
    service.uninstall("e1400patch")
    assert (game_dir / "game.ini").read_bytes() == game_ini
    assert not (game_dir / "e1400patch").exists()


def test_path_problems(game_dir: Path, database: Database) -> None:
    import sys

    game = Game.open(game_dir, database)
    if sys.platform != "win32":
        assert game.path_problems() == []
        return
    assert [p[0] for p in game.path_problems()] == ["GfxPath"]
    assert game.repair_paths() == ["GfxPath"]
    assert game.path_problems() == []


async def test_recommendations(
    game_dir: Path, database: Database, downloads: Any
) -> None:
    from europa1400_manager.core import ini, recommendations
    from europa1400_manager.core.models import RecommendationTable

    database.tables[RecommendationTable] = _table(
        RecommendationTable,
        [
            {
                "id": "gold",
                "name": "Gold",
                "metadata": {"edition": "gold"},
                "patches": [{"patch": "ddraw_compat", "level": "optional"}],
                "settings": [
                    {
                        "section": "General",
                        "key": "Bildmodus",
                        "value": "DIRECTWINDOW",
                        "level": "optional",
                    },
                    {"section": "General", "key": "show_intro", "value": "0"},
                ],
            },
            {
                "id": "de",
                "name": "DE",
                "metadata": {"edition": "gold", "language": "de"},
                "patches": [
                    {
                        "patch": "netfix",
                        "level": "recommended",
                        "reason": {"en": "host fix", "de": "Host-Fix"},
                    },
                    {"patch": "plugin"},
                ],
            },
            {
                "id": "en",
                "name": "EN",
                "metadata": {"language": "en"},
                "patches": [{"patch": "dxvk"}],
            },
        ],
    )
    service = PatchService(Game.open(game_dir, database), database)
    items = recommendations.items(service, "de")
    keys = [(i.key, i.level) for i in items]
    assert keys == [
        ("netfix", "recommended"),
        ("plugin", "recommended"),
        ("game.ini|general|show_intro", "recommended"),
        ("ddraw_compat", "optional"),
        ("game.ini|general|bildmodus", "optional"),
    ]
    netfix = next(i for i in items if i.key == "netfix")
    assert netfix.reason == "Host-Fix" and netfix.available and not netfix.done
    plugin = next(i for i in items if i.key == "plugin")
    assert not plugin.available  # the database marks it for English games only
    assert all(i.key != "dxvk" for i in items)  # English recommendation does not apply

    chosen = [i for i in items if i.recommended and i.available]
    done = await recommendations.apply(service, chosen)
    assert "netfix" in done and "e1400patch" in done
    assert ini.get(game_dir / "game.ini", "General", "show_intro") == "0"
    assert (game_dir / "game.ini.manager-backup").exists()
    after = {i.key: i.done for i in recommendations.items(service, "de")}
    assert after["netfix"] and not after["ddraw_compat"]
