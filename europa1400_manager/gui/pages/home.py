"""Home: the detected game, starting it, notices; first-run setup when no game is chosen."""

from __future__ import annotations

import asyncio
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from europa1400_manager.core.detection import FIELDS
from europa1400_manager.core.errors import PermissionProblemError
from europa1400_manager.gui import theme
from europa1400_manager.gui.state import AppState
from europa1400_manager.gui.widgets import (
    Banner,
    Card,
    Chip,
    Page,
    clear,
    muted,
    primary,
)
from europa1400_manager import i18n
from europa1400_manager.i18n import tr


class HomePage(Page):
    def __init__(self, state: AppState, show_patches: object) -> None:
        super().__init__(tr("ui.home"))
        self.state = state
        self.show_patches = show_patches
        state.game_changed.connect(self.refresh)
        state.patches_changed.connect(self.refresh)
        state.database_loaded.connect(self.refresh)

    def refresh(self) -> None:
        clear(self.content)
        clear(self.notices)
        if self.state.game is None:
            self._setup()
        else:
            self._game()

    # --- no game yet -------------------------------------------------------------------------------------------

    def _setup(self) -> None:
        self.title.setText(tr("ui.welcome"))
        card = Card()
        card.body.addWidget(QLabel(f"<b>{tr('ui.choose_game')}</b>"))
        card.body.addWidget(muted(tr("ui.choose_game_hint")))
        for path in self.state.installations:
            row = QHBoxLayout()
            row.addWidget(QLabel(str(path)), 1)
            button = primary(tr("ui.use"))
            button.clicked.connect(lambda _=False, p=path: self._open(p))
            row.addWidget(button)
            card.body.addLayout(row)
        if not self.state.installations:
            card.body.addWidget(muted(tr("ui.nothing_found")))
        browse = QPushButton(tr("ui.browse"))
        browse.clicked.connect(self._browse)
        card.body.addWidget(browse)
        self.content.addWidget(card)

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("ui.choose_game"))
        if folder:
            self._open(Path(folder))

    def _open(self, path: Path) -> None:
        self.state.run(self, lambda: self.state.open_game(path), tr("ui.identifying"))

    # --- game ----------------------------------------------------------------------------------------------------

    def _game(self) -> None:
        game = self.state.game
        assert game is not None
        info = game.info
        database = self.state.database
        language = info.metadata.get("language")
        self.title.setText(tr("ui.home"))

        card = Card(spacing=10)
        title = QLabel(
            "Die Gilde Gold"
            if language == "de" and info.metadata.get("edition") == "gold"
            else "Die Gilde"
            if language == "de"
            else "Europa 1400: The Guild Gold"
            if info.metadata.get("edition") == "gold"
            else "Europa 1400: The Guild"
        )
        title.setObjectName("GameTitle")
        card.body.addWidget(title)
        chips = QHBoxLayout()
        for key in FIELDS:
            value = info.metadata.get(key)
            if not value or (key == "drm" and value == "none"):
                continue
            guessed = info.sources.get(key) != "hash"
            chips.addWidget(
                Chip(
                    tr(f"meta.{key}.{value}")
                    if i18n.has(f"meta.{key}.{value}")
                    else str(database.name_of(key, value)),
                    "muted" if guessed else "accent",
                    tr("ui.guessed") if guessed else tr("ui.exact"),
                )
            )
        chips.addWidget(
            Chip(
                tr("ui.known_build") if info.exactly_known else tr("ui.unknown_build"),
                "success" if info.exactly_known else "warning",
                tr("ui.known_build_hint")
                if info.exactly_known
                else tr("ui.unknown_build_hint"),
            )
        )
        chips.addStretch(1)
        card.body.addLayout(chips)
        card.body.addWidget(muted(str(game.path)))

        buttons = QHBoxLayout()
        if info.exe_d3d8:
            play = primary(tr("ui.play"))
            play.setIcon(theme.icon("play", "#1b1406"))
            play.setToolTip(tr("ui.play_d3d8_hint", exe=info.exe_d3d8.name))
            play.clicked.connect(lambda: self._launch("d3d8"))
            buttons.addWidget(play)
        if info.exe_dx6:
            classic = QPushButton(tr("ui.play_dx6"))
            classic.setToolTip(tr("ui.play_dx6_hint", exe=info.exe_dx6.name))
            classic.clicked.connect(lambda: self._launch("dx6"))
            buttons.addWidget(classic)
        folder = QPushButton(tr("ui.open_folder"))
        folder.setIcon(theme.icon("folder"))
        folder.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(game.path)))
        )
        buttons.addWidget(folder)
        buttons.addStretch(1)
        card.body.addLayout(buttons)
        self.content.addWidget(card)

        self._notices()
        self._patch_summary()

    def _notices(self) -> None:
        game = self.state.game
        assert game is not None
        problems = game.path_problems()
        if problems:
            keys = ", ".join(p[0] for p in problems)
            self.notices.addWidget(
                Banner(
                    tr("ui.paths_wrong", keys=keys),
                    "warning",
                    tr("ui.repair"),
                    self._repair,
                )
            )
        try:
            game.check_writable()
        except PermissionProblemError as error:
            self.notices.addWidget(Banner(str(error), "danger"))
        if self.state.database.source in ("cache", "partial-cache"):
            self.notices.addWidget(Banner(tr("ui.offline"), "info"))
        elif self.state.database.source == "none":
            self.notices.addWidget(Banner(tr("ui.no_database"), "danger"))

    def _repair(self) -> None:
        game = self.state.game
        assert game is not None

        async def work() -> None:
            await asyncio.to_thread(game.repair_paths)

        self.state.run(self, work, done=lambda _: self.refresh())

    def _patch_summary(self) -> None:
        service = self.state.service
        if service is None or not self.state.database.patches:
            return
        statuses = service.statuses()
        installed = [s for s in statuses if s.installed]
        updates = [s for s in statuses if s.state.value == "update"]
        card = Card()
        card.body.addWidget(QLabel(f"<b>{tr('ui.patches')}</b>"))
        card.body.addWidget(
            muted(tr("ui.patch_summary", installed=len(installed), total=len(statuses)))
        )
        if updates:
            card.body.addWidget(
                Banner(
                    tr(
                        "ui.updates_available",
                        names=", ".join(s.patch.name for s in updates),
                    ),
                    "info",
                )
            )
        names = QVBoxLayout()
        for status in installed:
            names.addWidget(QLabel(f"✓  {status.patch.name}"))
        card.body.addLayout(names)
        button = primary(tr("ui.manage_patches"))
        button.clicked.connect(self.show_patches)  # type: ignore[arg-type]
        row = QHBoxLayout()
        row.addWidget(button)
        row.addStretch(1)
        card.body.addLayout(row)
        self.content.addWidget(card)

    def _launch(self, renderer: str) -> None:
        game = self.state.game
        assert game is not None

        async def work() -> None:
            game.launch(renderer)

        self.state.run(self, work)
