# Getting started

## Download

| | Windows | Linux |
|---|---|---|
| **Window** | [europa1400-manager-gui-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-windows.exe) | [europa1400-manager-gui-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-gui-linux) |
| Command line | [europa1400-manager-windows.exe](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-windows.exe) | [europa1400-manager-linux](https://github.com/europa1400-community/europa1400-manager/releases/latest/download/europa1400-manager-linux) |

Older versions and release notes: [releases](https://github.com/europa1400-community/europa1400-manager/releases).

## First start

1. Start the program; it needs no installation. Windows may warn about an unknown publisher, see
   [Troubleshooting](troubleshooting.md#windows-warns-about-the-program).
2. The manager looks for Steam and GOG installations. Pick yours, or choose the folder that contains `game.ini`.
3. The start page shows the detected game: *Known version* means the exact version is in the database.

The manager remembers the folder; with several installations switch between them on the *Manager* page.

## Recommended setup

The start page lists what the community recommends for your exact game version: the recommended items are
selected, optional ones (for example window mode) you can add. *Set up selected* installs and sets everything at once.
On the command line: `recommended` shows the list, `recommended --apply` sets it up.

## Installing a patch

Open *Patches*, pick a patch and click *Install*. Patches it needs are offered too. *Uninstall* removes it again and
restores the files it had replaced. A patch marked *Present* was installed by hand, by the store or by an older
manager; *Take over* reinstalls it under the manager's control.

Close the game before installing or removing patches; the manager checks that.

## Game settings and savegames

*Game settings* changes game.ini without starting the game (the original file is kept as
`game.ini.manager-backup`). *Savegames* backs them up to `Documents/Europa 1400 Manager/Backups`.

## Coming from version 1.x

The manager no longer keeps `config.yml` next to the program; it takes over the game folder from it once and stores
its settings in your user folder. Patches installed with 1.x show up as *Present* and can be taken over.
