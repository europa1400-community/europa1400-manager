"""Look of the window: a dark theme with the guild's gold as accent, and the navigation icons (inline SVG)."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

ACCENT = "#e0a83e"
ACCENT_HOVER = "#f0bd57"
BACKGROUND = "#171925"
SURFACE = "#202334"
SURFACE_HIGH = "#2a2e43"
BORDER = "#363b55"
TEXT = "#e8e9f1"
MUTED = "#9a9fba"
SUCCESS = "#5cc28a"
WARNING = "#e8b04a"
DANGER = "#e46a6a"
INFO = "#6aa8e4"

STYLE = f"""
* {{ font-family: "Segoe UI", "Noto Sans", "DejaVu Sans", sans-serif; font-size: 10pt; }}
QWidget {{ background: {BACKGROUND}; color: {TEXT}; }}
QToolTip {{ background: {SURFACE_HIGH}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}
#Sidebar {{ background: {SURFACE}; border-right: 1px solid {BORDER}; }}
#Sidebar QListWidget {{ background: transparent; border: none; outline: 0; }}
#Sidebar QListWidget::item {{ padding: 10px 14px; margin: 2px 8px; border-radius: 8px; color: {MUTED}; }}
#Sidebar QListWidget::item:hover {{ background: {SURFACE_HIGH}; color: {TEXT}; }}
#Sidebar QListWidget::item:selected {{ background: {SURFACE_HIGH}; color: {ACCENT}; }}
#AppTitle {{ font-size: 13pt; font-weight: 600; background: transparent; }}
#AppVersion {{ color: {MUTED}; background: transparent; }}
#PageTitle {{ font-size: 18pt; font-weight: 600; }}
#PageSubtitle {{ color: {MUTED}; }}
#Card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px; }}
#Card QLabel, #Card QCheckBox {{ background: transparent; }}
#CardTitle {{ font-size: 12pt; font-weight: 600; }}
#Muted {{ color: {MUTED}; }}
#GameTitle {{ font-size: 22pt; font-weight: 700; color: {ACCENT}; background: transparent; }}
QPushButton {{ background: {SURFACE_HIGH}; border: 1px solid {BORDER}; border-radius: 8px; padding: 7px 16px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:disabled {{ color: {MUTED}; border-color: {SURFACE_HIGH}; }}
QPushButton#Primary {{ background: {ACCENT}; color: #1b1406; border: none; font-weight: 600; }}
QPushButton#Primary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#Primary:disabled {{ background: {SURFACE_HIGH}; color: {MUTED}; }}
QPushButton#Danger {{ color: {DANGER}; }}
QPushButton#Danger:hover {{ border-color: {DANGER}; }}
QPushButton#Link {{ background: transparent; border: none; color: {ACCENT}; padding: 2px 4px; }}
QPushButton#Link:hover {{ text-decoration: underline; }}
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextBrowser, QTableWidget {{
    background: {SURFACE_HIGH}; border: 1px solid {BORDER}; border-radius: 6px; padding: 5px 8px;
    selection-background-color: {ACCENT}; selection-color: #1b1406; }}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox QAbstractItemView {{ background: {SURFACE_HIGH}; border: 1px solid {BORDER}; }}
QHeaderView::section {{ background: {SURFACE}; color: {MUTED}; border: none; padding: 6px; }}
QTableWidget {{ gridline-color: {BORDER}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {MUTED}; border-radius: 4px; background: {SURFACE_HIGH}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QCheckBox::indicator:hover {{ border-color: {ACCENT}; }}
QGroupBox::indicator {{ width: 14px; height: 14px; border: 1px solid {MUTED}; border-radius: 3px; background: {SURFACE_HIGH}; }}
QGroupBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {ACCENT}; width: 14px; margin: -6px 0; border-radius: 7px; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QProgressBar {{ background: {SURFACE_HIGH}; border: none; border-radius: 4px; height: 8px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QStatusBar {{ background: {SURFACE}; color: {MUTED}; border-top: 1px solid {BORDER}; }}
QStatusBar QLabel {{ background: transparent; color: {MUTED}; }}
#Banner {{ border-radius: 10px; padding: 2px; }}
#Banner QLabel {{ background: transparent; }}
#Chip {{ border-radius: 10px; padding: 2px 10px; font-size: 9pt; }}
QGroupBox {{ border: 1px solid {BORDER}; border-radius: 10px; margin-top: 14px; padding: 12px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; color: {ACCENT}; }}
"""

# 24x24 line icons (own drawings), stroke = currentColor replaced at render time
ICONS = {
    "home": '<path d="M3 11 12 4l9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "patches": '<path d="M9 3h6v4a2 2 0 1 0 4 0h2v6h-3a2 2 0 1 0 0 4h3v4H3V3h6"/>',
    "settings": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/>'
    '<circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "saves": '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7V3M8 21v-7h8v7"/>',
    "manager": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1'
    'M4.9 19.1 7 17M17 7l2.1-2.1"/>',
    "about": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "play": '<path d="M7 4v16l13-8z"/>',
    "folder": '<path d="M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>',
}


def icon(name: str, color: str = MUTED, size: int = 24) -> QIcon:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(QSize(size * 2, size * 2))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    result = QIcon()
    result.addPixmap(pixmap, QIcon.Mode.Normal)
    selected = QPixmap(pixmap.size())
    selected.fill(Qt.GlobalColor.transparent)
    painter = QPainter(selected)
    QSvgRenderer(QByteArray(svg.replace(color, ACCENT).encode())).render(painter)
    painter.end()
    result.addPixmap(selected, QIcon.Mode.Selected)
    return result


def apply(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans"])
    font.setPointSize(10)
    app.setFont(font)
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, BACKGROUND),
        (QPalette.ColorRole.Base, SURFACE_HIGH),
        (QPalette.ColorRole.AlternateBase, SURFACE),
        (QPalette.ColorRole.Text, TEXT),
        (QPalette.ColorRole.WindowText, TEXT),
        (QPalette.ColorRole.Button, SURFACE_HIGH),
        (QPalette.ColorRole.ButtonText, TEXT),
        (QPalette.ColorRole.Highlight, ACCENT),
        (QPalette.ColorRole.HighlightedText, "#1b1406"),
        (QPalette.ColorRole.Link, ACCENT),
        (QPalette.ColorRole.PlaceholderText, MUTED),
        (QPalette.ColorRole.ToolTipBase, SURFACE_HIGH),
        (QPalette.ColorRole.ToolTipText, TEXT),
    ):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    app.setStyleSheet(STYLE)
