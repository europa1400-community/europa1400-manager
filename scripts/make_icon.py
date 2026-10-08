"""Render europa1400_manager/resources/icon.svg to build/icon.ico (Windows executable icon)."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    QGuiApplication(sys.argv[:1] + ["-platform", "offscreen"])
    renderer = QSvgRenderer(
        QByteArray((ROOT / "europa1400_manager/resources/icon.svg").read_bytes())
    )
    image = QImage(256, 256, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    target = ROOT / "build" / "icon.ico"
    target.parent.mkdir(exist_ok=True)
    if not image.save(str(target), "ICO"):
        print("could not write", target, file=sys.stderr)
        return 1
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
