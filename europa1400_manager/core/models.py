"""Tables of europa1400-database (data/*.yml).

New fields are always optional: older managers ignore unknown fields, but fail on unknown enum values (patch types).
New patch types therefore go into tables of their own (e1400patch.yml).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any, ClassVar

from dataclass_wizard import YAMLWizard


class PatchType(StrEnum):
    SIMPLE = auto()  # one file, downloaded into the game folder
    ARCHIVE = auto()  # files taken from an archive
    E1400PATCH_LOADER = auto()  # europa1400-patches: the loader (e1400patch/)
    E1400PATCH_MODULE = auto()  # europa1400-patches: a patch module (patches/<id>/)


class PatchCategory(StrEnum):
    MULTIPLAYER = auto()
    GRAPHICS = auto()
    COMPATIBILITY = auto()
    GAMEPLAY = auto()
    TOOLS = auto()
    OTHER = auto()


@dataclass
class FileOperation(YAMLWizard):
    """A change after installing: currently `ini` (set section/key in file_name to value)."""

    type: str
    file_name: str | None = None
    section: str | None = None
    key: str | None = None
    value: str | int | float | bool | None = None


@dataclass
class DatabaseElement(YAMLWizard):
    id: str


@dataclass
class NamedDatabaseElement(DatabaseElement):
    name: str


@dataclass
class GameLanguage(NamedDatabaseElement):
    pass


@dataclass
class GameEdition(NamedDatabaseElement):
    pass


@dataclass
class GameVersion(NamedDatabaseElement):
    pass


@dataclass
class GameDistribution(NamedDatabaseElement):
    pass


@dataclass
class GameDrm(NamedDatabaseElement):
    pass


@dataclass
class GameExecutable(DatabaseElement):
    """A pair of game executables by file name (the D3D8 build and the DX6 "T&L" build; names differ per store)."""

    path: str
    tl_path: str


@dataclass
class GameMetadataId(YAMLWizard):
    edition: str | None = None
    version: str | None = None
    distribution: str | None = None
    language: str | None = None
    drm: str | None = None


@dataclass
class GameExecutableToMetadata(DatabaseElement):
    executable: str
    metadata: GameMetadataId


@dataclass
class GameFile(DatabaseElement):
    """A known game file, identified by its SHA-256 (exact build identification)."""

    sha256: str
    file: str  # usual path relative to the game folder (informational)
    role: str  # game_d3d8 | game_dx6 | server
    metadata: GameMetadataId = field(default_factory=GameMetadataId)
    note: str | None = None


@dataclass
class GamePatch(NamedDatabaseElement):
    url: str
    type: PatchType
    file_name: str | list[str] | None = None
    archive_file_name: str | list[str] | None = None
    file_operations: list[FileOperation] | None = None
    requires: list[str] | None = None  # installed first, automatically
    conflicts: list[str] | None = None  # must not be installed together
    description: dict[str, str] | None = (
        None  # by language code: {"en": ..., "de": ...}
    )
    category: str | None = None  # PatchCategory value
    homepage: str | None = None
    author: str | None = None
    version: str | None = None  # shown to the player; a change offers an update
    sha256: str | None = (
        None  # of the download, checked when set (pinned downloads only)
    )

    def text(self, language: str) -> str:
        if not self.description:
            return ""
        return (
            self.description.get(language)
            or self.description.get("en")
            or next(iter(self.description.values()), "")
        )


@dataclass
class RecommendedPatch(YAMLWizard):
    patch: str
    level: str = "recommended"  # "recommended" (selected by default) or "optional"
    reason: dict[str, str] | None = None


@dataclass
class RecommendedSetting(YAMLWizard):
    section: str
    key: str
    value: str
    file: str = "game.ini"
    level: str = "recommended"
    reason: dict[str, str] | None = None


@dataclass
class Recommendation(NamedDatabaseElement):
    """A one-click setup for the game versions its metadata matches."""

    metadata: GameMetadataId = field(default_factory=GameMetadataId)
    patches: list[RecommendedPatch] | None = None
    settings: list[RecommendedSetting] | None = None


@dataclass
class GameMetadataToPatch(DatabaseElement):
    metadata: GameMetadataId
    patch: str


def table(filename: str) -> Any:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.FILE_NAME = filename
        return cls

    return wrapper


@dataclass
class DatabaseTable(YAMLWizard):
    FILE_NAME: ClassVar[str]

    id: str
    name: str
    elements: list[Any]


@dataclass
@table("language.yml")
class GameLanguageTable(DatabaseTable):
    elements: list[GameLanguage]


@dataclass
@table("edition.yml")
class GameEditionTable(DatabaseTable):
    elements: list[GameEdition]


@dataclass
@table("version.yml")
class GameVersionTable(DatabaseTable):
    elements: list[GameVersion]


@dataclass
@table("distribution.yml")
class GameDistributionTable(DatabaseTable):
    elements: list[GameDistribution]


@dataclass
@table("drm.yml")
class GameDrmTable(DatabaseTable):
    elements: list[GameDrm]


@dataclass
@table("executable.yml")
class GameExecutableTable(DatabaseTable):
    elements: list[GameExecutable]


@dataclass
@table("executable_to_metadata.yml")
class GameExecutableToMetadataTable(DatabaseTable):
    elements: list[GameExecutableToMetadata]


@dataclass
@table("game_file.yml")
class GameFileTable(DatabaseTable):
    elements: list[GameFile]


@dataclass
@table("patch.yml")
class GamePatchTable(DatabaseTable):
    elements: list[GamePatch]


@dataclass
@table("e1400patch.yml")
class GameE1400PatchTable(DatabaseTable):
    """Patches of europa1400-patches; a table of its own because managers up to 1.1 fail on the new patch types."""

    elements: list[GamePatch]


@dataclass
@table("recommendation.yml")
class RecommendationTable(DatabaseTable):
    elements: list[Recommendation]


@dataclass
@table("metadata_to_patch.yml")
class GameMetadataToPatchTable(DatabaseTable):
    elements: list[GameMetadataToPatch]


ALL_TABLES: list[type[DatabaseTable]] = [
    GameLanguageTable,
    GameEditionTable,
    GameVersionTable,
    GameDistributionTable,
    GameDrmTable,
    GameExecutableTable,
    GameExecutableToMetadataTable,
    GameFileTable,
    GamePatchTable,
    GameE1400PatchTable,
    GameMetadataToPatchTable,
    RecommendationTable,
]
