# Command line

`europa1400-manager-windows.exe` (Linux: `europa1400-manager-linux`) does everything the window does, for scripts
and power users. `--help` works on every level. `--game <folder>` uses another installation for one command.

| Command | What it does |
|---|---|
| `games` | list the installations found on this computer |
| `use <folder>` | choose the game folder |
| `info` | the detected game (edition, version, language, store, executables) |
| `start` / `start --dx6` | start the game (Direct3D 8 / classic renderer) |
| `repair-paths` | point the paths in game.ini to the game folder (after moving the game) |
| `patches list` | patches and their state |
| `patches install <id> ...` | install patches and what they need |
| `patches uninstall <id> ... [--with-dependents]` | uninstall; replaced files are restored |
| `ini show` / `ini get <section> <key>` / `ini set <section> <key> <value>` | read and change game.ini |
| `saves list` / `saves backup` / `saves restore <zip>` | savegames |
| `update-check` | look for a newer manager |
| `--version`, `--verbose` | version, detailed log |

Patch ids: see [All patches](patch-list.md), for example `netfix`, `dxwrapper`, `dxvk`, `ddraw_compat`.

Settings, log and cache live in your user folder (Windows: `%APPDATA%\europa1400-community\europa1400-manager`,
`%LOCALAPPDATA%\europa1400-community\europa1400-manager`); the *Manager* page of the window opens them.
