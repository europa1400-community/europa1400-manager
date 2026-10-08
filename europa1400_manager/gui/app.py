"""Starting the GUI: Qt application with an asyncio event loop (qasync)."""

from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from types import TracebackType
from typing import cast

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from europa1400_manager import i18n
from europa1400_manager.core import logs, paths
from europa1400_manager.core.settings import Settings
from europa1400_manager.gui import texts, theme
from europa1400_manager.gui.main_window import MainWindow
from europa1400_manager.gui.state import AppState

log = logging.getLogger(__name__)


def _excepthook(
    kind: type[BaseException], error: BaseException, trace: TracebackType | None
) -> None:
    log.critical(
        "uncaught error:\n%s", "".join(traceback.format_exception(kind, error, trace))
    )
    if QApplication.instance():
        QMessageBox.critical(
            None, i18n.tr("ui.error"), i18n.tr("ui.unexpected_error", error=error)
        )


def main() -> int:
    import qasync

    logs.setup()
    texts.register()
    settings = Settings.load()
    i18n.set_language(settings.language)
    sys.excepthook = _excepthook

    if sys.platform == "win32":  # own taskbar icon instead of the Python one
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "europa1400-community.manager"
            )
        except (AttributeError, OSError):
            pass

    app = cast(QApplication, QApplication.instance() or QApplication(sys.argv))
    app.setApplicationName("Europa 1400 Manager")
    app.setOrganizationName("europa1400-community")
    app.setWindowIcon(QIcon(str(paths.package_resource("icon.svg"))))
    theme.apply(app)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    closed = asyncio.Event()
    app.aboutToQuit.connect(closed.set)

    state = AppState(settings)
    window = MainWindow(state)
    window.show()
    state.run(window, state.load, i18n.tr("ui.loading_database"))
    with loop:
        loop.run_until_complete(closed.wait())
    return 0
