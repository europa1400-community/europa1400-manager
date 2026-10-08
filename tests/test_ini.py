from pathlib import Path

from europa1400_manager.core import ini

ORIGINAL = b'; comment\r\n[General]\r\nBildmodus=FULLSCREEN\r\nName="Hans"\r\n\r\n[Sound]\r\nmsx=1\r\n'


def test_get_is_case_insensitive_and_strips_quotes(tmp_path: Path) -> None:
    path = tmp_path / "game.ini"
    path.write_bytes(ORIGINAL)
    assert ini.get(path, "general", "BILDMODUS") == "FULLSCREEN"
    assert ini.get(path, "General", "Name") == "Hans"
    assert ini.get(path, "General", "missing") is None
    assert ini.read_all(path)["sound"]["msx"] == "1"


def test_set_keeps_everything_else(tmp_path: Path) -> None:
    path = tmp_path / "game.ini"
    path.write_bytes(ORIGINAL)
    ini.set_value(path, "general", "bildmodus", "DIRECTWINDOW")
    assert path.read_bytes() == ORIGINAL.replace(b"FULLSCREEN", b"DIRECTWINDOW")


def test_add_and_remove(tmp_path: Path) -> None:
    path = tmp_path / "game.ini"
    path.write_bytes(ORIGINAL)
    ini.set_values(path, {("General", "show_intro"): "0", ("Network", "Port"): "7531"})
    text = path.read_bytes()
    assert b'Name="Hans"\r\nshow_intro=0\r\n\r\n[Sound]' in text
    assert text.endswith(b"[Network]\r\nPort=7531\r\n")
    ini.set_values(path, {("General", "show_intro"): None, ("Network", "Port"): None})
    assert b"show_intro" not in path.read_bytes() and b"Port=" not in path.read_bytes()


def test_umlauts_survive(tmp_path: Path) -> None:
    path = tmp_path / "game.ini"
    path.write_bytes("[Network]\r\nName=J\xfcrgen\r\n".encode("cp1252"))
    ini.set_value(path, "Network", "Port", "1")
    assert ini.get(path, "Network", "Name") == "J\xfcrgen"
