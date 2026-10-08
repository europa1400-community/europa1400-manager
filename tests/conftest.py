from __future__ import annotations

from pathlib import Path

import pytest

from europa1400_manager import i18n


@pytest.fixture(autouse=True)
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings, caches and logs of a test go to its temporary folder; texts in English."""
    for name in ("CONFIG", "CACHE", "LOG"):
        monkeypatch.setenv(f"E1400_MANAGER_{name}_DIR", str(tmp_path / name.lower()))
    i18n.set_language("en")


@pytest.fixture
def game_dir(tmp_path: Path) -> Path:
    """A fake GOG German installation (no game bytes: the executables are placeholders)."""
    game = tmp_path / "game"
    (game / "Server").mkdir(parents=True)
    (game / "Resources" / "gamedata" / "network").mkdir(parents=True)
    (game / "GildeGold_TL.exe").write_bytes(b"MZ fake d3d8 build")
    (game / "GildeGold.exe").write_bytes(b"MZ fake dx6 build")
    (game / "Server" / "server.dll").write_bytes(b"MZ fake server")
    (game / "goggame.dll").write_bytes(b"")
    (game / "Readme Patch 2.06 Gold.txt").write_text("readme")
    (game / "game.ini").write_bytes(
        b"[General]\r\nBildmodus=FULLSCREEN\r\nGfxPath=C:\\old\\resources\\\r\nlanguage=german\r\n\r\n"
        b"[Network]\r\nServer=Server\\server.dll\r\nPort=7531\r\n"
    )
    return game
