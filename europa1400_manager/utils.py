import os

import typer
from dotenv import load_dotenv

from europa1400_manager.const import AppMode


class DialogUtils:
    @staticmethod
    def tell(app_mode: AppMode, message: str) -> None:
        """Display a message to the user."""
        if app_mode == AppMode.GUI:
            raise NotImplementedError("GUI dialog not implemented yet.")
        else:
            typer.echo(message)

    @staticmethod
    def ask(app_mode: AppMode, prompt: str, default: str | None = None) -> str:
        """Ask a question and return the answer."""

        if app_mode == AppMode.GUI:
            raise NotImplementedError("GUI dialog not implemented yet.")
        else:
            return typer.prompt(text=prompt, default=default)

    @staticmethod
    def ask_yes_no(app_mode: AppMode, prompt: str, default: bool = True) -> bool:
        """Ask a yes/no question and return the answer."""
        if app_mode == AppMode.GUI:
            raise NotImplementedError("GUI dialog not implemented yet.")
        else:
            return typer.confirm(text=prompt, default=default)


class EnvUtils:
    @staticmethod
    def read(name: str, default: str) -> str:
        """Get an environment variable or return a default value."""
        load_dotenv()

        return os.getenv(name, default)
