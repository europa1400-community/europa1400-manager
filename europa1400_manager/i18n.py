"""User-facing texts in English and German. tr("key", name=value) formats with str.format."""

from __future__ import annotations

import locale
import os

LANGUAGES = {"en": "English", "de": "Deutsch"}

_language = "en"

TEXTS: dict[str, dict[str, str]] = {
    # --- errors and warnings (core) ---
    "error.download_http": {
        "en": "Download failed ({status}): {url}",
        "de": "Download fehlgeschlagen ({status}): {url}",
    },
    "error.download_too_large": {
        "en": "Download too large: {url}",
        "de": "Download zu groß: {url}",
    },
    "error.download_failed": {
        "en": "Download failed: {url} ({error})",
        "de": "Download fehlgeschlagen: {url} ({error})",
    },
    "error.download_checksum": {
        "en": "The download does not match its checksum and was discarded: {url}",
        "de": "Der Download passt nicht zu seiner Prüfsumme und wurde verworfen: {url}",
    },
    "error.archive_unsafe": {
        "en": "The archive contains an unsafe entry and was not used: {member}",
        "de": "Das Archiv enthält einen unsicheren Eintrag und wurde nicht verwendet: {member}",
    },
    "error.unsafe_path": {"en": "Unsafe path: {path}", "de": "Unsicherer Pfad: {path}"},
    "error.state_unreadable": {
        "en": "The manager's record in the game folder is damaged ({file}): {error}",
        "de": "Die Aufzeichnung des Managers im Spielordner ist beschädigt ({file}): {error}",
    },
    "warning.file_changed": {
        "en": "{path} was changed after the installation and was kept.",
        "de": "{path} wurde nach der Installation verändert und wurde behalten.",
    },
    "error.file_owned": {
        "en": "{path} belongs to the patch {owner}. Uninstall it first.",
        "de": "{path} gehört zum Patch {owner}. Deinstalliere ihn zuerst.",
    },
    "error.not_a_game_folder": {
        "en": "No Europa 1400 installation found in {path}.",
        "de": "In {path} wurde keine Europa-1400-Installation gefunden.",
    },
    "error.game_running": {
        "en": "The game is running. Close it first.",
        "de": "Das Spiel läuft. Beende es zuerst.",
    },
    "error.no_executable": {
        "en": "No game executable found in {path}.",
        "de": "Keine Spieldatei in {path} gefunden.",
    },
    "error.launch_failed": {
        "en": "{exe} could not be started: {error}",
        "de": "{exe} konnte nicht gestartet werden: {error}",
    },
    "error.not_writable": {
        "en": "The manager cannot write into {path}. Start the manager as administrator or move the game out of "
        "'Program Files'.",
        "de": "Der Manager kann nicht in {path} schreiben. Starte den Manager als Administrator oder verschiebe das "
        "Spiel aus 'Programme'.",
    },
    "error.patch_definition": {
        "en": "The database entry of {patch} is incomplete.",
        "de": "Der Datenbankeintrag von {patch} ist unvollständig.",
    },
    "error.not_an_archive": {
        "en": "The download of {patch} is no archive.",
        "de": "Der Download von {patch} ist kein Archiv.",
    },
    "error.archive_member": {
        "en": "{patch}: expected exactly one {file} in the archive, found {count}.",
        "de": "{patch}: im Archiv wurde genau eine Datei {file} erwartet, gefunden: {count}.",
    },
    "error.archive_layout": {
        "en": "{patch}: the archive does not contain {folder}.",
        "de": "{patch}: das Archiv enthält {folder} nicht.",
    },
    "error.unknown_patch": {
        "en": "Unknown patch: {patch}",
        "de": "Unbekannter Patch: {patch}",
    },
    "error.requirement_cycle": {
        "en": "The requirements of {patch} form a cycle.",
        "de": "Die Abhängigkeiten von {patch} bilden einen Kreis.",
    },
    "error.conflicts": {
        "en": "{patch} cannot be used together with: {others}. Uninstall them first.",
        "de": "{patch} kann nicht zusammen mit {others} verwendet werden. Deinstalliere diese zuerst.",
    },
    "error.required_by": {
        "en": "{patch} is needed by: {others}.",
        "de": "{patch} wird gebraucht von: {others}.",
    },
    "error.unmanaged_removal": {
        "en": "{patch} was not installed by the manager and cannot be removed automatically.",
        "de": "{patch} wurde nicht vom Manager installiert und kann nicht automatisch entfernt werden.",
    },
    "error.no_savegames": {
        "en": "There are no savegames yet.",
        "de": "Es gibt noch keine Spielstände.",
    },
    "progress.installing": {
        "en": "Installing {patch} ...",
        "de": "Installiere {patch} ...",
    },
    # --- game settings ---
    "settings.group.display": {"en": "Display", "de": "Anzeige"},
    "settings.group.sound": {"en": "Sound", "de": "Ton"},
    "settings.group.gameplay": {"en": "Gameplay", "de": "Spiel"},
    "settings.group.network": {"en": "Multiplayer", "de": "Mehrspieler"},
    "settings.monitor": {"en": "Monitor (Monitorfix)", "de": "Bildschirm (Monitorfix)"},
    "settings.monitor_off": {
        "en": "0 = off (all monitors)",
        "de": "0 = aus (alle Bildschirme)",
    },
    "settings.monitor_hint": {
        "en": "1 = main display, 2 = second monitor, ... After a game start {log} in the game folder lists the monitors and their numbers.",
        "de": "1 = Hauptbildschirm, 2 = zweiter Bildschirm, ... Nach einem Spielstart listet {log} im Spielordner die Bildschirme und ihre Nummern.",
    },
    "settings.display_mode": {"en": "Display mode", "de": "Bildmodus"},
    "settings.fullscreen": {"en": "Fullscreen", "de": "Vollbild"},
    "settings.window": {"en": "Window", "de": "Fenster"},
    "settings.show_intro": {"en": "Play intro", "de": "Intro abspielen"},
    "settings.music": {"en": "Music", "de": "Musik"},
    "settings.effects": {"en": "Sound effects", "de": "Soundeffekte"},
    "settings.weather_sound": {"en": "Weather sounds", "de": "Wettergeräusche"},
    "settings.master_volume": {"en": "Master volume", "de": "Gesamtlautstärke"},
    "settings.music_volume": {"en": "Music volume", "de": "Musiklautstärke"},
    "settings.effects_volume": {"en": "Effects volume", "de": "Effektlautstärke"},
    "settings.speech_volume": {"en": "Speech volume", "de": "Sprachlautstärke"},
    "settings.invert_mouse": {"en": "Invert mouse", "de": "Maus invertieren"},
    "settings.hints": {"en": "Hints", "de": "Hinweise"},
    "settings.cursor_text": {"en": "Text at the cursor", "de": "Text am Mauszeiger"},
    "settings.first_name": {"en": "First name", "de": "Vorname"},
    "settings.family_name": {"en": "Family name", "de": "Familienname"},
    "settings.host": {
        "en": "Host address (direct connection)",
        "de": "Host-Adresse (direkte Verbindung)",
    },
    "settings.port": {"en": "Port (TCP)", "de": "Port (TCP)"},
}


def system_language() -> str:
    for variable in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(variable)
        if value:
            return "de" if value.lower().startswith("de") else "en"
    try:
        code = locale.getlocale()[0] or ""
    except ValueError:
        code = ""
    return "de" if code.lower().startswith(("de", "german")) else "en"


def set_language(language: str | None) -> None:
    global _language
    _language = language if language in LANGUAGES else system_language()


def language() -> str:
    return _language


def tr(key: str, **values: object) -> str:
    entry = TEXTS.get(key)
    text = (entry.get(_language) or entry.get("en") or key) if entry else key
    return text.format(**values) if values else text


def add(texts: dict[str, dict[str, str]]) -> None:
    """Register more texts (the GUI keeps its own in europa1400_manager/gui/texts.py)."""
    TEXTS.update(texts)


def has(key: str) -> bool:
    return key in TEXTS
