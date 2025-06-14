import inspect
from abc import ABC

from europa1400_manager.async_typer import AsyncTyper
from europa1400_manager.const import AppMode


class BaseModule(ABC):
    NAME: str
    FRIENDLY_NAME: str
    app_mode: AppMode
    typer_app: AsyncTyper

    def __init__(self, app_mode: AppMode) -> None:
        self.app_mode = app_mode
        self.typer_app = AsyncTyper(no_args_is_help=True)
        self.typer_app.info.name = self.NAME
        self.typer_app.info.help = f"{self.FRIENDLY_NAME} module"

        self._register_commands()

    def _register_commands(self):
        for attr_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if attr_name in BaseModule.__dict__:
                continue
            if attr_name.startswith("_"):
                continue

            command = self.typer_app.command(
                name=attr_name.replace("_", "-"), help=method.__doc__ or ""
            )
            command(method)
