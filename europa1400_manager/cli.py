from europa1400_manager.async_typer import AsyncTyper
from europa1400_manager.modules.base_module import BaseModule


class Cli:
    def __init__(self, modules: list[BaseModule]) -> None:
        self.modules = modules
        self.typer_app = AsyncTyper(no_args_is_help=True)
        self.typer_app.callback()(self.default)

        for module in self.modules:
            self.typer_app.add_typer(module.typer_app, name=module.NAME)

    def run(self) -> None:
        self.typer_app()

    def default(self, gui: bool = False) -> None:
        """Launch the GUI."""
