"""Logging to <user log folder>/manager.log (rotated); the GUI shows the same lines."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from europa1400_manager.core import paths

FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


def setup(verbose: bool = False) -> Path:
    folder = paths.log_dir()
    folder.mkdir(parents=True, exist_ok=True)
    file = folder / "manager.log"
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        handler = RotatingFileHandler(
            file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(FORMAT))
        root.addHandler(handler)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    return file
