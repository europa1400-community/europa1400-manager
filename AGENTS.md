# Repository Guide

Europa 1400 Manager: installs community patches, edits game settings, backs up savegames. Players use the window
(`europa1400-manager-gui`), power users and scripts the command line (`europa1400-manager`).

## Rules

- **Conventional Commits** for commits and pull request titles (they decide the release version, see CONTRIBUTING.md).
- Code, comments and docs in English; user-facing texts in English and German (`i18n.py`, `gui/texts.py`).
- Never write into a game folder except through `core/install_state.py` (transactions with backups and rollback) or
  `core/ini.py` (lossless game.ini edits). Never ship or commit game files.
- Before a commit: `uv run ruff check .`, `uv run ruff format .`, `uv run ty check .`, `uv run pytest -q`.

## Architecture

```text
europa1400_manager/
  core/            everything the manager does, no UI (CLI and GUI only call into it)
    database.py      europa1400-database tables: fetch, offline cache, tolerant parsing
    models.py        table models (new fields always optional; new patch types in tables of their own)
    detection.py     finding installations (Steam, GOG, registry, folders) and identifying them
                     (SHA-256 of known files first, then heuristics: PE imports, game.ini language, store files)
    game.py          a game: launch, running check, write access, repairing game.ini paths
    install_state.py <game>/.europa1400-manager/state.json: files, backups, INI changes per patch; transactions
    handlers/        how each patch type is installed (simple, archive, e1400patch loader and modules)
    patches.py       patch status, requirements, conflicts, install/update/uninstall
    download.py      downloads (checksums, size limit, cache) and safe archive extraction
    game_settings.py the game.ini settings with proper controls
    savegames.py     savegame list, backup, restore
    settings.py      manager settings (user config folder; takes over config.yml of manager <= 1.2)
    updates.py       new manager version check
  cli.py           typer commands
  gui/             PySide6 window: app.py (Qt + asyncio via qasync), state.py (shared state and signals),
                   main_window.py, pages/, widgets.py, theme.py, texts.py
  i18n.py          tr(key, **values)
tests/             pytest (core only, fake game folders, no game files)
```

- Long work runs as coroutines (`AppState.run`); blocking file work inside them goes through `asyncio.to_thread`.
- `ManagerError` (and subclasses) carry a message for the player; anything else is a bug and is logged with traceback.
- Development data: `E1400_MANAGER_DATABASE_DIR=<checkout>/data` uses a local database;
  `E1400_MANAGER_CONFIG_DIR`, `_CACHE_DIR`, `_LOG_DIR` move the manager's own files (tests do that).

## Environment

- uv, Python 3.13, PyInstaller (`pyinstaller.spec`; the command line executable is built without Qt).
- Windows first; Linux works for Steam/Wine installations (launching uses `wine`).
- Qt for Python (PySide6) is LGPL v3: keep it dynamically linked (PyInstaller does) and the notice in the About page.

## Ideas for later

savegame cleanup, mod support through europa1400-patches (`mods/`), network bridge, asset tools, memory editor.
