"""Command line interface (typer). Every command works on the configured game folder; --game overrides it."""

from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from europa1400_manager import i18n
from europa1400_manager._version import __version__
from europa1400_manager.core import database as database_module
from europa1400_manager.core import (
    detection,
    game_settings,
    ini,
    logs,
    recommendations,
    savegames,
    updates,
)
from europa1400_manager.core.database import Database
from europa1400_manager.core.errors import ManagerError
from europa1400_manager.core.game import Game
from europa1400_manager.core.patches import PatchService
from europa1400_manager.core.settings import Settings

log = logging.getLogger(__name__)

app = typer.Typer(
    no_args_is_help=False,
    add_completion=False,
    help="Europa 1400 Manager: patches, settings, savegames.",
)
patches_app = typer.Typer(no_args_is_help=True, help="Install and remove patches.")
saves_app = typer.Typer(no_args_is_help=True, help="Back up and restore savegames.")
ini_app = typer.Typer(no_args_is_help=True, help="Read and change game.ini.")
app.add_typer(patches_app, name="patches")
app.add_typer(patches_app, name="patch", hidden=True)  # manager <= 1.2
app.add_typer(saves_app, name="saves")
app.add_typer(ini_app, name="ini")

GameOption = Annotated[
    Path | None,
    typer.Option("--game", "-g", help="Game folder (default: the configured one)."),
]


class Context:
    def __init__(self, game_path: Path | None = None) -> None:
        self.settings = Settings.load()
        i18n.set_language(self.settings.language or "en")
        self.database: Database = asyncio.run(
            database_module.load(self.settings.database_branch)
        )
        if self.database.source in ("cache", "partial-cache"):
            typer.secho("Offline: using the cached database.", fg="yellow", err=True)
        self._game_path = game_path

    def game(self) -> Game:
        path = self._game_path or self.settings.game_dir
        if path is None:
            found = detection.find_installations(
                self.database, self.settings.known_game_paths
            )
            if len(found) != 1:
                raise ManagerError(
                    "No game folder configured. Run `europa1400-manager games` and `europa1400-manager use <folder>`."
                )
            path = found[0]
            self.settings.remember_game(path)
            self.settings.save()
        return Game.open(path, self.database)


def run(function: Callable[[], object]) -> None:
    """Show ManagerError messages without a traceback."""
    try:
        function()
    except ManagerError as error:
        typer.secho(str(error), fg="red", err=True)
        raise typer.Exit(1) from error


def _progress_line(message: str, fraction: float | None) -> None:
    """Patch start messages as lines, download progress on one updating line."""
    if fraction is None:
        typer.echo(message)
    else:
        typer.echo(f"\r  {int(fraction * 100):3d}%", nl=fraction >= 1.0)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    gui: Annotated[bool, typer.Option("--gui", help="Open the window.")] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Detailed log.")
    ] = False,
    version: Annotated[
        bool, typer.Option("--version", help="Show the version.")
    ] = False,
) -> None:
    logs.setup(verbose)
    if version:
        typer.echo(__version__)
        raise typer.Exit
    if gui or ctx.invoked_subcommand is None:
        try:
            from europa1400_manager.gui.app import main as gui_main
        except ImportError:  # the command line executable is built without Qt
            typer.echo(ctx.get_help())
            typer.echo(
                "\nThe window is europa1400-manager-gui; this program is the command line version."
            )
            raise typer.Exit from None
        raise typer.Exit(gui_main())


@app.command()
def games() -> None:
    """List the game installations found on this computer."""
    context = Context()
    found = detection.find_installations(
        context.database, context.settings.known_game_paths
    )
    if not found:
        typer.echo("No installation found. Use `europa1400-manager use <folder>`.")
    for path in found:
        marker = "*" if str(path) == context.settings.game_path else " "
        typer.echo(f"{marker} {path}")


@app.command()
def use(folder: Path) -> None:
    """Set the game folder."""

    def action() -> None:
        context = Context()
        game = Game.open(folder.resolve(), context.database)
        context.settings.remember_game(game.path)
        context.settings.save()
        typer.echo(f"Game folder: {game.path}")

    run(action)


@app.command()
def info(game: GameOption = None) -> None:
    """Show the detected game."""

    def action() -> None:
        context = Context(game)
        current = context.game()
        typer.echo(f"Folder:       {current.path}")
        for key in detection.FIELDS:
            value = current.info.metadata.get(key)
            source = current.info.sources.get(key, "")
            name = context.database.name_of(key, value) if value else "?"
            typer.echo(
                f"{key.capitalize():<13} {name}{'' if source in ('hash', '') else '  (guessed)'}"
            )
        for exe in current.info.executables:
            typer.echo(
                f"Executable:   {exe.path.name} ({exe.renderer or '?'}, {'known' if exe.known else 'unknown'} build)"
            )
        for key, current_value, expected in current.path_problems():
            typer.secho(
                f"game.ini {key} points to {current_value}; run `repair-paths` ({expected})",
                fg="yellow",
            )

    run(action)


@app.command()
def start(
    game: GameOption = None,
    dx6: Annotated[bool, typer.Option(help="Start the DirectX 6 build.")] = False,
) -> None:
    """Start the game."""
    run(lambda: Context(game).game().launch("dx6" if dx6 else "d3d8"))


@app.command("repair-paths")
def repair_paths(game: GameOption = None) -> None:
    """Point the paths in game.ini to this game folder (after moving or copying the game)."""

    def action() -> None:
        fixed = Context(game).game().repair_paths()
        typer.echo(f"Repaired: {', '.join(fixed)}" if fixed else "All paths are fine.")

    run(action)


@patches_app.command("list")
def patches_list(game: GameOption = None) -> None:
    """List the patches and their state."""

    def action() -> None:
        context = Context(game)
        service = PatchService(context.game(), context.database)
        for status in service.statuses():
            compatible = {True: "", False: " (not for this game version)", None: ""}[
                status.compatible
            ]
            version = f" {status.installed_version}" if status.installed_version else ""
            typer.echo(
                f"{status.patch.id:<16} {status.state.value:<10}{version}  {status.patch.name}{compatible}"
            )

    run(action)


@patches_app.command("install")
def patches_install(patch_ids: list[str], game: GameOption = None) -> None:
    """Install patches (and what they need)."""

    def action() -> None:
        context = Context(game)
        service = PatchService(context.game(), context.database)
        for patch_id in patch_ids:
            installed = asyncio.run(service.install(patch_id, _progress_line))
            typer.echo(f"Installed: {', '.join(installed) or patch_id}")

    run(action)


@patches_app.command("uninstall")
def patches_uninstall(
    patch_ids: list[str],
    game: GameOption = None,
    with_dependents: Annotated[
        bool, typer.Option(help="Also remove patches that need it.")
    ] = False,
) -> None:
    """Uninstall patches; files they replaced are restored."""

    def action() -> None:
        context = Context(game)
        service = PatchService(context.game(), context.database)
        for patch_id in patch_ids:
            for warning in service.uninstall(patch_id, with_dependents):
                typer.secho(warning, fg="yellow")
            typer.echo(f"Uninstalled: {patch_id}")

    run(action)


@app.command()
def recommended(
    game: GameOption = None,
    apply: Annotated[
        bool, typer.Option("--apply", help="Set up what is recommended.")
    ] = False,
    include_optional: Annotated[
        bool, typer.Option("--all", help="With --apply: also the optional items.")
    ] = False,
) -> None:
    """Show (and with --apply set up) the recommended patches and settings for this game version."""

    def action() -> None:
        context = Context(game)
        service = PatchService(context.game(), context.database)
        items = recommendations.items(service, i18n.language())
        if not items:
            typer.echo("No recommendations for this game version.")
            return
        for item in items:
            state = "done" if item.done else ("n/a" if not item.available else "")
            typer.echo(f"{item.level:<12} {state:<5} {item.title}  ({item.reason})")
        if apply:
            chosen = [
                i
                for i in items
                if i.available and not i.done and (i.recommended or include_optional)
            ]
            done = asyncio.run(recommendations.apply(service, chosen, _progress_line))
            typer.echo(f"Set up: {', '.join(done) or 'nothing to do'}")

    run(action)


@ini_app.command("get")
def ini_get(section: str, key: str, game: GameOption = None) -> None:
    """Print a value of game.ini."""
    run(lambda: typer.echo(ini.get(Context(game).game().game_ini, section, key) or ""))


@ini_app.command("set")
def ini_set(section: str, key: str, value: str, game: GameOption = None) -> None:
    """Change a value of game.ini (everything else in the file stays as it is)."""

    def action() -> None:
        current = Context(game).game()
        current.ensure_not_running()
        ini.set_value(current.game_ini, section, key, value)

    run(action)


@ini_app.command("show")
def ini_show(game: GameOption = None) -> None:
    """Show the settings the manager knows."""

    def action() -> None:
        values = game_settings.read(Context(game).game().game_ini)
        for setting in game_settings.SETTINGS:
            typer.echo(
                f"[{setting.section}] {setting.key} = {values[(setting.section, setting.key)]}"
            )

    run(action)


@saves_app.command("list")
def saves_list(game: GameOption = None) -> None:
    """List the savegames."""

    def action() -> None:
        for save in savegames.list_savegames(Context(game).game()):
            kind = "multiplayer" if save.multiplayer else "single"
            typer.echo(f"{save.modified:%Y-%m-%d %H:%M}  {kind:<11} {save.relative}")

    run(action)


@saves_app.command("backup")
def saves_backup(game: GameOption = None) -> None:
    """Back up all savegames into a zip (Documents/Europa 1400 Manager/Backups)."""
    run(lambda: typer.echo(savegames.backup(Context(game).game())))


@saves_app.command("restore")
def saves_restore(archive: Path, game: GameOption = None) -> None:
    """Restore savegames from a backup zip (the current ones are backed up first)."""
    run(
        lambda: typer.echo(
            f"Restored {savegames.restore(Context(game).game(), archive)} savegames."
        )
    )


@app.command("update-check")
def update_check() -> None:
    """Check for a newer manager version."""
    update = asyncio.run(updates.check())
    typer.echo(
        f"Version {update.version} is available: {update.url}"
        if update
        else f"Up to date ({__version__})."
    )


# commands of manager <= 1.2
legacy_overview = typer.Typer(hidden=True)
app.add_typer(legacy_overview, name="overview", hidden=True)
legacy_overview.command("start-game")(start)


def entry() -> None:
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)
