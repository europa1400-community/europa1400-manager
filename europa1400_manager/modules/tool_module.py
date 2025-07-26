import typer

from europa1400_manager.const import ToolType
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.tools.ddrawcompat_tool import DDrawCompatTool
from europa1400_manager.utils import DialogUtils


class ToolModule(BaseModule):
    NAME = "tool"
    FRIENDLY_NAME = "Tools"

    async def install(
        self, tool_name: ToolType | None = typer.Argument(default=None)
    ) -> None:
        """Install the tools."""
        pass
        # if tool_name is not None:
        #     if tool_name not in self.config.tools:
        #         self.config.tools.append(tool_name)
        #         self.config.to_file()

        #     return await self._install_tool(tool_name)

        # for tool_type in self.config_module.config.tools:
        #     await self._install_tool(tool_type)

    async def _install_tool(self, tool_type: ToolType) -> None:
        """Install a specific tool."""
        match tool_type:
            case ToolType.DDRAWCOMPAT:
                tool = DDrawCompatTool(self.config)
                if not tool.is_installed:
                    await tool.install()
                    DialogUtils.tell(
                        self.config.app_mode,
                        f"{tool.FRIENDLY_NAME} has been installed successfully.",
                    )
                else:
                    DialogUtils.tell(
                        self.config.app_mode,
                        f"{tool.FRIENDLY_NAME} is already installed.",
                    )
            case _:
                DialogUtils.tell(
                    self.config.app_mode,
                    f"Tool {tool_type} is not supported.",
                )
