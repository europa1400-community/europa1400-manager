"""Recommended setups (europa1400-database recommendation.yml): what fits the detected game, and one-click applying."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from europa1400_manager.core import ini
from europa1400_manager.core.handlers import Progress
from europa1400_manager.core.models import RecommendationTable, RecommendedSetting
from europa1400_manager.core.patches import PatchService

log = logging.getLogger(__name__)

RECOMMENDED = "recommended"
OPTIONAL = "optional"


@dataclass
class RecommendedItem:
    kind: str  # "patch" or "setting"
    key: str  # patch id, or "file|section|key"
    title: str
    level: str
    reason: str
    done: bool  # already installed / already set
    available: bool  # the patch exists and is not marked as unfit for this game
    setting: RecommendedSetting | None = None

    @property
    def recommended(self) -> bool:
        return self.level == RECOMMENDED


def _text(texts: dict[str, str] | None, language: str) -> str:
    if not texts:
        return ""
    return texts.get(language) or texts.get("en") or next(iter(texts.values()), "")


def items(service: PatchService, language: str) -> list[RecommendedItem]:
    """Everything recommended for this game, recommended before optional, without duplicates."""
    game = service.game
    found: dict[str, RecommendedItem] = {}
    for recommendation in service.database.elements(RecommendationTable):
        if not game.info.matches(vars(recommendation.metadata)):
            continue
        for entry in recommendation.patches or []:
            patch = service.database.patch(entry.patch)
            if patch is None or entry.patch in found:
                continue
            status = service.status(patch)
            found[entry.patch] = RecommendedItem(
                "patch",
                entry.patch,
                patch.name,
                entry.level,
                _text(entry.reason, language),
                status.installed,
                status.compatible is not False,
            )
        for setting in recommendation.settings or []:
            key = f"{setting.file}|{setting.section}|{setting.key}".lower()
            if key in found:
                continue
            path = game.path / setting.file
            current = (
                ini.get(path, setting.section, setting.key) if path.exists() else None
            )
            found[key] = RecommendedItem(
                "setting",
                key,
                f"{setting.file} [{setting.section}] {setting.key} = {setting.value}",
                setting.level,
                _text(setting.reason, language),
                (current or "").lower() == setting.value.lower(),
                path.exists(),
                setting,
            )
    return sorted(
        found.values(), key=lambda item: (not item.recommended, item.kind != "patch")
    )


async def apply(
    service: PatchService,
    chosen: list[RecommendedItem],
    progress: Progress | None = None,
) -> list[str]:
    """Install the chosen patches and set the chosen values; returns what was done."""
    game = service.game
    game.ensure_not_running()
    game.check_writable()
    done: list[str] = []
    for item in chosen:
        if item.kind == "patch" and not item.done and item.available:
            done += await service.install(item.key, progress)
    changes: dict[str, dict[tuple[str, str], str | None]] = {}
    for item in chosen:
        if item.kind == "setting" and item.setting and not item.done and item.available:
            changes.setdefault(item.setting.file, {})[
                (item.setting.section, item.setting.key)
            ] = item.setting.value
    for file, values in changes.items():
        if file.lower() == "game.ini":
            game.backup_game_ini()
        ini.set_values(game.path / file, values)
        done += [f"{file} {key}" for _, key in values]
    log.info("applied recommendations: %s", done)
    return done
