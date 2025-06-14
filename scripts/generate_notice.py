#!/usr/bin/env python3
"""
Wrapper: on Windows invoke the PS1, otherwise invoke the shell script.
Falls back to powershell.exe if pwsh isn’t installed.
"""

import os
import platform
import shutil
import subprocess
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    if platform.system() == "Windows":
        # look for pwsh (PowerShell Core), else powershell.exe (Windows PowerShell)
        exe = shutil.which("pwsh") or shutil.which("powershell")
        if not exe:
            print(
                "Error: neither pwsh nor powershell was found on PATH", file=sys.stderr
            )
            return 1

        ps1 = os.path.join(here, "generate_notice.ps1")
        cmd = [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1]

    else:
        sh = os.path.join(here, "generate_notice.sh")
        # make sure it’s executable (chmod +x) or call via sh
        if not os.access(sh, os.X_OK):
            # fall back to invoking via bash
            cmd = ["bash", sh]
        else:
            cmd = [sh]

    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
