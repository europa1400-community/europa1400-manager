"""Game settings: the known game.ini values with proper controls, and all values in a table."""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from europa1400_manager.core import game_settings, ini
from europa1400_manager.core.errors import ManagerError
from europa1400_manager.core.game_settings import GameSetting
from europa1400_manager.gui.state import AppState
from europa1400_manager.gui.widgets import Banner, Card, Page, clear, muted, primary
from europa1400_manager.i18n import tr

BACKUP_NAME = "game.ini.manager-backup"


class GameSettingsPage(Page):
    def __init__(self, state: AppState) -> None:
        super().__init__(tr("ui.game_settings"), tr("ui.game_settings_subtitle"))
        self.state = state
        self.controls: dict[tuple[str, str], tuple[GameSetting, QWidget]] = {}
        self.loaded: dict[tuple[str, str], str | None] = {}
        self.table: QTableWidget | None = None
        self.raw_loaded: dict[tuple[str, str], str] = {}
        state.game_changed.connect(self.refresh)
        state.patches_changed.connect(self.refresh)

    def refresh(self) -> None:
        clear(self.content)
        clear(self.notices)
        self.controls.clear()
        game = self.state.game
        if game is None:
            self.notices.addWidget(Banner(tr("ui.no_game_selected"), "info"))
            return
        if not game.game_ini.exists():
            self.notices.addWidget(Banner(tr("ui.no_game_ini"), "warning"))
            return
        self.loaded = game_settings.read(game.game_ini)
        groups: dict[str, QFormLayout] = {}
        for setting in game_settings.SETTINGS:
            if setting.group not in groups:
                box = QGroupBox(tr(setting.group))
                form = QFormLayout(box)
                form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
                form.setHorizontalSpacing(24)
                groups[setting.group] = form
                self.content.addWidget(box)
            value = self.loaded[(setting.section, setting.key)]
            control = self._control(setting, value)
            groups[setting.group].addRow(tr(setting.label), control)
            self.controls[(setting.section, setting.key)] = (setting, control)

        self._raw_table(game.game_ini)

        buttons = QHBoxLayout()
        save = primary(tr("ui.save"))
        save.clicked.connect(self._save)
        reset = QPushButton(tr("ui.discard"))
        reset.clicked.connect(self.refresh)
        open_file = QPushButton(tr("ui.open_game_ini"))
        open_file.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(game.game_ini)))
        )
        buttons.addWidget(save)
        buttons.addWidget(reset)
        buttons.addStretch(1)
        buttons.addWidget(open_file)
        self.content.addLayout(buttons)
        if (game.path / BACKUP_NAME).exists():
            self.content.addWidget(muted(tr("ui.game_ini_backup", name=BACKUP_NAME)))

    def _control(self, setting: GameSetting, value: str | None) -> QWidget:
        if setting.kind == "bool":
            box = QCheckBox()
            box.setChecked(value not in (None, "", "0"))
            return box
        if setting.kind == "choice":
            combo = QComboBox()
            for choice, label in setting.choices:
                combo.addItem(tr(label), choice)
            if value and combo.findData(value.upper()) < 0:
                combo.addItem(value, value)
            combo.setCurrentIndex(max(0, combo.findData((value or "").upper())))
            return combo
        if setting.kind == "int":
            holder = QWidget()
            row = QHBoxLayout(holder)
            row.setContentsMargins(0, 0, 0, 0)
            spin = QSpinBox()
            spin.setRange(setting.minimum, setting.maximum)
            spin.setValue(_int(value, setting.minimum))
            if setting.maximum - setting.minimum <= 255:
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(setting.minimum, setting.maximum)
                slider.setValue(spin.value())
                slider.valueChanged.connect(spin.setValue)
                spin.valueChanged.connect(slider.setValue)
                row.addWidget(slider, 1)
            row.addWidget(spin)
            holder.setProperty("spin", spin)
            return holder
        line = QLineEdit(value or "")
        return line

    def _value(self, setting: GameSetting, control: QWidget) -> str:
        if isinstance(control, QCheckBox):
            return "1" if control.isChecked() else "0"
        if isinstance(control, QComboBox):
            return str(control.currentData())
        if isinstance(control, QLineEdit):
            return control.text().strip()
        spin = control.property("spin")
        return str(spin.value())

    def _raw_table(self, path: Path) -> None:
        values = ini.read_all(path)
        rows = [
            (section, key, value)
            for section, entries in values.items()
            for key, value in entries.items()
        ]
        self.raw_loaded = {(s, k): v for s, k, v in rows}
        card = Card()
        card.body.addWidget(muted(tr("ui.all_values_hint")))
        table = QTableWidget(len(rows), 3)
        table.setHorizontalHeaderLabels(
            [tr("ui.section"), tr("ui.key"), tr("ui.value")]
        )
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for index, (section, key, value) in enumerate(rows):
            for column, text in enumerate((section, key, value)):
                item = QTableWidgetItem(text)
                if column < 2:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(index, column, item)
        table.setMinimumHeight(260)
        box = QGroupBox(tr("ui.all_values"))
        box.setCheckable(True)
        box.setChecked(False)
        table.setVisible(False)
        box.toggled.connect(table.setVisible)
        inner = QFormLayout(box)
        inner.addRow(table)
        card.body.addWidget(box)
        self.table = table
        self.content.addWidget(card)

    def _save(self) -> None:
        game = self.state.game
        if game is None:
            return
        changes: dict[tuple[str, str], str | None] = {}
        for key, (setting, control) in self.controls.items():
            value = self._value(setting, control)
            if value != (
                self.loaded.get(key) or ("0" if setting.kind == "bool" else "")
            ):
                changes[key] = value
        if self.table is not None:
            for row in range(self.table.rowCount()):
                items = [self.table.item(row, column) for column in range(3)]
                if any(item is None for item in items):
                    continue
                section, key, value = (
                    item.text() for item in items if item is not None
                )
                if self.raw_loaded.get((section, key)) != value and (
                    section,
                    key,
                ) not in {(s.lower(), k.lower()) for s, k in changes}:
                    changes[(section, key)] = value
        if not changes:
            QMessageBox.information(self, tr("ui.save"), tr("ui.nothing_changed"))
            return
        try:
            game.ensure_not_running()
            backup = game.path / BACKUP_NAME
            if not backup.exists():
                shutil.copy2(game.game_ini, backup)
            ini.set_values(game.game_ini, changes)
        except (ManagerError, OSError) as error:
            QMessageBox.warning(self, tr("ui.error"), str(error))
            return
        QMessageBox.information(self, tr("ui.save"), tr("ui.saved", count=len(changes)))
        self.refresh()


def _int(value: str | None, fallback: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return fallback
