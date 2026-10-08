# Getting started

## Download

| | Windows | Linux |
|---|---|---|
| Window (GUI) | [europa1400-manager-gui-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-windows.exe) | [europa1400-manager-gui-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-linux) |
| Command line | [europa1400-manager-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-windows.exe) | [europa1400-manager-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-linux) |

Older versions and release notes: [releases](https://github.com/europa1400-community/europa1400-manager/releases).

## First start

1. Put the program into a folder of its own (for example `Documents\Europa 1400 Manager`). It needs no installation.
2. Start it. Windows may warn about an unknown publisher, see [Troubleshooting](troubleshooting.md#windows-warns-about-the-program).
3. Enter your game folder, the one that contains `game.ini`, for example
   `C:\GOG Games\Europa 1400 Gold` or `C:\Program Files (x86)\Steam\steamapps\common\Europa 1400 The Guild Gold`.
4. The manager detects the game version and remembers the folder in `config.yml` next to the program.

## Installing a patch

**GUI:** open the *Patches* tab, pick a patch and install it. Uninstall works the same way.

**Command line:**

```text
europa1400-manager-windows.exe patch install netfix
europa1400-manager-windows.exe patch uninstall netfix
```

Which patch fixes what: [Patches](patches.md). Install only what you need; every patch can be removed again.
