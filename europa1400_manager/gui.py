from europa1400_manager.modules.base_module import BaseModule


class Gui:
    def __init__(self, modules: list[BaseModule]) -> None:
        self.modules = modules

    def run(self) -> None:
        raise NotImplementedError("GUI functionality is not implemented yet.")
