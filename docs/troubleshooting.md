# Troubleshooting

## Windows warns about the program

The executables are not signed, so Windows SmartScreen may show "Windows protected your PC". Click *More info* and
*Run anyway*. Only download the manager from the
[releases page](https://github.com/europa1400-community/europa1400-manager/releases) or the links on this website.

## The manager asks for the game folder again

The folder is stored in `config.yml` in the folder you start the manager from. Start it from the same folder each time,
or delete `config.yml` to choose a different game folder.

## Multiplayer still disconnects

- Only the **host** needs Netfix; check that it is installed on the host's game.
- The host's log `e1400patch\logs\e1400patch.log` (in the game folder) shows a line `netfix: session: ...` for every
  hosted game. Attach it when you report the problem.
- Report it on [Discord](https://discord.gg/jB9HYY8DpT) or as a
  [GitHub issue](https://github.com/europa1400-community/europa1400-patches/issues) with the game version
  (`info show`).

## Removing everything

Uninstall every patch in the manager (or with `patch uninstall <id>`), then delete the manager's folder. Uninstalling
deletes the files a patch added; the patch loader also restores the `game.ini` setting it changed.
