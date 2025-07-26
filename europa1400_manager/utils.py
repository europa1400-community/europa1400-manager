import os
from pathlib import Path
from tkinter import messagebox, simpledialog

import typer
from dotenv import load_dotenv

from europa1400_manager.const import (
    DEFAULT_CONFIG_FILE_PATH,
    ENV_CONFIG_FILE_PATH,
    AppMode,
)


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


class PathUtils:
    @staticmethod
    def get_config_file_path() -> Path:
        """Get the default configuration file path."""
        return Path(EnvUtils.read(ENV_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_PATH))

    @staticmethod
    def get_game_path(app_mode: AppMode) -> Path:
        while True:
            game_path = Path(
                DialogUtils.ask(
                    app_mode,
                    "Please enter the path to the game directory:",
                    default=str(Path.home() / "Europa 1400"),
                )
            )

            if PathUtils._validate_game_path(app_mode, game_path):
                break

        return game_path

    @staticmethod
    def _validate_game_path(app_mode: AppMode, game_path: Path) -> bool:
        """Validate the game path."""
        if not game_path.exists():
            DialogUtils.tell(app_mode, "Invalid game path. Please try again.")
            return False

        return True
