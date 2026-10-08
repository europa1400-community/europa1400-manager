"""Errors with a message meant for the player (shown as is by the CLI and the GUI)."""

from __future__ import annotations


class ManagerError(Exception):
    """An expected problem with a message for the player; anything else is a bug and is logged with its traceback."""


class GameNotFoundError(ManagerError):
    pass


class GameRunningError(ManagerError):
    pass


class PermissionProblemError(ManagerError):
    pass


class DownloadError(ManagerError):
    pass


class PatchError(ManagerError):
    pass
