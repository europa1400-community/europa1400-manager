import tkinter as tk
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.license_module import LicenseModule


class LicenseModuleGui(BaseModuleGui, LicenseModule):
    FRIENDLY_NAME = "Licenses"

    def __init__(
        self,
        config: Config,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
    ) -> None:
        super().__init__(config, event_emitter, root, notebook)

        top_frame = tk.Frame(self.tab)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        self.show_all_var = tk.BooleanVar(value=False)
        self.show_all_var.trace_add("write", lambda *args: self._update_gui())

        show_all_checkbox = tk.Checkbutton(
            top_frame, text="Show all licenses", variable=self.show_all_var
        )
        show_all_checkbox.pack(side=tk.LEFT, anchor=tk.W)

        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(self.text_widget.get("1.0", tk.END))

        copy_button = tk.Button(
            top_frame, text="Copy to Clipboard", command=copy_to_clipboard
        )
        copy_button.pack(side=tk.RIGHT, anchor=tk.E, padx=(5, 0))

        text_frame = tk.Frame(self.tab)
        text_frame.pack(expand=True, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set
        )
        self.text_widget.pack(expand=True, fill=tk.BOTH)

        scrollbar.config(command=self.text_widget.yview)

    def _update_gui(self) -> None:
        licenses = (
            self._get_all_licenses() if self.show_all_var.get() else self._get_license()
        )
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, licenses)
        self.text_widget.config(state=tk.DISABLED)
