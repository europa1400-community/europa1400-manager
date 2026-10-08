# 🧰 Europa 1400 Manager

Install community patches and fixes for **Europa 1400: The Guild** (*Die Gilde*) with a few clicks: graphics fixes for
modern Windows, the multiplayer network fix and more. The manager detects your game version and only offers what fits.

**Documentation: [europa1400-community.github.io/europa1400-manager](https://europa1400-community.github.io/europa1400-manager/)**

## Download

| | Windows | Linux |
|---|---|---|
| Window (GUI) | [europa1400-manager-gui-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-windows.exe) | [europa1400-manager-gui-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-linux) |
| Command line | [europa1400-manager-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-windows.exe) | [europa1400-manager-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-linux) |

No installation needed: put the file in a folder of its own and start it. On first start the manager asks for your
game folder and remembers it in `config.yml` next to the program.

## Quick start

- **GUI:** start `europa1400-manager-gui-windows.exe`, open the *Patches* tab and install what you need.
- **Command line:**

  ```text
  europa1400-manager-windows.exe info show              # detected game version
  europa1400-manager-windows.exe patch install netfix   # install a patch (needed patches come along)
  europa1400-manager-windows.exe patch uninstall netfix # remove it again
  ```

Which patch is for what: [Patches](https://europa1400-community.github.io/europa1400-manager/patches/).
Problems or questions: [Discord](https://discord.gg/jB9HYY8DpT) or
[GitHub issues](https://github.com/europa1400-community/europa1400-manager/issues).

---

## For developers

- Python 3.13 with [uv](https://docs.astral.sh/uv/): `uv sync --all-groups`, then `uv run python -m europa1400_manager`
  (add `--gui` for the window).
- Checks: `uv run ruff check .` and `uv run ty check .`.
- Patches and game versions come from [europa1400-database](https://github.com/europa1400-community/europa1400-database);
  how to add a patch type: [Development](https://europa1400-community.github.io/europa1400-manager/development/).
- Documentation website: `uv sync --group docs`, `uv run mkdocs serve` (sources in `docs/`, published on every push to
  `master`).
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/); releases: see
  [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed, see [LICENSE.md](LICENSE.md). The game itself is not included.
