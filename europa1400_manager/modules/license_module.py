import sys
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
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path(__file__).parent.parent

        license_file_path = base_path / "LICENSE.md"
        if license_file_path.exists():
            print(license_file_path.read_text(encoding="utf-8"))
        else:
            print(f"License file not found at {license_file_path!r}.")

    def _show_all_licenses(self) -> None:
        """Display both LICENSE.md and NOTICE.md, whether frozen or not."""
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path(__file__).parent.parent

        license_path = base_path / "LICENSE.md"
        notice_path = base_path / "NOTICE.md"

        if license_path.exists() and notice_path.exists():
            license_content = license_path.read_text(encoding="utf-8")
            notice_content = notice_path.read_text(encoding="utf-8")
            print(license_content)
            print("\n" + "=" * 40 + "\n")
            print(notice_content)
        else:
            print(f"Couldn't find LICENSE.md or NOTICE.md in {base_path!r}")
