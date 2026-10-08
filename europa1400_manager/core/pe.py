"""Minimal PE reader: machine type and imported DLL names (enough to tell the game's renderer builds apart)."""

from __future__ import annotations

import struct
from pathlib import Path

MACHINE_I386 = 0x14C


def _rva_to_offset(sections: list[tuple[int, int, int, int]], rva: int) -> int | None:
    for virtual_address, virtual_size, raw_pointer, raw_size in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + (rva - virtual_address)
    return None


def imports(path: Path) -> tuple[int, set[str]] | None:
    """(machine, lower-case imported DLL names) or None if the file is no readable PE image."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    try:
        if data[:2] != b"MZ":
            return None
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe : pe + 4] != b"PE\0\0":
            return None
        machine, section_count = struct.unpack_from("<HH", data, pe + 4)
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        optional = pe + 24
        magic = struct.unpack_from("<H", data, optional)[0]
        directories = optional + (96 if magic == 0x10B else 112)
        import_rva = struct.unpack_from("<I", data, directories + 8)[0]
        sections = []
        table = optional + optional_size
        for index in range(section_count):
            entry = table + 40 * index
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
                "<IIII", data, entry + 8
            )
            sections.append((virtual_address, virtual_size, raw_pointer, raw_size))
        names: set[str] = set()
        offset = _rva_to_offset(sections, import_rva) if import_rva else None
        while offset is not None and offset + 20 <= len(data):
            name_rva = struct.unpack_from("<I", data, offset + 12)[0]
            if name_rva == 0:
                break
            name_offset = _rva_to_offset(sections, name_rva)
            if name_offset is not None:
                end = data.find(b"\0", name_offset, name_offset + 256)
                names.add(data[name_offset:end].decode("ascii", "replace").lower())
            offset += 20
        return machine, names
    except (struct.error, ValueError):
        return None


def renderer(path: Path) -> str | None:
    """ "d3d8" for the Direct3D 8 build, "dx6" for the DirectDraw build, None if unknown."""
    result = imports(path)
    if result is None:
        return None
    names = result[1]
    if "d3d8.dll" in names:
        return "d3d8"
    if "ddraw.dll" in names:
        return "dx6"
    return None
