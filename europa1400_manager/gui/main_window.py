"""Main window: navigation on the left, pages on the right, status bar with progress."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QCloseEvent, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from europa1400_manager._version import __version__
from europa1400_manager.core import paths, updates
from europa1400_manager.gui import theme
from europa1400_manager.gui.pages.about import AboutPage
from europa1400_manager.gui.pages.game_settings import GameSettingsPage
from europa1400_manager.gui.pages.home import HomePage
from europa1400_manager.gui.pages.manager_settings import ManagerSettingsPage
from europa1400_manager.gui.pages.patches import PatchesPage
from europa1400_manager.gui.pages.savegames import SavegamesPage
from europa1400_manager.gui.state import AppState
from europa1400_manager.i18n import tr


class MainWindow(QMainWindow):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Europa 1400 Manager")
        self.setWindowIcon(QIcon(str(paths.package_resource("icon.svg"))))
        self.resize(1120, 760)
        self.setMinimumSize(880, 600)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(root)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(0, 18, 0, 12)
        header = QHBoxLayout()
        header.setContentsMargins(18, 0, 18, 12)
        logo = QLabel()
        logo.setPixmap(
            QIcon(str(paths.package_resource("icon.svg"))).pixmap(QSize(36, 36))
        )
        logo.setStyleSheet("background: transparent;")
        names = QVBoxLayout()
        title = QLabel("Europa 1400")
        title.setObjectName("AppTitle")
        version = QLabel(f"Manager {__version__}")
        version.setObjectName("AppVersion")
        names.addWidget(title)
        names.addWidget(version)
        header.addWidget(logo)
        header.addLayout(names, 1)
        side.addLayout(header)
        self.navigation = QListWidget()
        self.navigation.setIconSize(QSize(20, 20))
        side.addWidget(self.navigation, 1)
        layout.addWidget(sidebar)

        self.pages = QStackedWidget()
        layout.addWidget(self.pages, 1)
        self._add(
            "home",
            tr("ui.home"),
            HomePage(state, lambda: self.navigation.setCurrentRow(1)),
        )
        self._add("patches", tr("ui.patches"), PatchesPage(state))
        self._add("settings", tr("ui.game_settings"), GameSettingsPage(state))
        self._add("saves", tr("ui.savegames"), SavegamesPage(state))
        self._add("manager", tr("ui.manager_settings"), ManagerSettingsPage(state))
        self._add("about", tr("ui.about"), AboutPage())
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        self.status_text = QLabel(tr("ui.loading_database"))
        self.progress = QProgressBar()
        self.progress.setFixedWidth(180)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        self.statusBar().addWidget(self.status_text, 1)
        self.statusBar().addPermanentWidget(self.progress)

        state.busy_changed.connect(self._busy)
        state.progress.connect(self._progress)
        state.database_loaded.connect(self._database_status)
        state.game_changed.connect(self._database_status)
        state.update_available.connect(self._update)

    def _add(self, icon: str, text: str, page: QWidget) -> None:
        item = QListWidgetItem(theme.icon(icon), text)
        item.setSizeHint(QSize(200, 42))
        self.navigation.addItem(item)
        self.pages.addWidget(page)

    def _busy(self, busy: bool, message: str) -> None:
        self.progress.setVisible(busy)
        self.progress.setRange(0, 0)
        self.navigation.setEnabled(not busy)
        if busy and message:
            self.status_text.setText(message)
        elif not busy:
            self._database_status()
        for index in range(self.pages.count()):
            page = self.pages.widget(index)
            if page is not None:
                page.setEnabled(not busy)

    def _progress(self, message: str, fraction: float) -> None:
        self.status_text.setText(message)
        if fraction < 0:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 1000)
            self.progress.setValue(int(fraction * 1000))

    def _database_status(self) -> None:
        source = self.state.database.source
        text = {
            "online": tr("ui.db_online"),
            "cache": tr("ui.db_cache"),
            "partial-cache": tr("ui.db_cache"),
            "local": tr("ui.db_local"),
            "none": tr("ui.db_none"),
        }[source]
        game = self.state.game
        self.status_text.setText(
            f"{text}   ·   {game.path if game else tr('ui.no_game_selected')}"
        )

    def _update(self, update: updates.Update) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(tr("ui.update_title"))
        box.setText(tr("ui.update_text", version=update.version, current=__version__))
        download = box.addButton(
            tr("ui.update_download"), QMessageBox.ButtonRole.AcceptRole
        )
        skip = box.addButton(tr("ui.update_skip"), QMessageBox.ButtonRole.RejectRole)
        box.addButton(tr("ui.later"), QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() is download:
            QDesktopServices.openUrl(QUrl(update.url))
        elif box.clickedButton() is skip:
            self.state.settings.skipped_manager_version = update.version
            self.state.settings.save()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt API
        if (
            self.state.busy
            and QMessageBox.question(self, tr("ui.quit"), tr("ui.quit_busy"))
            != QMessageBox.StandardButton.Yes
        ):
            event.ignore()
            return
        event.accept()


__all__ = ["MainWindow", "Qt"]
