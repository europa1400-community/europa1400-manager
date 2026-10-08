import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from europa1400_manager.core import download
from europa1400_manager.core.errors import DownloadError


def _zip(path: Path, entries: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return path


def test_extract_zip(tmp_path: Path) -> None:
    archive = _zip(tmp_path / "a.zip", {"x/ddraw.dll": b"1", "readme.txt": b"2"})
    files = download.extract(archive, tmp_path / "out")
    assert sorted(f.relative_to(tmp_path / "out").as_posix() for f in files) == [
        "readme.txt",
        "x/ddraw.dll",
    ]


@pytest.mark.parametrize(
    "name", ["../evil.dll", "/abs.dll", "C:/abs.dll", "a/../../evil.dll"]
)
def test_zip_slip_is_refused(tmp_path: Path, name: str) -> None:
    archive = _zip(tmp_path / "a.zip", {name: b"x"})
    with pytest.raises(DownloadError):
        download.extract(archive, tmp_path / "out")
    assert not (tmp_path / "evil.dll").exists()


def test_tar_symlink_is_refused(tmp_path: Path) -> None:
    archive = tmp_path / "a.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("link")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        tar.addfile(info)
    with pytest.raises(DownloadError):
        download.extract(archive, tmp_path / "out")


def test_tar_regular(tmp_path: Path) -> None:
    archive = tmp_path / "a.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        data = b"dll"
        info = tarfile.TarInfo("dxvk/x32/d3d9.dll")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    files = download.extract(archive, tmp_path / "out")
    assert files[0].read_bytes() == b"dll"


def test_file_name_of() -> None:
    assert download.file_name_of("https://x/y/netfix.zip?raw=1") == "netfix.zip"
