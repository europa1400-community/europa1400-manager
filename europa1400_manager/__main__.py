import asyncio
import sys

import typer
from pyee import EventEmitter

from europa1400_manager.cli import Cli
from europa1400_manager.config import Config
from europa1400_manager.const import AppMode
from europa1400_manager.database import Database
from europa1400_manager.gui import Gui


async def main(app_mode: AppMode = AppMode.CLI) -> None:
    config = Config.load(app_mode)
    database = Database()
    await database.init()
    event_emitter = EventEmitter()

    if app_mode is AppMode.GUI:
        gui = Gui(config, database, event_emitter)
        await gui.run()
    else:
        cli = Cli(config, database)
        await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(
            main(
                app_mode=AppMode.GUI
                if len(sys.argv) > 1 and sys.argv[1] == "--gui"
                else AppMode.CLI
            )
        )
    except typer.Exit:
        pass
