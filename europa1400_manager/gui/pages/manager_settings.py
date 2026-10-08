"""Manager settings: game folder, language, updates, database source, logs."""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

from europa1400_manager.core import paths
from europa1400_manager.gui.state import AppState
from europa1400_manager.gui.widgets import Page, clear, muted, primary
from europa1400_manager.i18n import LANGUAGES, tr


class ManagerSettingsPage(Page):
    def __init__(self, state: AppState) -> None:
        super().__init__(tr("ui.manager_settings"))
        self.state = state
        state.game_changed.connect(self.refresh)
        state.database_loaded.connect(self.refresh)

    def refresh(self) -> None:
        clear(self.content)
        settings = self.state.settings

        games = QGroupBox(tr("ui.game_folder"))
        form = QFormLayout(games)
        self.games = QComboBox()
        self.games.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.games.setMinimumContentsLength(24)
        for path in self.state.installations:
            self.games.addItem(str(path), str(path))
        if self.state.game:
            self.games.setCurrentIndex(
                max(0, self.games.findData(str(self.state.game.path)))
            )
        use = primary(tr("ui.use"))
        use.clicked.connect(
            lambda: self._open(Path(self.games.currentData()))
            if self.games.currentData()
            else None
        )
        browse = QPushButton(tr("ui.browse"))
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.games, 1)
        row.addWidget(use)
        row.addWidget(browse)
        form.addRow(row)
        form.addRow(muted(tr("ui.game_folder_hint")))
        self.content.addWidget(games)

        general = QGroupBox(tr("ui.general"))
        form = QFormLayout(general)
        language = QComboBox()
        language.addItem(tr("ui.system_language"), None)
        for code, name in LANGUAGES.items():
            language.addItem(name, code)
        language.setCurrentIndex(max(0, language.findData(settings.language)))
        language.currentIndexChanged.connect(
            lambda: self._set_language(language.currentData())
        )
        form.addRow(tr("ui.language"), language)
        updates = QCheckBox(tr("ui.check_updates"))
        updates.setChecked(settings.check_updates)
        updates.toggled.connect(lambda value: self._save(check_updates=value))
        form.addRow("", updates)
        self.content.addWidget(general)

        database = QGroupBox(tr("ui.database"))
        form = QFormLayout(database)
        source = {
            "online": tr("ui.db_online"),
            "cache": tr("ui.db_cache"),
            "partial-cache": tr("ui.db_cache"),
            "local": tr("ui.db_local"),
            "none": tr("ui.db_none"),
        }[self.state.database.source]
        form.addRow(tr("ui.db_state"), QLabel(source))
        branch = QLineEdit(settings.database_branch)
        branch.setToolTip(tr("ui.db_branch_hint"))
        reload_button = QPushButton(tr("ui.reload"))
        reload_button.clicked.connect(
            lambda: self._reload(branch.text().strip() or "master")
        )
        row = QHBoxLayout()
        row.addWidget(branch, 1)
        row.addWidget(reload_button)
        form.addRow(tr("ui.db_branch"), row)
        self.content.addWidget(database)

        files = QGroupBox(tr("ui.files"))
        form = QFormLayout(files)
        for label, folder in (
            (tr("ui.log_folder"), paths.log_dir()),
            (tr("ui.settings_folder"), paths.config_dir()),
        ):
            button = QPushButton(tr("ui.open"))
            button.clicked.connect(lambda _=False, f=folder: self._open_folder(f))
            form.addRow(label, _left(button))
        clear_cache = QPushButton(tr("ui.clear_cache"))
        clear_cache.clicked.connect(self._clear_cache)
        form.addRow(tr("ui.cache"), _left(clear_cache))
        self.content.addWidget(files)

    def _open(self, path: Path) -> None:
        self.state.run(self, lambda: self.state.open_game(path), tr("ui.identifying"))

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("ui.choose_game"))
        if folder:
            self._open(Path(folder))

    def _save(self, **values: object) -> None:
        for key, value in values.items():
            setattr(self.state.settings, key, value)
        self.state.settings.save()

    def _set_language(self, code: str | None) -> None:
        self._save(language=code)
        QMessageBox.information(self, tr("ui.language"), tr("ui.restart_for_language"))

    def _reload(self, branch: str) -> None:
        self._save(database_branch=branch)
        self.state.run(self, self.state.reload_database, tr("ui.loading_database"))

    @staticmethod
    def _open_folder(folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _clear_cache(self) -> None:
        shutil.rmtree(paths.cache_dir() / "downloads", ignore_errors=True)
        QMessageBox.information(self, tr("ui.cache"), tr("ui.cache_cleared"))


def _left(widget: QWidget) -> QWidget:
    """A widget at its natural width, aligned left inside a form row."""
    holder = QWidget()
    row = QHBoxLayout(holder)
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(widget)
    row.addStretch(1)
    return holder
