import typer

from europa1400_manager.modules.base_module import BaseModule


class ConfigModule(BaseModule):
    NAME = "config"
    FRIENDLY_NAME = "Configuration"

    async def show(self) -> None:
        """Show the current configuration."""
        typer.echo(f"Current configuration: {self.config.to_json(indent=2)}")
