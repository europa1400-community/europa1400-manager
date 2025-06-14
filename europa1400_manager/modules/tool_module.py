import typer

from europa1400_manager.const import AppMode, ToolType
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.modules.config_module import ConfigModule
from europa1400_manager.tools.ddrawcompat_tool import DDrawCompatTool
from europa1400_manager.utils import DialogUtils


class ToolModule(BaseModule):
    NAME = "tool"
    FRIENDLY_NAME = "Tools"

    def __init__(self, app_mode: AppMode, config_module: ConfigModule) -> None:
        super().__init__(app_mode)
        self.config_module = config_module

    async def install(
        self, tool_name: ToolType | None = typer.Argument(default=None)
    ) -> None:
        """Install the tools."""

        if tool_name is not None:
            if tool_name not in self.config_module.config.tools:
                self.config_module.config.tools.append(tool_name)
                self.config_module.config.to_file(self.config_module.config_file_path)

            return await self._install_tool(tool_name)

        for tool_type in self.config_module.config.tools:
            await self._install_tool(tool_type)

    async def _install_tool(self, tool_type: ToolType) -> None:
        """Install a specific tool."""
        match tool_type:
            case ToolType.DDRAWCOMPAT:
                tool = DDrawCompatTool(self.config_module.config)
                if not tool.is_installed:
                    await tool.install()
                    DialogUtils.tell(
                        self.app_mode,
                        f"{tool.FRIENDLY_NAME} has been installed successfully.",
                    )
                else:
                    DialogUtils.tell(
                        self.app_mode,
                        f"{tool.FRIENDLY_NAME} is already installed.",
                    )
            case _:
                DialogUtils.tell(
                    self.app_mode,
                    f"Tool {tool_type} is not supported.",
                )
