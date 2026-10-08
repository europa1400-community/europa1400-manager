"""Line based access to Windows INI files that keeps everything else of the file as it is.

The game reads game.ini with the Windows profile API: keys and sections are case-insensitive, quotes around values are
stripped, the file is in the ANSI code page. Comments, order, spelling and line endings are kept on writing; a write
goes to a temporary file first and replaces the original atomically.
"""

from __future__ import annotations

from pathlib import Path

ENCODING = "cp1252"


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding=ENCODING, errors="replace", newline="").splitlines(
        keepends=True
    )


def _section_of(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("[") and "]" in stripped:
        return stripped[1 : stripped.index("]")].strip().lower()
    return None


def _key_of(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped[0] in ";#" or "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip().lower()


def _value_of(line: str) -> str:
    value = line.split("=", 1)[1].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def get(path: Path, section: str, key: str) -> str | None:
    """Value of a key (surrounding quotes removed), None when missing."""
    current = None
    for line in _read_lines(path):
        name = _section_of(line)
        if name is not None:
            current = name
        elif current == section.lower() and _key_of(line) == key.lower():
            return _value_of(line)
    return None


def read_all(path: Path) -> dict[str, dict[str, str]]:
    """All values as {section: {key: value}} with lower-case section and key names (first occurrence wins)."""
    result: dict[str, dict[str, str]] = {}
    current = None
    for line in _read_lines(path):
        name = _section_of(line)
        if name is not None:
            current = name
            result.setdefault(current, {})
        elif current is not None and (key := _key_of(line)) is not None:
            result[current].setdefault(key, _value_of(line))
    return result


def set_values(path: Path, changes: dict[tuple[str, str], str | None]) -> None:
    """Set several (section, key) -> value at once; None removes a key. Missing sections and keys are added."""
    lines = _read_lines(path)
    for (section, key), value in changes.items():
        lines = _set_in_lines(lines, section, key, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        "".join(lines), encoding=ENCODING, errors="replace", newline=""
    )
    temporary.replace(path)


def set_value(path: Path, section: str, key: str, value: str | None) -> None:
    set_values(path, {(section, key): value})


def _set_in_lines(
    lines: list[str], section: str, key: str, value: str | None
) -> list[str]:
    newline = "\r\n" if not lines or lines[0].endswith("\r\n") else "\n"
    wanted = section.lower()
    current, section_end, done = None, None, False
    result: list[str] = []
    for line in lines:
        name = _section_of(line)
        if name is not None:
            if current == wanted and not done and value is not None:
                insert_at = section_end if section_end is not None else len(result)
                result.insert(insert_at, f"{key}={value}{newline}")
                done = True
            current = name
        elif current == wanted and _key_of(line) == key.lower():
            if value is not None and not done:
                ending = (
                    "\r\n"
                    if line.endswith("\r\n")
                    else ("\n" if line.endswith("\n") else "")
                )
                original_key = line.split("=", 1)[0].strip()
                result.append(f"{original_key}={value}{ending or newline}")
                done = True
            continue
        result.append(line)
        if current == wanted and line.strip():
            section_end = len(result)
    if value is not None and not done:
        if section_end is not None:
            result.insert(section_end, f"{key}={value}{newline}")
        else:
            if result and not result[-1].endswith(("\n", "\r\n")):
                result[-1] += newline
            result.append(f"[{section}]{newline}")
            result.append(f"{key}={value}{newline}")
    return result
