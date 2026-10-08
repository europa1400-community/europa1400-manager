"""About: version, links, licenses."""

from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextBrowser

from europa1400_manager._version import __version__
from europa1400_manager.core import paths
from europa1400_manager.gui.widgets import Card, Page, link, muted
from europa1400_manager.i18n import tr

LINKS = (
    ("ui.website", "https://europa1400-community.github.io/europa1400-manager/"),
    ("ui.source", "https://github.com/europa1400-community/europa1400-manager"),
    (
        "ui.report_problem",
        "https://github.com/europa1400-community/europa1400-manager/issues",
    ),
    ("ui.discord", "https://discord.gg/jB9HYY8DpT"),
)


class AboutPage(Page):
    def __init__(self) -> None:
        super().__init__(tr("ui.about"))
        card = Card()
        title = QLabel(f"Europa 1400 Manager {__version__}")
        title.setObjectName("CardTitle")
        card.body.addWidget(title)
        card.body.addWidget(muted(tr("ui.about_text")))
        row = QHBoxLayout()
        for key, url in LINKS:
            button = link(tr(key))
            button.clicked.connect(
                lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u))
            )
            row.addWidget(button)
        row.addStretch(1)
        card.body.addLayout(row)
        self.content.addWidget(card)

        licenses = Card()
        licenses.body.addWidget(QLabel(f"<b>{tr('ui.licenses')}</b>"))
        licenses.body.addWidget(muted(tr("ui.qt_notice")))
        text = QTextBrowser()
        text.setMinimumHeight(320)
        parts = []
        for name in ("LICENSE.md", "NOTICE.md"):
            path = paths.resource_dir() / name
            if path.exists():
                parts.append(path.read_text(encoding="utf-8", errors="replace"))
        text.setPlainText("\n\n".join(parts) or tr("ui.licenses_missing"))
        licenses.body.addWidget(text)
        self.content.addWidget(licenses)
