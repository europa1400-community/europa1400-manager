from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from dataclass_wizard import YAMLWizard


def table(filename: str) -> Any:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.FILE_NAME = filename
        return cls

    return wrapper


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
    path: str
    tl_path: str


@dataclass
class GameExecutableToMetadata(DatabaseElement):
    executable: str
    metadata: GameMetadataId


@dataclass
class GamePatch(NamedDatabaseElement):
    pass


@dataclass
class GameMetadataToPatch(DatabaseElement):
    metadata: GameMetadataId
    patch: str


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
@table("patch.yml")
class GamePatchTable(DatabaseTable):
    elements: list[GamePatch]


@dataclass
@table("metadata_to_patch.yml")
class GameMetadataToPatchTable(DatabaseTable):
    elements: list[GameMetadataToPatch]


@dataclass
class GameMetadataId(YAMLWizard):
    edition: str | None = None
    version: str | None = None
    distribution: str | None = None
    language: str | None = None
    drm: str | None = None


@dataclass
class GameMetadata(YAMLWizard):
    edition: GameEdition | None = None
    version: GameVersion | None = None
    distribution: GameDistribution | None = None
    language: GameLanguage | None = None
    drm: GameDrm | None = None
