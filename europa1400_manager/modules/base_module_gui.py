import asyncio
import tkinter as tk
from abc import ABC
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.modules.base_module import BaseModule


class BaseModuleGui(BaseModule, ABC):
    """Base class for GUI modules."""

    def __init__(
        self,
        config: Config,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
    ) -> None:
        super().__init__(config)

        self.event_emitter = event_emitter
        self.root = root
        self.notebook = notebook

        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text=self.FRIENDLY_NAME)

    def update_gui(self) -> None:
        """Update the GUI elements for this module."""
        self._update_gui()

        loop = asyncio.get_event_loop()
        loop.create_task(self._async_update_gui())

    async def _async_update_gui(self) -> None:
        """Asynchronous update of the GUI elements for this module."""

    def _update_gui(self) -> None:
        """Synchronous update of the GUI elements for this module."""
