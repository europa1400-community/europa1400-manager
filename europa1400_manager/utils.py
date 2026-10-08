import configparser
import os
from pathlib import Path
from tkinter import messagebox, simpledialog
from typing import Any, TypeVar, cast

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

        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Accept-Encoding": "deflate",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(str(url), headers=headers) as response:
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
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Accept-Encoding": "deflate",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(str(url), headers=headers) as response:
                response.raise_for_status()
                text = await response.text()

        return cast(dict[str, Any], yaml.safe_load(text))

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


class PreservingIniUtils:
    """Line based access to Windows INI files that keeps everything else of the file as it is.

    For files the game reads with the Windows profile API (game.ini): keys are case-insensitive, quotes around values are
    stripped on reading, the file stays in the ANSI code page, comments, order, spelling and line endings are kept.
    """

    ENCODING = "cp1252"

    @classmethod
    def _read_lines(cls, file_path: Path) -> list[str]:
        if not file_path.exists():
            return []
        return file_path.read_text(encoding=cls.ENCODING).splitlines(keepends=True)

    @staticmethod
    def _section_of(line: str) -> str | None:
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            return stripped[1 : stripped.index("]")].strip().lower()
        return None

    @staticmethod
    def _key_of(line: str) -> str | None:
        stripped = line.strip()
        if not stripped or stripped[0] in ";#" or "=" not in stripped:
            return None
        return stripped.split("=", 1)[0].strip().lower()

    @classmethod
    def get_value(cls, file_path: Path, section: str, key: str) -> str | None:
        """Value of a key (surrounding quotes removed), None when missing."""
        current = None
        for line in cls._read_lines(file_path):
            name = cls._section_of(line)
            if name is not None:
                current = name
            elif current == section.lower() and cls._key_of(line) == key.lower():
                value = line.split("=", 1)[1].strip()
                if len(value) >= 2 and value[0] == value[-1] == '"':
                    value = value[1:-1]
                return value
        return None

    @classmethod
    def set_value(
        cls, file_path: Path, section: str, key: str, value: str | None
    ) -> None:
        """Set (or with None remove) a key; adds the section and key if missing."""
        lines = cls._read_lines(file_path)
        newline = "\r\n" if not lines or lines[0].endswith("\r\n") else "\n"
        current, section_end, done = None, None, False
        result: list[str] = []
        for line in lines:
            name = cls._section_of(line)
            if name is not None:
                if current == section.lower() and not done and value is not None:
                    insert_at = section_end if section_end is not None else len(result)
                    result.insert(insert_at, f"{key}={value}{newline}")
                    done = True
                current = name
            elif current == section.lower() and cls._key_of(line) == key.lower():
                if value is not None and not done:
                    ending = (
                        "\r\n"
                        if line.endswith("\r\n")
                        else ("\n" if line.endswith("\n") else "")
                    )
                    original_key = line.split("=", 1)[0].strip()
                    result.append(f"{original_key}={value}{ending or newline}")
                    done = True
                continue
            result.append(line)
            if current == section.lower() and line.strip():
                section_end = len(result)
        if value is not None and not done:
            if current == section.lower() or section_end is not None:
                insert_at = section_end if section_end is not None else len(result)
                result.insert(insert_at, f"{key}={value}{newline}")
            else:
                if result and not result[-1].endswith(("\n", "\r\n")):
                    result[-1] += newline
                result.append(f"[{section}]{newline}")
                result.append(f"{key}={value}{newline}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("".join(result), encoding=cls.ENCODING, newline="")


class IniUtils:
    @staticmethod
    def set_key_value(
        file_path: Path, section: str, key: str, value: str | int | float | bool
    ) -> None:
        """Set a key-value pair in an INI file section."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        config_parser = configparser.ConfigParser()
        if file_path.exists():
            config_parser.read(file_path, encoding="utf-8")

        if not config_parser.has_section(section):
            config_parser.add_section(section)

        config_parser.set(section, key, str(value))

        with open(file_path, "w", encoding="utf-8") as config_file:
            config_parser.write(config_file)
