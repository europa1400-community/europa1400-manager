import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import typer

from europa1400_manager.config import Config
from europa1400_manager.const import (
    DEFAULT_CONFIG_FILE_PATH,
    ENV_CONFIG_FILE_PATH,
    AppMode,
)
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.utils import DialogUtils, EnvUtils


class ConfigModule(BaseModule):
    NAME = "config"
    FRIENDLY_NAME = "Configuration"

    config_file_path: Path
    config: Config

    def __init__(self, app_mode: AppMode) -> None:
        super().__init__(app_mode)

        self.config_file_path = Path(
            EnvUtils.read(ENV_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_PATH)
        )

        if not self.config_file_path.exists():
            result = DialogUtils.ask_yes_no(
                self.app_mode,
                f"Configuration file at {self.config_file_path} not found. Initialize default configuration?",
            )

            if result:
                self.init()
            else:
                raise typer.Exit(code=1)

        self.config = Config.from_file(self.config_file_path)

    def init(
        self,
        game_path: Path | None = None,
    ) -> None:
        if game_path is None:
            while True:
                game_path = Path(
                    DialogUtils.ask(
                        self.app_mode,
                        "Please enter the path to the game directory:",
                        default=str(Path.home() / "Europa 1400"),
                    )
                )

                if self._validate_game_path(game_path):
                    break

        self.config = Config(game_path=game_path)
        self.config.to_file(self.config_file_path)

        DialogUtils.tell(
            self.app_mode,
            f"Configuration initialized with game path: {self.config.game_path}",
        )

    async def show(self) -> None:
        """Show the current configuration."""
        typer.echo(f"Current configuration: {self.config.to_json(indent=2)}")

    def _validate_game_path(self, game_path: Path) -> bool:
        """Validate the game path."""
        if not game_path.exists():
            DialogUtils.tell(self.app_mode, "Invalid game path. Please try again.")
            return False

        return True

    def _initialize_gui(self, root: tk.Tk, tab: ttk.Frame):
        """Initialize the GUI elements for the configuration module."""

        def auto_save_config() -> None:
            """Automatically save the configuration when any option changes."""
            # Update config with current values
            self.config.game_path = Path(game_path_var.get())

            # Save to file
            self.config.to_file(self.config_file_path)

        def reset_to_defaults_clicked() -> None:
            """Reset configuration to defaults."""
            result = DialogUtils.ask_yes_no(
                self.app_mode,
                "Are you sure you want to reset the configuration to defaults? This will delete the current configuration.",
                default=False,
            )

            if result:
                # Delete the current config file
                if self.config_file_path.exists():
                    self.config_file_path.unlink()

                # Reinitialize with defaults
                self.init()

                # Update the display
                update_all_fields()

        def browse_game_path() -> None:
            """Browse for game path directory."""
            selected_path = filedialog.askdirectory(
                title="Select Europa 1400 Game Directory",
                initialdir=str(self.config.game_path)
                if self.config.game_path.exists()
                else str(Path.home()),
            )
            if selected_path:
                game_path_var.set(selected_path)
                auto_save_config()  # Auto-save when path changes

        def on_game_path_changed(*args) -> None:
            """Called when game path entry is modified."""
            auto_save_config()

        def update_all_fields():
            """Update all field values in the GUI."""
            # Update game path
            game_path_var.set(str(self.config.game_path))

        # Variables to hold the configuration values
        game_path_var = tk.StringVar()

        # Add trace to auto-save when game path changes
        game_path_var.trace_add("write", on_game_path_changed)

        # Top row with reset button
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill="x", pady=(0, 10))
        reset_button = ttk.Button(
            top_frame, text="Reset to Defaults", command=reset_to_defaults_clicked
        )
        reset_button.pack(side="right", padx=(5, 0))

        # Main content frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(expand=True, fill="both")

        # Game Path section
        path_frame = ttk.LabelFrame(main_frame, text="Game Configuration", padding="10")
        path_frame.pack(fill="x", pady=(0, 10))

        # Game Path
        game_path_frame = ttk.Frame(path_frame)
        game_path_frame.pack(fill="x", pady=2)
        ttk.Label(game_path_frame, text="Game Path:", width=15, anchor="w").pack(
            side="left"
        )
        game_path_entry = ttk.Entry(game_path_frame, textvariable=game_path_var)
        game_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_button = ttk.Button(
            game_path_frame, text="Browse...", command=browse_game_path
        )
        browse_button.pack(side="right")

        # Initialize all field values
        update_all_fields()
