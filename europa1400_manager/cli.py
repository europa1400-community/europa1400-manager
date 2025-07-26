from europa1400_manager.async_typer import AsyncTyper
from europa1400_manager.config import Config
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.modules.config_module import ConfigModule
from europa1400_manager.modules.info_module import InfoModule
from europa1400_manager.modules.license_module import LicenseModule
from europa1400_manager.modules.tool_module import ToolModule


class Cli:
    def __init__(self, config: Config) -> None:
        config_module = ConfigModule(config)
        info_module = InfoModule(config)
        tool_module = ToolModule(config)
        license_module = LicenseModule(config)

        self.modules: list[BaseModule] = [
            config_module,
            info_module,
            tool_module,
            license_module,
        ]
        self.typer_app = AsyncTyper(no_args_is_help=True)
        self.typer_app.callback()(self.default)

        for module in self.modules:
            self.typer_app.add_typer(module.typer_app, name=module.NAME)

    def run(self) -> None:
        self.typer_app()

    def default(self, gui: bool = False) -> None:
        """Launch the GUI."""
