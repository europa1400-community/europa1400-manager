# Development

## Setup

Python 3.13 with [uv](https://docs.astral.sh/uv/):

```text
uv sync --all-groups
uv run python -m europa1400_manager          # window
uv run python -m europa1400_manager --help   # command line
uv run ruff check . ; uv run ty check . ; uv run pytest -q
```

Use a local copy of the database with `E1400_MANAGER_DATABASE_DIR=<europa1400-database>/data`; a branch of the
online database is set on the *Manager* page (testers).

## Structure

`europa1400_manager/core/` holds everything the manager does without a user interface: database, game detection,
patch handlers, the install journal with backups and rollback, game settings, savegames. The command line
(`cli.py`, typer) and the window (`gui/`, PySide6 with asyncio through qasync) only call into it. Details:
[AGENTS.md](https://github.com/europa1400-community/europa1400-manager/blob/master/AGENTS.md).

## Adding a patch type

1. Add the type to `PatchType` (`core/models.py`) and a handler in `core/handlers/` that writes only through the
   `Transaction` it gets (files, INI values, owned folders).
2. Register it in `core/handlers/__init__.py`.
3. Put database entries of a new type into a table of their own: older managers fail on unknown types.

## Website

Sources in `docs/`, configuration in `mkdocs.yml`; the patch list is generated from the database by
`scripts/gen_patch_table.py`. Preview with `uv sync --group docs` and `uv run mkdocs serve`. GitHub Actions publishes
the site on every push to `master` and once a day.

## Releases

Conventional Commits decide the version. In GitHub: **Actions → Release → Run workflow**; see
[CONTRIBUTING.md](https://github.com/europa1400-community/europa1400-manager/blob/master/CONTRIBUTING.md).
