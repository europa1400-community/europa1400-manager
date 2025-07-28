import sys
from pathlib import Path

from europa1400_manager.modules.base_module import BaseModule


class LicenseModule(BaseModule):
    NAME = "license"
    FRIENDLY_NAME = "License"

    def show(self, all: bool = False) -> None:
        """Display the license information."""
        licenses: str
        if all:
            licenses = self._get_all_licenses()
        else:
            licenses = self._get_license()
        print(licenses)

    def _get_license(self) -> str:
        """Return the license information for the game."""
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path()

        license_file_path = base_path / "LICENSE.md"
        if license_file_path.exists():
            return license_file_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"License file not found at {license_file_path!r}.")

    def _get_all_licenses(self) -> str:
        """Return both LICENSE.md and NOTICE.md, whether frozen or not."""
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            base_path = Path(meipass) if meipass else Path(".")
        else:
            base_path = Path()

        license_path = base_path / "LICENSE.md"
        notice_path = base_path / "NOTICE.md"

        if license_path.exists() and notice_path.exists():
            licenses = ""
            license_content = license_path.read_text(encoding="utf-8")
            notice_content = notice_path.read_text(encoding="utf-8")
            licenses += license_content
            licenses += "\n" + "=" * 40 + "\n"
            licenses += notice_content
            return licenses
        else:
            raise FileNotFoundError(
                f"Couldn't find LICENSE.md or NOTICE.md in {base_path!r}"
            )
