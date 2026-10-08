"""Home: the detected game, starting it, notices; first-run setup when no game is chosen."""

from __future__ import annotations

import asyncio
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from europa1400_manager.core import game_settings, recommendations
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
        self._recommendations()
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

    def _recommendations(self) -> None:
        service = self.state.service
        if service is None:
            return
        items = recommendations.items(service, i18n.language())
        if not items:
            return
        card = Card()
        title = QLabel(tr("ui.recommended_setup"))
        title.setObjectName("CardTitle")
        card.body.addWidget(title)
        missing = [i for i in items if i.recommended and not i.done and i.available]
        card.body.addWidget(
            muted(
                tr("ui.recommended_hint") if missing else tr("ui.recommended_complete")
            )
        )
        boxes: list[tuple[QCheckBox, recommendations.RecommendedItem]] = []
        for item in items:
            box = QCheckBox(_item_title(item))
            box.setChecked(item.done or (item.recommended and item.available))
            box.setEnabled(not item.done and item.available)
            tooltip = item.reason
            if not item.available:
                tooltip = tr("ui.not_for_this_game_hint")
            box.setToolTip(tooltip)
            row = QVBoxLayout()
            row.setSpacing(0)
            row.addWidget(box)
            label = item.reason if item.available else tr("ui.not_for_this_game_hint")
            level = (
                tr("ui.level_recommended")
                if item.recommended
                else tr("ui.level_optional")
            )
            done = f"  ·  {tr('ui.already_done')}" if item.done else ""
            note = muted(f"{level}{done}  ·  {label}")
            note.setContentsMargins(26, 0, 0, 6)
            row.addWidget(note)
            card.body.addLayout(row)
            boxes.append((box, item))
        apply = primary(tr("ui.apply_selected"))

        def update_button() -> None:
            apply.setEnabled(any(b.isChecked() and b.isEnabled() for b, _ in boxes))

        for box, _ in boxes:
            box.toggled.connect(update_button)
        update_button()
        apply.clicked.connect(
            lambda: self._apply(
                [i for b, i in boxes if b.isChecked() and b.isEnabled()]
            )
        )
        buttons = QHBoxLayout()
        buttons.addWidget(apply)
        buttons.addStretch(1)
        card.body.addLayout(buttons)
        self.content.addWidget(card)

    def _apply(self, chosen: list[recommendations.RecommendedItem]) -> None:
        service = self.state.service
        if service is None or not chosen:
            return

        def progress(message: str, fraction: float | None) -> None:
            self.state.progress.emit(message, -1.0 if fraction is None else fraction)

        async def work() -> list[str]:
            return await recommendations.apply(service, chosen, progress)

        def done(_: list[str]) -> None:
            QMessageBox.information(
                self, tr("ui.recommended_setup"), tr("ui.recommended_applied")
            )
            self.state.patches_changed.emit()

        self.state.run(self, work, tr("ui.applying"), done)

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


def _item_title(item: recommendations.RecommendedItem) -> str:
    """Patch name, or the setting with its label from the settings page when the manager knows it."""
    if item.kind == "patch" or item.setting is None:
        return item.title
    setting = item.setting
    for known in game_settings.SETTINGS:
        if (
            known.section.lower() == setting.section.lower()
            and known.key.lower() == setting.key.lower()
        ):
            value = setting.value
            if known.kind == "bool":
                value = tr("ui.on") if value not in ("0", "") else tr("ui.off")
            for choice, label in known.choices:
                if choice.lower() == setting.value.lower():
                    value = tr(label)
            return f"{tr(known.label)}: {value}"
    return item.title
