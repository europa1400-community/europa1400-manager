from pathlib import Path

import pytest

from europa1400_manager.core import monitor


def test_read_write_keeps_comments(tmp_path: Path) -> None:
    path = monitor.config_path(tmp_path)
    path.write_bytes(b"[monitorfix]\r\n; comment\r\nmonitor=1\r\n")
    assert monitor.installed(tmp_path)
    assert monitor.read(tmp_path) == 1
    monitor.write(tmp_path, 2)
    assert path.read_bytes() == b"[monitorfix]\r\n; comment\r\nmonitor=2\r\n"
    assert monitor.read(tmp_path) == 2


def test_defaults_and_limits(tmp_path: Path) -> None:
    assert not monitor.installed(tmp_path)
    monitor.config_path(tmp_path).write_text("[monitorfix]\nmonitor=abc\n")
    assert monitor.read(tmp_path) == 1
    with pytest.raises(ValueError):
        monitor.write(tmp_path, 9)
