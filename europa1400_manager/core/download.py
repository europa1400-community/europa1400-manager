"""Downloads and archive extraction with the checks a manager that writes into a game folder needs.

- downloads go to a temporary file, are size limited, can be verified against a SHA-256 and are cached by URL+hash
- archives (zip, tar.*) are extracted only if every member stays inside the target and is a regular file or folder
"""

from __future__ import annotations

import hashlib
import logging
import shutil
import tarfile
import zipfile
from collections.abc import Callable
from pathlib import Path, PurePosixPath

import aiohttp

from europa1400_manager.core import paths
from europa1400_manager.core.errors import DownloadError
from europa1400_manager.i18n import tr

log = logging.getLogger(__name__)

MAX_DOWNLOAD = 512 * 1024 * 1024
TIMEOUT = aiohttp.ClientTimeout(total=None, sock_connect=20, sock_read=60)
Progress = Callable[[int, int | None], None]  # (bytes done, total or None)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_name_of(url: str) -> str:
    name = PurePosixPath(url.split("?", 1)[0]).name
    return name or "download"


async def download(
    url: str, sha256: str | None = None, progress: Progress | None = None
) -> Path:
    """Download url into the download cache and return the file. With sha256 a cached copy is reused."""
    folder = (
        paths.cache_dir() / "downloads" / hashlib.sha256(url.encode()).hexdigest()[:16]
    )
    target = folder / file_name_of(url)
    if sha256 and target.exists() and sha256_of(target) == sha256.lower():
        log.info("using cached %s", target)
        return target
    folder.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    done = 0
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(
                url, headers={"User-Agent": "europa1400-manager"}
            ) as response:
                if response.status != 200:
                    raise DownloadError(
                        tr("error.download_http", url=url, status=response.status)
                    )
                total = response.content_length
                if total and total > MAX_DOWNLOAD:
                    raise DownloadError(tr("error.download_too_large", url=url))
                with partial.open("wb") as file:
                    async for chunk in response.content.iter_chunked(1 << 16):
                        done += len(chunk)
                        if done > MAX_DOWNLOAD:
                            raise DownloadError(tr("error.download_too_large", url=url))
                        file.write(chunk)
                        if progress:
                            progress(done, total)
    except aiohttp.ClientError as error:
        partial.unlink(missing_ok=True)
        raise DownloadError(
            tr("error.download_failed", url=url, error=error)
        ) from error
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    if sha256 and sha256_of(partial) != sha256.lower():
        partial.unlink(missing_ok=True)
        raise DownloadError(tr("error.download_checksum", url=url))
    partial.replace(target)
    return target


def _check_member(name: str, root: Path) -> Path:
    if name.startswith(("/", "\\")) or ":" in name.split("/")[0]:
        raise DownloadError(tr("error.archive_unsafe", member=name))
    destination = (root / name).resolve()
    if not destination.is_relative_to(root):
        raise DownloadError(tr("error.archive_unsafe", member=name))
    return destination


def is_archive(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz"))


def extract(archive: Path, target: Path) -> list[Path]:
    """Extract archive into target (created); returns the extracted files."""
    target.mkdir(parents=True, exist_ok=True)
    root = target.resolve()
    files: list[Path] = []
    if archive.name.lower().endswith(".zip"):
        with zipfile.ZipFile(archive) as zip_file:
            for info in zip_file.infolist():
                destination = _check_member(info.filename, root)
                if info.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                if (info.external_attr >> 16) & 0o170000 == 0o120000:  # symlink
                    raise DownloadError(
                        tr("error.archive_unsafe", member=info.filename)
                    )
                destination.parent.mkdir(parents=True, exist_ok=True)
                with zip_file.open(info) as source, destination.open("wb") as sink:
                    shutil.copyfileobj(source, sink)
                files.append(destination)
    else:
        with tarfile.open(archive, "r:*") as tar_file:
            for member in tar_file.getmembers():
                destination = _check_member(member.name, root)
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise DownloadError(tr("error.archive_unsafe", member=member.name))
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = tar_file.extractfile(member)
                if source is None:
                    continue
                with source, destination.open("wb") as sink:
                    shutil.copyfileobj(source, sink)
                files.append(destination)
    return files
