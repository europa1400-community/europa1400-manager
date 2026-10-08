"""Small building blocks of the pages."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from europa1400_manager.gui import theme


def clear(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        widget, inner = item.widget(), item.layout()
        if widget is not None:
            widget.deleteLater()
        elif inner is not None:
            clear(inner)


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None, spacing: int = 8) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 16, 18, 16)
        self.body.setSpacing(spacing)


class Chip(QLabel):
    COLORS = {
        "success": theme.SUCCESS,
        "warning": theme.WARNING,
        "danger": theme.DANGER,
        "info": theme.INFO,
        "muted": theme.MUTED,
        "accent": theme.ACCENT,
    }

    def __init__(self, text: str, kind: str = "muted", tooltip: str = "") -> None:
        super().__init__(text)
        color = self.COLORS.get(kind, theme.MUTED)
        self.setObjectName("Chip")
        self.setStyleSheet(
            f"#Chip {{ color: {color}; border: 1px solid {color}; background: transparent; }}"
        )
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        if tooltip:
            self.setToolTip(tooltip)


class Banner(QFrame):
    """A coloured notice with an optional action button."""

    def __init__(
        self,
        text: str,
        kind: str = "info",
        action: str = "",
        on_action: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        color = Chip.COLORS.get(kind, theme.INFO)
        self.setObjectName("Banner")
        self.setStyleSheet(
            f"#Banner {{ background: {theme.SURFACE}; border: 1px solid {color}; }}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 10, 10)
        bar = QLabel()
        bar.setFixedWidth(4)
        bar.setStyleSheet(f"background: {color}; border-radius: 2px;")
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)
        layout.addWidget(bar)
        layout.addWidget(label, 1)
        if action and on_action:
            button = QPushButton(action)
            button.clicked.connect(on_action)
            layout.addWidget(button)


def primary(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Primary")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def danger(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Danger")
    return button


def link(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("Link")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def muted(text: str, wrap: bool = True) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Muted")
    label.setWordWrap(wrap)
    return label


class Page(QWidget):
    """A scrollable page with title and subtitle; content goes into self.content."""

    def __init__(self, title: str, subtitle: str = "") -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        holder = QWidget()
        scroll.setWidget(holder)
        self.layout_ = QVBoxLayout(holder)
        self.layout_.setContentsMargins(32, 28, 32, 28)
        self.layout_.setSpacing(16)
        self.title = QLabel(title)
        self.title.setObjectName("PageTitle")
        self.subtitle = muted(subtitle)
        self.layout_.addWidget(self.title)
        if subtitle:
            self.layout_.addWidget(self.subtitle)
        self.notices = QVBoxLayout()
        self.notices.setSpacing(8)
        self.layout_.addLayout(self.notices)
        self.content = QVBoxLayout()
        self.content.setSpacing(14)
        self.layout_.addLayout(self.content)
        self.layout_.addStretch(1)
