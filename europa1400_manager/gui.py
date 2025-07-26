import tkinter as tk
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.const import EVENT_UPDATE_ALL_MODULES
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.config_module_gui import ConfigModuleGui
from europa1400_manager.modules.info_module_gui import InfoModuleGui
from europa1400_manager.modules.license_module_gui import LicenseModuleGui


class Gui:
    def __init__(self, config: Config) -> None:
        self.root = tk.Tk()
        self.root.title("Europa 1400 Manager")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.event_emitter = EventEmitter()

        info_module = InfoModuleGui(
            config, self.event_emitter, self.root, self.notebook
        )
        config_module = ConfigModuleGui(
            config, self.event_emitter, self.root, self.notebook
        )
        license_module = LicenseModuleGui(
            config, self.event_emitter, self.root, self.notebook
        )
        self.modules: list[BaseModuleGui] = [info_module, config_module, license_module]

        self.event_emitter.on(EVENT_UPDATE_ALL_MODULES, self._update_all_modules)

    def _update_all_modules(self) -> None:
        """Update all modules when the event is triggered."""
        for module in self.modules:
            module.update_gui()

    def run(self) -> None:
        for module in self.modules:
            module._update_gui()

        self.root.mainloop()
