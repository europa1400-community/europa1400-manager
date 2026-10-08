# 🧰 Europa 1400 Manager

Install community patches and fixes for **Europa 1400: The Guild** (*Die Gilde*) with a few clicks, change game
settings and back up your savegames. The manager finds your game, identifies the exact version and only offers what
fits.

**Documentation: [europa1400-community.github.io/europa1400-manager](https://europa1400-community.github.io/europa1400-manager/)**

## Download

| | Windows | Linux |
|---|---|---|
| **Window** | [europa1400-manager-gui-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-windows.exe) | [europa1400-manager-gui-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-linux) |
| Command line | [europa1400-manager-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-windows.exe) | [europa1400-manager-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-linux) |

No installation needed: download and start. The manager finds Steam and GOG installations by itself.

## What it does

- **Patches**: graphics fixes for current Windows, the multiplayer Netfix and more; what a patch needs is installed
  with it, files it replaces are backed up and restored when you uninstall it.
- **Game settings**: display mode, sound, multiplayer name and address, and every other game.ini value, without
  starting the game. Repairs the game's paths after moving the game folder.
- **Savegames**: back up and restore with one click.
- **Start the game** with the Direct3D 8 or the classic renderer.
- German and English.

Questions or problems: [Discord](https://discord.gg/jB9HYY8DpT) or
[GitHub issues](https://github.com/europa1400-community/europa1400-manager/issues).

---

## For developers

- Python 3.13 with [uv](https://docs.astral.sh/uv/): `uv sync --all-groups`, then `uv run python -m europa1400_manager`
  (window) or `uv run python -m europa1400_manager --help` (command line).
- Checks: `uv run ruff check .`, `uv run ty check .`, `uv run pytest -q`.
- Architecture and rules: [AGENTS.md](AGENTS.md). Patches and game versions come from
  [europa1400-database](https://github.com/europa1400-community/europa1400-database).
- Website: `uv sync --group docs`, `uv run mkdocs serve` (sources in `docs/`).
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/); releases: [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed, see [LICENSE.md](LICENSE.md). The window uses Qt for Python (PySide6, LGPL v3). The game itself is not
included.
