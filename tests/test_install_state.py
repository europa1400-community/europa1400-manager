from pathlib import Path

import pytest

from europa1400_manager.core.errors import PatchError
from europa1400_manager.core.install_state import InstallState


def _source(tmp_path: Path, name: str, data: bytes) -> Path:
    path = tmp_path / "src" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_install_backs_up_and_uninstall_restores(
    tmp_path: Path, game_dir: Path
) -> None:
    (game_dir / "ddraw.dll").write_bytes(b"store's own ddraw")
    original_ini = (game_dir / "game.ini").read_bytes()
    state = InstallState(game_dir)
    transaction = state.begin("ddraw_compat", "0.6.0")
    transaction.write_file(_source(tmp_path, "ddraw.dll", b"new ddraw"), "ddraw.dll")
    transaction.write_file(_source(tmp_path, "a.dll", b"a"), "sub/dir/a.dll")
    transaction.set_ini("game.ini", "General", "Bildmodus", "DIRECTWINDOW")
    transaction.commit()

    state = InstallState(game_dir)  # reloaded from disk
    assert (game_dir / "ddraw.dll").read_bytes() == b"new ddraw"
    assert state.patches["ddraw_compat"].version == "0.6.0"
    assert state.uninstall("ddraw_compat") == []
    assert (game_dir / "ddraw.dll").read_bytes() == b"store's own ddraw"
    assert not (game_dir / "sub").exists()
    assert (game_dir / "game.ini").read_bytes() == original_ini
    assert "ddraw_compat" not in InstallState(game_dir).patches


def test_rollback(tmp_path: Path, game_dir: Path) -> None:
    (game_dir / "d3d8.dll").write_bytes(b"old")
    original_ini = (game_dir / "game.ini").read_bytes()
    state = InstallState(game_dir)
    transaction = state.begin("x", None)
    transaction.own_dir("newdir")
    transaction.write_file(_source(tmp_path, "d3d8.dll", b"new"), "d3d8.dll")
    transaction.write_file(_source(tmp_path, "f", b"f"), "newdir/deep/f")
    transaction.set_ini("game.ini", "Network", "Server", "e1400patch\\server.dll")
    transaction.rollback()
    assert (game_dir / "d3d8.dll").read_bytes() == b"old"
    assert not (game_dir / "newdir").exists()
    assert (game_dir / "game.ini").read_bytes() == original_ini
    assert "x" not in state.patches


def test_changed_file_is_kept(tmp_path: Path, game_dir: Path) -> None:
    state = InstallState(game_dir)
    transaction = state.begin("x", None)
    transaction.write_file(_source(tmp_path, "f.dll", b"ours"), "f.dll")
    transaction.commit()
    (game_dir / "f.dll").write_bytes(b"player's")
    warnings = state.uninstall("x")
    assert len(warnings) == 1 and (game_dir / "f.dll").read_bytes() == b"player's"


def test_file_of_another_patch_is_refused(tmp_path: Path, game_dir: Path) -> None:
    state = InstallState(game_dir)
    transaction = state.begin("a", None)
    transaction.write_file(_source(tmp_path, "d3d9.dll", b"a"), "d3d9.dll")
    transaction.commit()
    with pytest.raises(PatchError):
        state.begin("b", None).write_file(
            _source(tmp_path, "d3d9.dll", b"b"), "D3D9.dll"
        )


def test_ini_in_own_file_and_owned_dir(tmp_path: Path, game_dir: Path) -> None:
    state = InstallState(game_dir)
    transaction = state.begin("loader", None)
    transaction.own_dir("e1400patch")
    transaction.write_file(
        _source(tmp_path, "c.ini", b"[a]\r\nb=1\r\n"), "e1400patch/c.ini"
    )
    transaction.set_ini("e1400patch/c.ini", "a", "b", "2")
    transaction.commit()
    (game_dir / "e1400patch" / "logs").mkdir()
    (game_dir / "e1400patch" / "logs" / "x.log").write_text("log")
    assert state.uninstall("loader") == []
    assert not (game_dir / "e1400patch").exists()


def test_unsafe_target_is_refused(tmp_path: Path, game_dir: Path) -> None:
    transaction = InstallState(game_dir).begin("x", None)
    with pytest.raises(PatchError):
        transaction.write_file(_source(tmp_path, "f", b"f"), "../outside.dll")
