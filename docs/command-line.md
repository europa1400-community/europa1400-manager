# Command line

The command line version (`europa1400-manager-windows.exe`, `europa1400-manager-linux`) offers the same functions as
the window. `--help` works on every level, for example `europa1400-manager-windows.exe patch --help`.

| Command | What it does |
|---|---|
| `overview start-game` | start the game |
| `overview start-game-tl` | start the T&L version of the game |
| `info show` | show the detected game (edition, version, language, store) |
| `info checksums` | checksums of the game files (useful for bug reports) |
| `patch install <id>` | install a patch and the patches it needs |
| `patch uninstall <id>` | uninstall a patch |
| `config show` | show the configuration (game folder) |
| `license show` | licenses of the manager and the bundled libraries |
| `--gui` | open the window instead |

Patch ids: see [All patches](patch-list.md), for example `netfix`, `dxwrapper`, `dxvk`, `ddraw_compat`.

The configuration lives in `config.yml` in the folder you start the program from. Delete it to choose the game folder
again.
