import tkinter as tk
from tkinter import ttk

from europa1400_manager.modules.base_module import BaseModule


class Gui:
    def __init__(self, modules: list[BaseModule]) -> None:
        self.modules = modules

    def run(self) -> None:
        root = tk.Tk()
        root.title("Europa 1400 Manager")

        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill=tk.BOTH)

        for module in self.modules:
            module.initialize_gui(root, notebook)

        root.mainloop()
