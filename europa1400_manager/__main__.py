import sys

import typer

from europa1400_manager.cli import Cli
from europa1400_manager.config import Config
from europa1400_manager.const import AppMode
from europa1400_manager.gui import Gui


def main(app_mode: AppMode = AppMode.CLI) -> None:
    config = Config.load(app_mode)

    if app_mode is AppMode.GUI:
        gui = Gui(config)
        gui.run()
    else:
        cli = Cli(config)
        cli.run()


if __name__ == "__main__":
    try:
        main(
            app_mode=AppMode.GUI
            if len(sys.argv) > 1 and sys.argv[1] == "--gui"
            else AppMode.CLI
        )
    except typer.Exit:
        pass
