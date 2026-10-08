"""europa1400-database: fetched at start, cached for offline use.

Sources, in this order:
1. E1400_MANAGER_DATABASE_DIR: a local folder with the YAML tables (development, e.g. a checkout's data/ folder)
2. GitHub (raw files of the configured branch, default master); each successfully fetched table is cached
3. the cache of the last successful fetch (offline)
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar, cast

import aiohttp
import yaml
from dataclass_wizard import fromdict

from europa1400_manager.core import paths
from europa1400_manager.core.models import (
    ALL_TABLES,
    DatabaseElement,
    DatabaseTable,
    GameDistributionTable,
    GameDrmTable,
    GameE1400PatchTable,
    GameEditionTable,
    GameExecutableTable,
    GameExecutableToMetadataTable,
    GameFileTable,
    GameLanguageTable,
    GameMetadataToPatchTable,
    GamePatch,
    GamePatchTable,
    GameVersionTable,
)

log = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://raw.githubusercontent.com/europa1400-community/europa1400-database"
)
DEFAULT_BRANCH = "master"
TIMEOUT = aiohttp.ClientTimeout(total=20)

TTable = TypeVar("TTable", bound=DatabaseTable)


def parse_table(table_type: type[TTable], text: str) -> TTable:
    """Parse a table; elements this version cannot read (e.g. newer patch types) are skipped, not the whole table."""
    data = cast(dict[str, Any], yaml.safe_load(text)) or {}
    elements: list[Any] = []
    for element in data.get("elements") or []:
        try:
            fromdict(table_type, {**data, "elements": [element]})
            elements.append(element)
        except Exception as error:  # noqa: BLE001 - any unreadable element is skipped
            name = element.get("id") if isinstance(element, dict) else element
            log.warning("skipping %s element %r: %s", table_type.FILE_NAME, name, error)
    return fromdict(table_type, {**data, "elements": elements})


@dataclass
class Database:
    tables: dict[type[DatabaseTable], DatabaseTable] = field(default_factory=dict)
    source: str = "none"  # "local", "online", "cache", "partial-cache", "none"
    problems: list[str] = field(default_factory=list)

    def elements(self, table_type: type[TTable]) -> list[Any]:
        table = self.tables.get(table_type)
        return list(table.elements) if table else []

    def element(
        self, table_type: type[DatabaseTable], element_id: str | None
    ) -> Any | None:
        if element_id is None:
            return None
        return next(
            (
                e
                for e in self.elements(table_type)
                if cast(DatabaseElement, e).id == element_id
            ),
            None,
        )

    @property
    def patches(self) -> list[GamePatch]:
        return self.elements(GamePatchTable) + self.elements(GameE1400PatchTable)

    def patch(self, patch_id: str) -> GamePatch | None:
        return next((p for p in self.patches if p.id == patch_id), None)

    # convenience accessors used by detection and the UI
    def name_of(self, kind: str, element_id: str | None) -> str | None:
        table_type = {
            "edition": GameEditionTable,
            "version": GameVersionTable,
            "distribution": GameDistributionTable,
            "language": GameLanguageTable,
            "drm": GameDrmTable,
        }[kind]
        element = self.element(table_type, element_id)
        return element.name if element else element_id

    @property
    def files(self) -> list[Any]:
        return self.elements(GameFileTable)

    @property
    def executables(self) -> list[Any]:
        return self.elements(GameExecutableTable)

    @property
    def executable_mappings(self) -> list[Any]:
        return self.elements(GameExecutableToMetadataTable)

    @property
    def patch_mappings(self) -> list[Any]:
        return self.elements(GameMetadataToPatchTable)


def _cache_file(table_type: type[DatabaseTable]) -> Path:
    return paths.cache_dir() / "database" / table_type.FILE_NAME


async def _fetch_text(session: aiohttp.ClientSession, url: str) -> str:
    headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
    async with session.get(url, headers=headers) as response:
        if response.status == 404:
            raise FileNotFoundError(url)
        response.raise_for_status()
        return await response.text(encoding="utf-8")


async def load(branch: str | None = None, base_url: str | None = None) -> Database:
    """Load all tables; never raises (problems are listed in Database.problems)."""
    database = Database()
    local = os.environ.get("E1400_MANAGER_DATABASE_DIR")
    if local:
        for table_type in ALL_TABLES:
            path = Path(local) / table_type.FILE_NAME
            if path.exists():
                database.tables[table_type] = parse_table(
                    table_type, path.read_text(encoding="utf-8")
                )
        database.source = "local"
        return database

    base = f"{(base_url or os.environ.get('E1400_MANAGER_DATABASE_URL') or DEFAULT_URL).rstrip('/')}/{branch or DEFAULT_BRANCH}/data/"
    online, cached = 0, 0
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            results = await asyncio.gather(
                *(_fetch_text(session, base + t.FILE_NAME) for t in ALL_TABLES),
                return_exceptions=True,
            )
    except Exception as error:  # noqa: BLE001 - no network at all
        results = [error] * len(ALL_TABLES)

    for table_type, result in zip(ALL_TABLES, results):
        cache = _cache_file(table_type)
        if isinstance(result, str):
            try:
                database.tables[table_type] = parse_table(table_type, result)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(result, encoding="utf-8")
                online += 1
                continue
            except Exception as error:  # noqa: BLE001
                database.problems.append(f"{table_type.FILE_NAME}: {error}")
        elif isinstance(result, FileNotFoundError):
            continue  # table not in this branch (yet)
        else:
            database.problems.append(f"{table_type.FILE_NAME}: {result}")
        if cache.exists():
            database.tables[table_type] = parse_table(
                table_type, cache.read_text(encoding="utf-8")
            )
            cached += 1

    if cached and online:
        database.source = "partial-cache"
    elif cached:
        database.source = "cache"
    elif online:
        database.source = "online"
    log.info(
        "database: %d tables online, %d from cache, problems: %s",
        online,
        cached,
        database.problems,
    )
    return database
