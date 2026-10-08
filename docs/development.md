# Development

## Setup

Python 3.13 with [uv](https://docs.astral.sh/uv/):

```text
uv sync --all-groups
uv run python -m europa1400_manager --help    # command line
uv run python -m europa1400_manager --gui     # window
uv run ruff check .
uv run ty check .
```

## Structure

- Each module (`europa1400_manager/modules/`) is a command group on the command line and a tab in the window. Public
  methods of a module become commands; helpers start with `_`.
- Patch types (`europa1400_manager/patches/`) describe how a patch is installed: `simple` (one file), `archive`
  (files from an archive, optional INI changes), `e1400patch_loader` and `e1400patch_module`
  ([europa1400-patches](https://github.com/europa1400-community/europa1400-patches)).
- Data comes from [europa1400-database](https://github.com/europa1400-community/europa1400-database) (`master`,
  fetched at start). Override with `DATABASE_REPOSITORY_BRANCH` (e.g. a feature branch) in the environment or `.env`.

## Adding a patch type

1. Add the type to `PatchType` (`const.py`) and a class derived from `BasePatch` in `patches/`.
2. Register it in `PatchModule.PATCH_TYPE_TO_CLASS`.
3. Put database entries of a new type into a table of their own (like `e1400patch.yml`): managers that do not know the
   type would otherwise fail on the whole table.

## Website

Sources in `docs/`, configuration in `mkdocs.yml`; the patch list is generated from the database by
`scripts/gen_patch_table.py`. Preview with `uv sync --group docs` and `uv run mkdocs serve`. GitHub Actions publishes the
site on every push to `master` and once a day.

## Releases

Conventional Commits decide the version. In GitHub: **Actions → Release → Run workflow**; see
[CONTRIBUTING.md](https://github.com/europa1400-community/europa1400-manager/blob/master/CONTRIBUTING.md).
