import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from europa1400_manager.const import AppMode
from europa1400_manager.modules.base_module import BaseModule


class LicenseModule(BaseModule):
    NAME = "license"
    FRIENDLY_NAME = "License"

    def __init__(self, app_mode: AppMode) -> None:
        super().__init__(app_mode)

    def show(self, all: bool = False) -> None:
        """Display the license information."""
        licenses: str
        if all:
            licenses = self._get_all_licenses()
        else:
            licenses = self._get_license()
        print(licenses)

    def _get_license(self) -> str:
        """Return the license information for the game."""
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path()

        license_file_path = base_path / "LICENSE.md"
        if license_file_path.exists():
            return license_file_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"License file not found at {license_file_path!r}.")

    def _get_all_licenses(self) -> str:
        """Return both LICENSE.md and NOTICE.md, whether frozen or not."""
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path()

        license_path = base_path / "LICENSE.md"
        notice_path = base_path / "NOTICE.md"

        if license_path.exists() and notice_path.exists():
            licenses = ""
            license_content = license_path.read_text(encoding="utf-8")
            notice_content = notice_path.read_text(encoding="utf-8")
            licenses += license_content
            licenses += "\n" + "=" * 40 + "\n"
            licenses += notice_content
            return licenses
        else:
            raise FileNotFoundError(
                f"Couldn't find LICENSE.md or NOTICE.md in {base_path!r}"
            )

    def _initialize_gui(self, root: tk.Tk, tab: ttk.Frame) -> None:
        top_frame = tk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        show_all_var = tk.BooleanVar(value=False)
        show_all_checkbox = tk.Checkbutton(
            top_frame, text="Show all licenses", variable=show_all_var
        )
        show_all_checkbox.pack(side=tk.LEFT, anchor=tk.W)

        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(text_widget.get("1.0", tk.END))

        copy_button = tk.Button(
            top_frame, text="Copy to Clipboard", command=copy_to_clipboard
        )
        copy_button.pack(side=tk.RIGHT, anchor=tk.E, padx=(5, 0))

        text_frame = tk.Frame(tab)
        text_frame.pack(expand=True, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        licenses = (
            self._get_all_licenses() if show_all_var.get() else self._get_license()
        )
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, licenses)
        text_widget.config(state=tk.DISABLED)
        scrollbar.config(command=text_widget.yview)

        def update_text_widget():
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            licenses = (
                self._get_all_licenses() if show_all_var.get() else self._get_license()
            )
            text_widget.insert(tk.END, licenses)
            text_widget.config(state=tk.DISABLED)

        show_all_checkbox.config(command=update_text_widget)
