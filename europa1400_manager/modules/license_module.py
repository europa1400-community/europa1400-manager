from pathlib import Path

from europa1400_manager.const import AppMode
from europa1400_manager.modules.base_module import BaseModule


class LicenseModule(BaseModule):
    NAME = "license"
    FRIENDLY_NAME = "License"

    def __init__(self, app_mode: AppMode) -> None:
        super().__init__(app_mode)

    def show(self, all: bool = False) -> None:
        """Display the license information."""
        if all:
            self._show_all_licenses()
        else:
            self._show_license()

    def _show_license(self) -> None:
        """Display the license information for the game."""
        license_file_path = Path("LICENSE.md")
        if license_file_path.exists():
            with license_file_path.open(encoding="utf-8") as file:
                license_content = file.read()
            print(license_content)
        else:
            print("License file not found.")

    def _show_all_licenses(self) -> None:
        # Display the license information for all components.
        # use license.md contents and then notice.md contents, all in a single dialog tell
        license_file_path = Path("LICENSE.md")
        notice_file_path = Path("NOTICE.md")
        if license_file_path.exists() and notice_file_path.exists():
            with license_file_path.open(encoding="utf-8") as license_file:
                license_content = license_file.read()
            with notice_file_path.open(encoding="utf-8") as notice_file:
                notice_content = notice_file.read()
            print(license_content)
            print("\n" + "=" * 40 + "\n")
            print(notice_content)
        else:
            print("License or notice file not found.")
