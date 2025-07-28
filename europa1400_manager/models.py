from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, TypeVar

from dataclass_wizard import YAMLWizard

TTable = TypeVar("TTable", bound="DatabaseTable")


def table(filename: str):
    def wrapper(cls: type[TTable]) -> type[TTable]:
        cls.FILE_NAME = filename
        return dataclass(cls)

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
class DatabaseTable(YAMLWizard):
    FILE_NAME: ClassVar[str]

    id: str
    name: str
    elements: list[DatabaseElement]


@table("language.yml")
class GameLanguageTable(DatabaseTable):
    elements: list[GameLanguage]


@table("edition.yml")
class GameEditionTable(DatabaseTable):
    elements: list[GameEdition]


@table("version.yml")
class GameVersionTable(DatabaseTable):
    elements: list[GameVersion]


@table("distribution.yml")
class GameDistributionTable(DatabaseTable):
    elements: list[GameDistribution]


@table("drm.yml")
class GameDrmTable(DatabaseTable):
    elements: list[GameDrm]


@table("executable.yml")
class GameExecutableTable(DatabaseTable):
    elements: list[GameExecutable]


@table("executable_to_metadata.yml")
class GameExecutableToMetadataTable(DatabaseTable):
    elements: list[GameExecutableToMetadata]


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
