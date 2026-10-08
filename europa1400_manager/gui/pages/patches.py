"""Patches: what is available for this game, installing, updating and removing."""

from __future__ import annotations

import asyncio

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
)

from europa1400_manager import i18n
from europa1400_manager.core import recommendations
from europa1400_manager.core.models import PatchCategory
from europa1400_manager.core.patches import PatchService, PatchState, PatchStatus
from europa1400_manager.gui.state import AppState
from europa1400_manager.gui.widgets import (
    Banner,
    Card,
    Chip,
    Page,
    clear,
    danger,
    link,
    muted,
    primary,
)
from europa1400_manager.i18n import tr

CATEGORY_ORDER = [c.value for c in PatchCategory]


class PatchesPage(Page):
    def __init__(self, state: AppState) -> None:
        super().__init__(tr("ui.patches"), tr("ui.patches_subtitle"))
        self.state = state
        self.recommended: set[str] = set()
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("ui.search"))
        self.search.textChanged.connect(self.refresh)
        self.category = QComboBox()
        self.category.addItem(tr("ui.all_categories"), "")
        for category in CATEGORY_ORDER:
            self.category.addItem(tr(f"category.{category}"), category)
        self.category.currentIndexChanged.connect(self.refresh)
        self.only_compatible = QCheckBox(tr("ui.only_compatible"))
        self.only_compatible.setChecked(True)
        self.only_compatible.toggled.connect(self.refresh)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.category, 1)
        filters.addWidget(self.only_compatible)
        self.layout_.insertLayout(2, filters)
        for signal in (
            state.game_changed,
            state.patches_changed,
            state.database_loaded,
        ):
            signal.connect(self.refresh)

    def refresh(self) -> None:
        clear(self.content)
        clear(self.notices)
        service = self.state.service
        if service is None:
            self.notices.addWidget(Banner(tr("ui.no_game_selected"), "info"))
            return
        if not self.state.database.patches:
            self.notices.addWidget(Banner(tr("ui.no_database"), "danger"))
            return
        text = self.search.text().strip().lower()
        category = self.category.currentData()
        statuses = service.statuses()
        self.recommended = {
            i.key
            for i in recommendations.items(service, i18n.language())
            if i.kind == "patch" and i.recommended
        }
        shown = 0
        for status in sorted(
            statuses,
            key=lambda s: (_category_index(s), not s.installed, s.patch.name.lower()),
        ):
            patch = status.patch
            if (
                text
                and text
                not in f"{patch.name} {patch.id} {patch.text(i18n.language())}".lower()
            ):
                continue
            if category and (patch.category or "other") != category:
                continue
            if (
                self.only_compatible.isChecked()
                and status.compatible is False
                and not status.installed
            ):
                continue
            self.content.addWidget(self._card(service, status))
            shown += 1
        if not shown:
            self.content.addWidget(muted(tr("ui.no_patches_match")))

    def _card(self, service: PatchService, status: PatchStatus) -> Card:
        patch = status.patch
        card = Card()
        header = QHBoxLayout()
        name = QLabel(patch.name)
        name.setObjectName("CardTitle")
        header.addWidget(name)
        if patch.version:
            header.addWidget(Chip(patch.version, "muted"))
        state_chip = {
            PatchState.INSTALLED: Chip(tr("ui.installed"), "success"),
            PatchState.UPDATE: Chip(
                tr("ui.update_available", version=status.installed_version), "info"
            ),
            PatchState.UNMANAGED: Chip(
                tr("ui.unmanaged"), "warning", tr("ui.unmanaged_hint")
            ),
        }.get(status.state)
        if state_chip:
            header.addWidget(state_chip)
        if status.compatible is False:
            header.addWidget(
                Chip(
                    tr("ui.not_for_this_game"),
                    "danger",
                    tr("ui.not_for_this_game_hint"),
                )
            )
        elif status.compatible is True:
            header.addWidget(Chip(tr("ui.fits"), "success", tr("ui.fits_hint")))
        if patch.id in self.recommended:
            header.addWidget(
                Chip(
                    tr("ui.level_recommended"), "accent", tr("ui.recommended_chip_hint")
                )
            )
        header.addWidget(Chip(tr(f"category.{patch.category or 'other'}"), "muted"))
        header.addStretch(1)
        card.body.addLayout(header)

        description = patch.text(i18n.language())
        if description:
            card.body.addWidget(muted(description))
        details = []
        if patch.requires:
            details.append(
                tr(
                    "ui.requires",
                    names=", ".join(_name(service, r) for r in patch.requires),
                )
            )
        if patch.conflicts:
            details.append(
                tr(
                    "ui.conflicts_with",
                    names=", ".join(_name(service, c) for c in patch.conflicts),
                )
            )
        if status.required_by:
            details.append(
                tr(
                    "ui.needed_by",
                    names=", ".join(_name(service, r) for r in status.required_by),
                )
            )
        if patch.author:
            details.append(tr("ui.author", name=patch.author))
        if details:
            card.body.addWidget(muted("  ·  ".join(details)))

        buttons = QHBoxLayout()
        if status.state == PatchState.AVAILABLE:
            install = primary(tr("ui.install"))
            install.clicked.connect(lambda: self._install(service, status))
            buttons.addWidget(install)
        elif status.state == PatchState.UPDATE:
            update = primary(tr("ui.update"))
            update.clicked.connect(lambda: self._install(service, status))
            buttons.addWidget(update)
        elif status.state == PatchState.UNMANAGED:
            adopt = primary(tr("ui.reinstall"))
            adopt.setToolTip(tr("ui.reinstall_hint"))
            adopt.clicked.connect(lambda: self._install(service, status))
            buttons.addWidget(adopt)
        if status.installed and (
            status.state != PatchState.UNMANAGED
            or service.handler(patch).can_remove_unmanaged()
        ):
            remove = danger(tr("ui.uninstall"))
            remove.clicked.connect(lambda: self._uninstall(service, status))
            buttons.addWidget(remove)
        if patch.homepage:
            homepage = patch.homepage
            more = link(tr("ui.homepage"))
            more.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(homepage)))
            buttons.addWidget(more)
        buttons.addStretch(1)
        card.body.addLayout(buttons)
        return card

    def _install(self, service: PatchService, status: PatchStatus) -> None:
        patch = status.patch
        try:
            order = service.install_order(patch.id)
        except Exception as error:  # noqa: BLE001
            QMessageBox.warning(self, tr("ui.error"), str(error))
            return
        extra = [p.name for p in order if p.id != patch.id]
        if (
            status.compatible is False
            and QMessageBox.question(
                self, tr("ui.install"), tr("ui.install_incompatible", name=patch.name)
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        if (
            extra
            and QMessageBox.question(
                self,
                tr("ui.install"),
                tr("ui.install_with", name=patch.name, others=", ".join(extra)),
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        def progress(message: str, fraction: float | None) -> None:
            self.state.progress.emit(message, -1.0 if fraction is None else fraction)

        async def work() -> list[str]:
            return await service.install(patch.id, progress)

        self.state.run(
            self,
            work,
            tr("progress.installing", patch=patch.name),
            done=lambda _: self.state.patches_changed.emit(),
        )

    def _uninstall(self, service: PatchService, status: PatchStatus) -> None:
        patch = status.patch
        with_dependents = False
        if status.required_by:
            names = ", ".join(_name(service, r) for r in status.required_by)
            if (
                QMessageBox.question(
                    self,
                    tr("ui.uninstall"),
                    tr("ui.uninstall_dependents", name=patch.name, others=names),
                )
                != QMessageBox.StandardButton.Yes
            ):
                return
            with_dependents = True
        elif (
            QMessageBox.question(
                self, tr("ui.uninstall"), tr("ui.uninstall_confirm", name=patch.name)
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        async def work() -> list[str]:
            return await asyncio.to_thread(service.uninstall, patch.id, with_dependents)

        def done(warnings: list[str]) -> None:
            if warnings:
                QMessageBox.information(self, tr("ui.uninstall"), "\n".join(warnings))
            self.state.patches_changed.emit()

        self.state.run(self, work, tr("ui.uninstalling", patch=patch.name), done)


def _name(service: PatchService, patch_id: str) -> str:
    patch = service.database.patch(patch_id)
    return patch.name if patch else patch_id


def _category_index(status: PatchStatus) -> int:
    category = status.patch.category or "other"
    return (
        CATEGORY_ORDER.index(category)
        if category in CATEGORY_ORDER
        else len(CATEGORY_ORDER)
    )
