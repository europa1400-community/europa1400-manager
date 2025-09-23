import asyncio
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.database import Database
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.info_module import InfoModule
from europa1400_manager.modules.overview_module import OverviewModule


@dataclass
class OverviewModuleGui(BaseModuleGui, OverviewModule):
    INDEX = 0
    FRIENDLY_NAME = "Overview"

    def __init__(
        self,
        config: Config,
        database: Database,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
        info_module: InfoModule,
    ) -> None:
        OverviewModule.__init__(self, config, database, info_module)
        BaseModuleGui.__init__(self, config, database, event_emitter, root, notebook)

        # Main container frame
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title section
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            title_frame,
            text="Europa 1400: The Guild",
            font=("Arial", 16, "bold"),
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Game Launcher",
            font=("Arial", 10),
        )
        subtitle_label.pack()

        # Game launch section
        launch_frame = ttk.LabelFrame(main_frame, text="Launch Game", padding="20")
        launch_frame.pack(fill="x", pady=(0, 20))

        # Center the buttons horizontally
        button_container = ttk.Frame(launch_frame)
        button_container.pack(anchor="center")

        # Main game button
        self.start_game_button = ttk.Button(
            button_container,
            text="Start Game",
            command=self._on_start_game_clicked,
            width=20,
        )
        self.start_game_button.pack(pady=5)

        # T&L game button
        self.start_game_tl_button = ttk.Button(
            button_container,
            text="Start Game (T&L)",
            command=self._on_start_game_tl_clicked,
            width=20,
        )
        self.start_game_tl_button.pack(pady=5)

        # Launch mode settings
        settings_frame = ttk.Frame(launch_frame)
        settings_frame.pack(fill="x", pady=(15, 0))

        # Game information section
        info_frame = ttk.LabelFrame(main_frame, text="Game Information", padding="15")
        info_frame.pack(fill="x")

        # Game path
        path_frame = ttk.Frame(info_frame)
        path_frame.pack(fill="x", pady=2)
        ttk.Label(path_frame, text="Game Path:", width=15, anchor="w").pack(side="left")
        self.game_path_value = ttk.Label(path_frame, text="", anchor="w")
        self.game_path_value.pack(side="left", fill="x", expand=True)

        # Status indicators
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill="x", pady=(10, 0))

        # Main executable status
        main_exe_frame = ttk.Frame(status_frame)
        main_exe_frame.pack(fill="x", pady=2)
        ttk.Label(main_exe_frame, text="Main Game:", width=15, anchor="w").pack(
            side="left"
        )
        self.main_exe_status = ttk.Label(
            main_exe_frame, text="", anchor="w", foreground="red"
        )
        self.main_exe_status.pack(side="left", fill="x", expand=True)

        # T&L executable status
        tl_exe_frame = ttk.Frame(status_frame)
        tl_exe_frame.pack(fill="x", pady=2)
        ttk.Label(tl_exe_frame, text="T&L Game:", width=15, anchor="w").pack(
            side="left"
        )
        self.tl_exe_status = ttk.Label(
            tl_exe_frame, text="", anchor="w", foreground="red"
        )
        self.tl_exe_status.pack(side="left", fill="x", expand=True)

    def _on_start_game_clicked(self) -> None:
        """Handle Start Game button click."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_game())

    def _on_start_game_tl_clicked(self) -> None:
        """Handle Start Game (T&L) button click."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_game_tl())

    def _update_gui(self) -> None:
        """Update the GUI elements for this module."""
        # Update game path
        self.game_path_value.config(text=str(self.config.game_path))

        # Check executable availability and update button states
        main_exe_path = self.info_module._executable_path
        tl_exe_path = self.info_module._tl_executable_path

        # Update main executable status
        if main_exe_path and main_exe_path.exists():
            self.main_exe_status.config(text="Available", foreground="green")
            self.start_game_button.config(state="normal")
        else:
            self.main_exe_status.config(text="Not Found", foreground="red")
            self.start_game_button.config(state="disabled")

        # Update T&L executable status
        if tl_exe_path and tl_exe_path.exists():
            self.tl_exe_status.config(text="Available", foreground="green")
            self.start_game_tl_button.config(state="normal")
        else:
            self.tl_exe_status.config(text="Not Found", foreground="red")
            self.start_game_tl_button.config(state="disabled")
