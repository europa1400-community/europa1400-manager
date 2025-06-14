# Repository Guide

## Commit Conventions

- Use **Conventional Commits** for all commit messages.

## Architecture Overview

- The application supports both **CLI** and **GUI** modes.
- Each module is represented as a **subcommand** in the CLI and as a **tab** in the GUI.
- Dialog utilities work for both CLI (Typer) and GUI (Tkinter).
- Configuration is persisted via a config file; everything else is stateless.
- The GUI uses **tkinter**, the CLI uses **typer**, and **asyncio** is used for asynchronous code.
- Public methods of modules are automatically exposed as commands.
- Modules can depend on other modules but **must not form circular dependencies**.
- The `Cli` class sets up the Typer application.
- The `Gui` class sets up the tkinter GUI.
- `async_typer.py` defines a subclass that enables async commands in Typer.
- The `tools/` directory contains tool classes describing how third‑party tools are installed.

## Environment

- The project uses **uv** for dependency management and is distributed as a **PyInstaller** executable.
- It is contained in a Python package and targets **Python 3.13**.
- Development uses **ruff** and **mypy**; always add type hints.
- The app is platform independent (Windows, macOS and Linux).
- Game installations for development live in the `./game/` directory (with subdirectories per version).
- Game assets reside in the `assets/` directory.

## Modules

Application modules might include the following:

- **config** – handles configuration management.
- **info** – provides information about the game installation.
- **tool** – installs and configures third‑party tools such as DDrawCompat.
- **savegame** – manages saves and improves autosaving in the game.
- **memory editor** – injects the memory editor DLL into the game.
- **patch** – applies community patches.
- **network bridge** – acts as a network bridge to improve multiplayer mode.
- **asset** – extracts, decodes and converts game assets.


