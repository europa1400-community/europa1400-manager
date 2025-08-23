"""GUI entry point for europa1400-manager."""

import asyncio

import typer
from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.const import AppMode
from europa1400_manager.database import Database
from europa1400_manager.gui import Gui


async def main() -> None:
    """Main entry point for GUI mode."""
    config = Config.load(AppMode.GUI)
    database = Database()
    await database.init()
    event_emitter = EventEmitter()

    gui = Gui(config, database, event_emitter)
    await gui.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except typer.Exit:
        pass
