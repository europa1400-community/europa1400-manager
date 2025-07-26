import inspect
import tkinter as tk
from abc import ABC
from tkinter import ttk

from europa1400_manager.async_typer import AsyncTyper
from europa1400_manager.const import AppMode


class BaseModule(ABC):
    NAME: str
    FRIENDLY_NAME: str
    app_mode: AppMode
    typer_app: AsyncTyper

    def __init__(self, app_mode: AppMode) -> None:
        self.app_mode = app_mode
        self.typer_app = AsyncTyper(no_args_is_help=True)
        self.typer_app.info.name = self.NAME
        self.typer_app.info.help = f"{self.FRIENDLY_NAME} module"

        self._register_commands()

    def _register_commands(self) -> None:
        for attr_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if attr_name in BaseModule.__dict__:
                continue
            if attr_name.startswith("_"):
                continue

            command = self.typer_app.command(
                name=attr_name.replace("_", "-"), help=method.__doc__ or ""
            )
            command(method)

    def initialize_gui(self, root: tk.Tk, notebook: ttk.Notebook) -> None:
        """Initialize the GUI elements for this module."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=self.FRIENDLY_NAME)
        self._initialize_gui(root, tab)

    def _initialize_gui(self, root: tk.Tk, tab: ttk.Frame):
        pass
