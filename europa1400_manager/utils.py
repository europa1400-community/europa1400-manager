import os
from tkinter import messagebox, simpledialog

import typer
from dotenv import load_dotenv

from europa1400_manager.const import AppMode


class DialogUtils:
    @staticmethod
    def tell(app_mode: AppMode, message: str) -> None:
        """Display a message to the user."""
        if app_mode == AppMode.GUI:
            messagebox.showinfo("Information", message)
        else:
            typer.echo(message)

    @staticmethod
    def ask(app_mode: AppMode, prompt: str, default: str | None = None) -> str:
        """Ask a question and return the answer."""

        if app_mode == AppMode.GUI:
            return str(
                simpledialog.askstring("Input", prompt, initialvalue=default) or ""
            )
        else:
            return str(typer.prompt(text=prompt, default=default))

    @staticmethod
    def ask_yes_no(app_mode: AppMode, prompt: str, default: bool = True) -> bool:
        """Ask a yes/no question and return the answer."""
        if app_mode == AppMode.GUI:
            return bool(
                messagebox.askyesno(
                    "Question",
                    prompt,
                    default=messagebox.YES if default else messagebox.NO,
                )
            )
        else:
            return typer.confirm(text=prompt, default=default)


class EnvUtils:
    @staticmethod
    def read(name: str, default: str) -> str:
        """Get an environment variable or return a default value."""
        load_dotenv()

        return os.getenv(name, default)
