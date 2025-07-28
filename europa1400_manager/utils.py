import os
from pathlib import Path
from tkinter import messagebox, simpledialog
from typing import Any, TypeVar

import aiohttp
import typer
import yaml
from dotenv import load_dotenv
from yarl import URL

from europa1400_manager.const import (
    DEFAULT_CONFIG_FILE_PATH,
    DEFAULT_DATABASE_FILES_BASE_PATH,
    DEFAULT_DATABASE_REPOSITORY_BRANCH,
    DEFAULT_DATABASE_REPOSITORY_URL,
    ENV_CONFIG_FILE_PATH,
    ENV_DATABASE_FILES_BASE_PATH,
    ENV_DATABASE_REPOSITORY_BRANCH,
    ENV_DATABASE_REPOSITORY_URL,
    AppMode,
)
from europa1400_manager.models import DatabaseTable, GameMetadata


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

    @staticmethod
    def get_config_file_path() -> Path:
        """Get the default configuration file path."""
        return Path(EnvUtils.read(ENV_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_PATH))

    @staticmethod
    def get_database_repository_url() -> URL:
        """Get the database repository URL from environment variables."""
        return URL(
            EnvUtils.read(ENV_DATABASE_REPOSITORY_URL, DEFAULT_DATABASE_REPOSITORY_URL)
        )

    @staticmethod
    def get_database_repository_branch() -> str:
        """Get the database repository branch from environment variables."""
        return EnvUtils.read(
            ENV_DATABASE_REPOSITORY_BRANCH, DEFAULT_DATABASE_REPOSITORY_BRANCH
        )

    @staticmethod
    def get_database_files_base_path() -> str:
        """Get the base path for database files."""
        return EnvUtils.read(
            ENV_DATABASE_FILES_BASE_PATH, DEFAULT_DATABASE_FILES_BASE_PATH
        )


class PathUtils:
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


TTable = TypeVar("TTable", bound=DatabaseTable)


class DatabaseUtils:
    @staticmethod
    async def fetch_table(table_type: type[TTable]) -> TTable:
        url = (
            EnvUtils.get_database_repository_url()
            / EnvUtils.get_database_repository_branch()
            / EnvUtils.get_database_files_base_path()
            / table_type.FILE_NAME
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                response.raise_for_status()
                text = await response.text()
                table = table_type.from_yaml(text)
                if not isinstance(table, table_type):
                    raise TypeError(
                        f"Expected instance of {table_type.__name__}, got {type(table).__name__}"
                    )
                return table

    @staticmethod
    async def read_yaml_file(url: URL) -> dict[str, Any]:
        """Read a YAML file from a URL and return its contents."""
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                response.raise_for_status()
                text = await response.text()
                return yaml.safe_load(text)

    @staticmethod
    async def read_database_file(file_path: Path) -> dict[str, Any]:
        """Read the database file and return its contents."""
        repository_file_path = (
            EnvUtils.get_database_repository_url()
            / EnvUtils.get_database_repository_branch()
            / file_path.as_posix()
        )
        return await DatabaseUtils.read_yaml_file(repository_file_path)


class MetadataUtils:
    @staticmethod
    def generate_identifier(metadata: GameMetadata) -> str:
        """Generate a unique identifier for the game metadata."""
        if (
            metadata.edition is None
            or metadata.version is None
            or metadata.distribution is None
            or metadata.language is None
        ):
            raise ValueError("All properties must be set to generate an identifier.")

        return f"{metadata.edition}_{metadata.version}_{metadata.distribution}_{metadata.language}"

    @staticmethod
    def calc_changes(
        metadata: GameMetadata,
        other: GameMetadata,
        ignore_from_none: bool = True,
        ignore_to_none: bool = True,
    ) -> list[tuple[Any, Any]]:
        """Check if there are any changes between two :class:`GameMetadata` instances."""
        changes: list[tuple[str, tuple[Any, Any]]] = []

        for key in metadata.__dataclass_fields__.keys():
            value = getattr(metadata, key)
            other_value = getattr(other, key)

            if ignore_from_none and value is None:
                continue

            if ignore_to_none and other_value is None:
                continue

            if value != other_value:
                changes.append((key, (value, other_value)))

        return changes

    @staticmethod
    def merge(
        metadata: GameMetadata, other: GameMetadata, decisions: list[tuple[str, Any]]
    ) -> GameMetadata:
        """Merge two :class:`GameMetadata` instances based on decisions."""
        for other_key in other.__dataclass_fields__.keys():
            self_value = getattr(metadata, other_key)
            other_value = getattr(other, other_key)

            chosen_value = self_value if self_value is not None else other_value

            if self_value is not None and self_value != other_value:
                if other_key not in [d[0] for d in decisions]:
                    raise ValueError(
                        f"Decision for attribute {other_key} not found in decisions."
                    )

                chosen_value = next(d[1] for d in decisions if d[0] == other_key)

            setattr(metadata, other_key, chosen_value)

        return metadata
