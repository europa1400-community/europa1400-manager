"""Is there a newer manager release? (GitHub releases API, no account needed)"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import aiohttp

from europa1400_manager._version import __version__

log = logging.getLogger(__name__)

RELEASES = "https://api.github.com/repos/europa1400-community/europa1400-manager/releases/latest"
RELEASE_PAGE = (
    "https://github.com/europa1400-community/europa1400-manager/releases/latest"
)


@dataclass
class Update:
    version: str
    url: str
    notes: str


def _parse(version: str) -> tuple[int, ...] | None:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)$", version.strip())
    return tuple(int(x) for x in match.groups()) if match else None


def is_newer(candidate: str, current: str = __version__) -> bool:
    new, old = _parse(candidate), _parse(current)
    return new is not None and old is not None and new > old


async def check() -> Update | None:
    """The latest release if it is newer than this build; None otherwise or on any problem (offline, dev build)."""
    if _parse(__version__) is None:
        return None
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                RELEASES, headers={"Accept": "application/vnd.github+json"}
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
    except Exception as error:  # noqa: BLE001
        log.info("update check failed: %s", error)
        return None
    version = str(data.get("tag_name", ""))
    if not is_newer(version):
        return None
    return Update(
        version.lstrip("v"),
        str(data.get("html_url") or RELEASE_PAGE),
        str(data.get("body") or ""),
    )
