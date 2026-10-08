# Troubleshooting

## Windows warns about the program

The executables are not signed, so Windows SmartScreen may show "Windows protected your PC". Click *More info* and
*Run anyway*. Only download the manager from the
[releases page](https://github.com/europa1400-community/europa1400-manager/releases) or the links on this website.

## "The manager cannot write into the game folder"

Games in `C:\Program Files (x86)` can only be changed with administrator rights. Start the manager as administrator
(right click → *Run as administrator*), or install the game somewhere else (GOG lets you choose the folder).

## The game does not start after moving or copying it

game.ini contains the game folder. The start page shows a notice with *Repair*; on the command line run
`europa1400-manager repair-paths`.

## Multiplayer

- Only the **host** needs Netfix.
- Joining over the Internet without a VPN: the host forwards **TCP port 7531** (game.ini `[Network] Port`) in the
  router, the others enter the host's address. Finding games in the lobby list works only in a (virtual) LAN.
- The host's log `e1400patch\logs\e1400patch.log` (in the game folder) shows a line `netfix: session: ...` for every
  hosted game. Attach it when you report a problem.

## Something went wrong

The manager's log is on the *Manager* page (*Log folder*). Report the problem on [Discord](https://discord.gg/jB9HYY8DpT)
or as a [GitHub issue](https://github.com/europa1400-community/europa1400-manager/issues) with the log and the game
version from the start page.

## Removing everything

Uninstall every patch on the *Patches* page, then delete the program. Uninstalling restores the files a patch had
replaced and the game.ini values it had changed; files you changed yourself afterwards are kept.
