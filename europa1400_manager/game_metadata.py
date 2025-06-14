from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from europa1400_manager.const import (
    EUROPA1400_EXE_PATH,
    EUROPA1400_GOLD_EXE_PATH,
    EUROPA1400_GOLD_TL_EXE_PATH,
    EUROPA1400_TL_EXE_PATH,
    GILDE_EXE_PATH,
    GILDE_GOLD_EXE_PATH,
    GILDE_GOLD_TL_EXE_PATH,
    GILDE_TL_EXE_PATH,
    GameDistribution,
    GameDrm,
    GameEdition,
    GameLanguage,
    GameVersion,
)


@dataclass
class GameMetadata:
    edition: GameEdition | None = None
    version: GameVersion | None = None
    distribution: GameDistribution | None = None
    language: GameLanguage | None = None
    drm: GameDrm | None = None

    @property
    def identifier(self) -> str:
        """Generate a unique identifier for the game based on its properties."""
        if (
            self.edition is None
            or self.version is None
            or self.distribution is None
            or self.language is None
        ):
            raise ValueError("All properties must be set to generate an identifier.")

        return f"{self.edition.value}_{self.version.value}_{self.distribution.value}_{self.language.value}"

    @property
    def executable_path(self) -> Path:
        if self.edition is None:
            raise ValueError("Edition must be set to determine the executable path.")

        match self.edition:
            case GameEdition.STANDARD:
                return (
                    Path(GILDE_TL_EXE_PATH)
                    if self.language == GameLanguage.GERMAN
                    else Path(EUROPA1400_TL_EXE_PATH)
                )
            case GameEdition.GOLD:
                return (
                    Path(GILDE_GOLD_TL_EXE_PATH)
                    if self.language == GameLanguage.GERMAN
                    else Path(EUROPA1400_GOLD_TL_EXE_PATH)
                )
            case _:
                raise ValueError(f"Unsupported edition: {self.edition}")

    @property
    def tl_executable_path(self) -> Path:
        if self.edition is None:
            raise ValueError("Edition must be set to determine the executable path.")

        match self.edition:
            case GameEdition.STANDARD:
                return (
                    Path(GILDE_EXE_PATH)
                    if self.language == GameLanguage.GERMAN
                    else Path(EUROPA1400_EXE_PATH)
                )
            case GameEdition.GOLD:
                return (
                    Path(GILDE_GOLD_EXE_PATH)
                    if self.language == GameLanguage.GERMAN
                    else Path(EUROPA1400_GOLD_EXE_PATH)
                )
            case _:
                raise ValueError(f"Unsupported edition: {self.edition}")

    def calc_changes(
        self,
        other: Self,
        ignore_from_none: bool = True,
        ignore_to_none: bool = True,
    ) -> list[tuple[Any, Any]]:
        """Check if there are any changes compared to another GameInformation instance."""
        changes: list[tuple[str, tuple[Any, Any]]] = []

        for attr in self.__dataclass_fields__:
            self_value = getattr(self, attr)
            other_value = getattr(other, attr)

            if ignore_from_none and self_value is None:
                continue

            if ignore_to_none and other_value is None:
                continue

            if self_value != other_value:
                changes.append((attr, (self_value, other_value)))

        return changes

    def merge(self, other: Self, decisions: list[tuple[str, Any]]) -> None:
        """Merge another GameInformation instance into this one based on decisions."""
        for attr in other.__dataclass_fields__:
            self_value = getattr(self, attr)
            other_value = getattr(other, attr)

            chosen_value = self_value if self_value is not None else other_value

            if self_value is not None and self_value != other_value:
                if attr not in [d[0] for d in decisions]:
                    raise ValueError(
                        f"Decision for attribute {attr} not found in decisions."
                    )

                chosen_value = next(d[1] for d in decisions if d[0] == attr)

            setattr(self, attr, chosen_value)


EXECUTABLE_CANDIDATES = [
    (
        GILDE_EXE_PATH,
        GameMetadata(edition=GameEdition.STANDARD, language=GameLanguage.GERMAN),
    ),
    (
        GILDE_GOLD_EXE_PATH,
        GameMetadata(edition=GameEdition.GOLD, language=GameLanguage.GERMAN),
    ),
    (
        EUROPA1400_EXE_PATH,
        GameMetadata(edition=GameEdition.STANDARD),
    ),
    (
        EUROPA1400_GOLD_EXE_PATH,
        GameMetadata(edition=GameEdition.GOLD),
    ),
]

TL_EXECUTABLE_CANDIDATES = [
    (
        GILDE_TL_EXE_PATH,
        GameMetadata(edition=GameEdition.STANDARD, language=GameLanguage.GERMAN),
    ),
    (
        GILDE_GOLD_TL_EXE_PATH,
        GameMetadata(edition=GameEdition.GOLD, language=GameLanguage.GERMAN),
    ),
    (
        EUROPA1400_TL_EXE_PATH,
        GameMetadata(edition=GameEdition.STANDARD),
    ),
    (
        EUROPA1400_GOLD_TL_EXE_PATH,
        GameMetadata(edition=GameEdition.GOLD),
    ),
]

CANDIDATE_GROUPS = [
    EXECUTABLE_CANDIDATES,
    TL_EXECUTABLE_CANDIDATES,
]
