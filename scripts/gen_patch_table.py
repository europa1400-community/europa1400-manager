"""Generates patch-list.md, the list of patches currently in europa1400-database (fetched at build time).

The website is rebuilt daily, so the list follows the database without changes here. Without network access the page
says so instead of failing the build.
"""

from __future__ import annotations

import urllib.request
from typing import Any

import mkdocs_gen_files
import yaml

DATABASE = "https://raw.githubusercontent.com/europa1400-community/europa1400-database/master/data/"
TABLES = {"patch.yml": "third-party patch", "e1400patch.yml": "europa1400-patches"}
TYPES = {
    "simple": "single file",
    "archive": "files from an archive",
    "e1400patch_loader": "patch loader",
    "e1400patch_module": "loader patch",
}


def fetch(name: str) -> dict[str, Any]:
    with urllib.request.urlopen(DATABASE + name, timeout=30) as response:
        return yaml.safe_load(response.read().decode("utf-8"))


def table() -> str:
    lines = ["| Id | Name | Kind | Needs | Download |", "|---|---|---|---|---|"]
    for name, source in TABLES.items():
        for patch in fetch(name).get("elements") or []:
            needs = ", ".join(f"`{r}`" for r in patch.get("requires") or []) or "-"
            kind = TYPES.get(patch.get("type", ""), patch.get("type", ""))
            lines.append(
                f"| `{patch['id']}` | {patch.get('name', '')} | {kind} ({source}) | {needs} | [link]({patch.get('url', '')}) |"
            )
    return "\n".join(lines) + "\n"


try:
    content = table()
except Exception as error:  # no network while building locally
    content = f"!!! warning\n    The patch list could not be loaded from the database ({error}).\n"

HEADER = """# All patches in the database

Generated from [europa1400-database](https://github.com/europa1400-community/europa1400-database) when this website
was built (daily). What the patches do: [Patches](patches.md).

"""

with mkdocs_gen_files.open("patch-list.md", "w") as file:
    file.write(HEADER + content)
