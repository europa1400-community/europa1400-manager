"""Savegames: list, back up, restore."""

from __future__ import annotations

import asyncio
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from europa1400_manager.core import savegames
from europa1400_manager.gui.state import AppState
from europa1400_manager.gui.widgets import Banner, Card, Page, clear, muted, primary
from europa1400_manager.i18n import tr


class SavegamesPage(Page):
    def __init__(self, state: AppState) -> None:
        super().__init__(tr("ui.savegames"), tr("ui.savegames_subtitle"))
        self.state = state
        state.game_changed.connect(self.refresh)

    def refresh(self) -> None:
        clear(self.content)
        clear(self.notices)
        game = self.state.game
        if game is None:
            self.notices.addWidget(Banner(tr("ui.no_game_selected"), "info"))
            return
        saves = savegames.list_savegames(game)
        card = Card()
        if saves:
            table = QTableWidget(len(saves), 4)
            table.setHorizontalHeaderLabels(
                [tr("ui.name"), tr("ui.kind"), tr("ui.modified"), tr("ui.size")]
            )
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for row, save in enumerate(
                sorted(saves, key=lambda s: s.modified, reverse=True)
            ):
                values = (
                    Path(save.relative).stem,
                    tr("ui.multiplayer")
                    if save.multiplayer
                    else tr("ui.single_player"),
                    f"{save.modified:%d.%m.%Y %H:%M}",
                    f"{save.size / 1024 / 1024:.1f} MB",
                )
                for column, value in enumerate(values):
                    table.setItem(row, column, QTableWidgetItem(value))
            table.setMinimumHeight(min(420, 40 + 32 * len(saves)))
            card.body.addWidget(table)
        else:
            card.body.addWidget(muted(tr("error.no_savegames")))
        buttons = QHBoxLayout()
        backup = primary(tr("ui.backup_now"))
        backup.setEnabled(bool(saves))
        backup.clicked.connect(self._backup)
        restore = QPushButton(tr("ui.restore"))
        restore.clicked.connect(self._restore)
        folder = QPushButton(tr("ui.open_save_folder"))
        folder.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(savegames.gamedata_dir(game)))
            )
        )
        backups = QPushButton(tr("ui.open_backup_folder"))
        backups.clicked.connect(self._open_backups)
        for button in (backup, restore, folder, backups):
            buttons.addWidget(button)
        buttons.addStretch(1)
        card.body.addLayout(buttons)
        self.content.addWidget(card)

        existing = savegames.list_backups()
        history = Card()
        history.body.addWidget(QLabel(f"<b>{tr('ui.backups')}</b>"))
        if not existing:
            history.body.addWidget(muted(tr("ui.no_backups")))
        for archive in existing[:10]:
            row = QHBoxLayout()
            row.addWidget(QLabel(archive.name), 1)
            button = QPushButton(tr("ui.restore_this"))
            button.clicked.connect(lambda _=False, a=archive: self._restore_archive(a))
            row.addWidget(button)
            history.body.addLayout(row)
        self.content.addWidget(history)

    def _open_backups(self) -> None:
        folder = savegames.backup_dir()
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _backup(self) -> None:
        game = self.state.game
        assert game is not None

        async def work() -> Path:
            return await asyncio.to_thread(savegames.backup, game)

        def done(path: Path) -> None:
            QMessageBox.information(
                self, tr("ui.savegames"), tr("ui.backup_done", path=path)
            )
            self.refresh()

        self.state.run(self, work, tr("ui.backing_up"), done)

    def _restore(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        folder = savegames.backup_dir()
        file, _ = QFileDialog.getOpenFileName(
            self, tr("ui.restore"), str(folder), "ZIP (*.zip)"
        )
        if file:
            self._restore_archive(Path(file))

    def _restore_archive(self, archive: Path) -> None:
        game = self.state.game
        assert game is not None
        if (
            QMessageBox.question(
                self, tr("ui.restore"), tr("ui.restore_confirm", name=archive.name)
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        async def work() -> int:
            return await asyncio.to_thread(savegames.restore, game, archive)

        def done(count: int) -> None:
            QMessageBox.information(
                self, tr("ui.savegames"), tr("ui.restored", count=count)
            )
            self.refresh()

        self.state.run(self, work, tr("ui.restoring"), done)
