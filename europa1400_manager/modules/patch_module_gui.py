import asyncio
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.const import EVENT_UPDATE_ALL_MODULES, PatchType
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.patch_module import PatchModule


class PatchModuleGui(BaseModuleGui, PatchModule):
    FRIENDLY_NAME = "Patches"

    def __init__(
        self,
        config: Config,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
    ) -> None:
        super().__init__(config, event_emitter, root, notebook)

        main_frame = ttk.LabelFrame(self.tab, text="Patches", padding="10")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.status_vars: dict[PatchType, tk.BooleanVar] = {}
        self.action_buttons: dict[PatchType, ttk.Button] = {}

        self._executor = ThreadPoolExecutor(max_workers=1)
        for patch_type, patch in self.patches.items():
            row = ttk.Frame(main_frame)
            row.pack(fill="x", pady=2, padx=5)

            var = tk.BooleanVar(value=patch.is_installed)
            check = ttk.Checkbutton(row, variable=var, state="disabled")
            check.pack(side="left", padx=(0, 5))
            self.status_vars[patch_type] = var

            name_label = ttk.Label(row, text=patch.FRIENDLY_NAME, width=20, anchor="w")
            name_label.pack(side="left")

            action_button = ttk.Button(
                row,
                text="",
                command=lambda pt=patch_type: self._on_action_clicked(pt),
            )
            action_button.pack(side="right")
            self.action_buttons[patch_type] = action_button

    def _on_action_clicked(self, patch_type: PatchType) -> None:
        patch = self.patches[patch_type]

        def task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if patch.is_installed:
                loop.run_until_complete(patch.uninstall())
            else:
                loop.run_until_complete(patch.install())
            loop.close()

        future = self._executor.submit(task)
        future.add_done_callback(
            lambda _: self.root.after(
                0, lambda: self.event_emitter.emit(EVENT_UPDATE_ALL_MODULES)
            )
        )

    def _update_gui(self) -> None:
        for patch_type, patch in self.patches.items():
            installed = patch.is_installed
            var = self.status_vars[patch_type]
            button = self.action_buttons[patch_type]

            var.set(installed)
            button.config(text="Uninstall" if installed else "Install")
