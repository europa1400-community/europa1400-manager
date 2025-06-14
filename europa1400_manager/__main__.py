import sys

import typer

from europa1400_manager.cli import Cli
from europa1400_manager.const import AppMode
from europa1400_manager.gui import Gui
from europa1400_manager.modules.config_module import ConfigModule
from europa1400_manager.modules.info_module import InfoModule
from europa1400_manager.modules.license_module import LicenseModule
from europa1400_manager.modules.tool_module import ToolModule


def main(app_mode: AppMode = AppMode.CLI) -> None:
    config_module = ConfigModule(app_mode)
    info_module = InfoModule(app_mode, config_module)
    tool_module = ToolModule(app_mode, config_module)
    license_module = LicenseModule(app_mode)

    modules = [
        config_module,
        info_module,
        tool_module,
        license_module,
    ]

    if app_mode is AppMode.GUI:
        gui = Gui(modules)
        gui.run()
    else:
        cli = Cli(modules)
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
