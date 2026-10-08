"""Texts of the window (English, German)."""

from __future__ import annotations

from europa1400_manager import i18n


def _t(en: str, de: str) -> dict[str, str]:
    return {"en": en, "de": de}


TEXTS = {
    # navigation and pages
    "ui.home": _t("Home", "Start"),
    "ui.welcome": _t("Welcome", "Willkommen"),
    "ui.patches": _t("Patches", "Patches"),
    "ui.patches_subtitle": _t(
        "Fixes and improvements from the community. Everything can be removed again; files a patch replaces are restored.",
        "Fixes und Verbesserungen aus der Community. Alles lässt sich wieder entfernen; ersetzte Dateien werden "
        "wiederhergestellt.",
    ),
    "ui.game_settings": _t("Game settings", "Spieleinstellungen"),
    "ui.game_settings_subtitle": _t(
        "Settings from game.ini. Change them here instead of in the game when it does not start.",
        "Einstellungen aus der game.ini. Ändere sie hier, wenn das Spiel zum Beispiel nicht mehr startet.",
    ),
    "ui.savegames": _t("Savegames", "Spielstände"),
    "ui.savegames_subtitle": _t(
        "Back up your savegames before trying patches or mods.",
        "Sichere deine Spielstände, bevor du Patches oder Mods ausprobierst.",
    ),
    "ui.manager_settings": _t("Manager", "Manager"),
    "ui.about": _t("About", "Über"),
    # general
    "ui.error": _t("Problem", "Problem"),
    "ui.unexpected_error": _t(
        "Something went wrong: {error}\n\nDetails are in the log (Manager → Log folder).",
        "Etwas ist schiefgelaufen: {error}\n\nDetails stehen im Log (Manager → Log-Ordner).",
    ),
    "ui.loading_database": _t("Loading patch database ...", "Lade Patch-Datenbank ..."),
    "ui.identifying": _t("Identifying the game ...", "Erkenne das Spiel ..."),
    "ui.use": _t("Use", "Verwenden"),
    "ui.browse": _t("Choose folder ...", "Ordner wählen ..."),
    "ui.open": _t("Open", "Öffnen"),
    "ui.save": _t("Save", "Speichern"),
    "ui.discard": _t("Discard changes", "Änderungen verwerfen"),
    "ui.reload": _t("Reload", "Neu laden"),
    "ui.later": _t("Later", "Später"),
    "ui.quit": _t("Quit", "Beenden"),
    "ui.quit_busy": _t(
        "The manager is still working. Quit anyway? (An interrupted installation is rolled back at the next start.)",
        "Der Manager arbeitet noch. Trotzdem beenden?",
    ),
    "ui.no_game_selected": _t("No game selected", "Kein Spiel ausgewählt"),
    # home
    "ui.choose_game": _t("Choose your game", "Wähle dein Spiel"),
    "ui.choose_game_hint": _t(
        "These installations of Europa 1400 / Die Gilde were found. You can change the folder later.",
        "Diese Installationen von Die Gilde / Europa 1400 wurden gefunden. Den Ordner kannst du später ändern.",
    ),
    "ui.nothing_found": _t(
        "No installation found automatically. Choose the folder that contains game.ini.",
        "Keine Installation automatisch gefunden. Wähle den Ordner, in dem die game.ini liegt.",
    ),
    "ui.guessed": _t(
        "Guessed from the installation", "Aus der Installation geschlossen"
    ),
    "ui.exact": _t("Identified exactly by checksum", "Exakt per Prüfsumme erkannt"),
    "ui.known_build": _t("Known version", "Bekannte Version"),
    "ui.unknown_build": _t("Unknown version", "Unbekannte Version"),
    "ui.known_build_hint": _t(
        "This exact game version is in the database.",
        "Genau diese Spielversion ist in der Datenbank.",
    ),
    "ui.unknown_build_hint": _t(
        "This game version is not in the database yet; patches may not fit. Please report it.",
        "Diese Spielversion ist noch nicht in der Datenbank; Patches passen eventuell nicht. Bitte melde sie.",
    ),
    "ui.play": _t("Play", "Spielen"),
    "ui.play_dx6": _t("Classic renderer", "Klassischer Renderer"),
    "ui.play_d3d8_hint": _t(
        "Starts {exe} (Direct3D 8, recommended)",
        "Startet {exe} (Direct3D 8, empfohlen)",
    ),
    "ui.play_dx6_hint": _t("Starts {exe} (DirectX 6)", "Startet {exe} (DirectX 6)"),
    "ui.open_folder": _t("Game folder", "Spielordner"),
    "ui.paths_wrong": _t(
        "game.ini points to another folder ({keys}). The game was probably moved or copied.",
        "Die game.ini zeigt auf einen anderen Ordner ({keys}). Das Spiel wurde vermutlich verschoben oder kopiert.",
    ),
    "ui.repair": _t("Repair", "Reparieren"),
    "ui.offline": _t(
        "Offline: the patch list is from the last start.",
        "Offline: Die Patch-Liste stammt vom letzten Start.",
    ),
    "ui.no_database": _t(
        "The patch database could not be loaded. Check the internet connection.",
        "Die Patch-Datenbank konnte nicht geladen werden. Prüfe die Internetverbindung.",
    ),
    "ui.patch_summary": _t(
        "{installed} of {total} patches installed",
        "{installed} von {total} Patches installiert",
    ),
    "ui.updates_available": _t(
        "Updates available: {names}", "Updates verfügbar: {names}"
    ),
    "ui.manage_patches": _t("Manage patches", "Patches verwalten"),
    # recommendations
    "ui.recommended_setup": _t("Recommended setup", "Empfohlene Einrichtung"),
    "ui.recommended_hint": _t(
        "Fixes and settings the community recommends for your game version. Choose and apply with one click.",
        "Fixes und Einstellungen, die die Community für deine Spielversion empfiehlt. Auswählen und mit einem Klick "
        "einrichten.",
    ),
    "ui.recommended_complete": _t(
        "Everything recommended for your game version is set up.",
        "Alles Empfohlene für deine Spielversion ist eingerichtet.",
    ),
    "ui.level_recommended": _t("Recommended", "Empfohlen"),
    "ui.level_optional": _t("Optional", "Optional"),
    "ui.already_done": _t("already set up", "schon eingerichtet"),
    "ui.apply_selected": _t("Set up selected", "Ausgewählte einrichten"),
    "ui.applying": _t("Setting up ...", "Richte ein ..."),
    "ui.recommended_applied": _t(
        "Done. You can start the game.", "Fertig. Du kannst das Spiel starten."
    ),
    "ui.recommended_chip_hint": _t(
        "Recommended for your game version", "Für deine Spielversion empfohlen"
    ),
    "ui.on": _t("on", "an"),
    "ui.off": _t("off", "aus"),
    # patches
    "ui.search": _t("Search ...", "Suchen ..."),
    "ui.all_categories": _t("All categories", "Alle Kategorien"),
    "ui.only_compatible": _t(
        "Only patches for my version", "Nur Patches für meine Version"
    ),
    "ui.no_patches_match": _t(
        "No patch matches the filter.", "Kein Patch passt zum Filter."
    ),
    "ui.installed": _t("Installed", "Installiert"),
    "ui.update_available": _t(
        "Update (installed: {version})", "Update (installiert: {version})"
    ),
    "ui.unmanaged": _t("Present", "Vorhanden"),
    "ui.unmanaged_hint": _t(
        "The files are there, but were not installed by this manager (by hand, by the store or by an older manager).",
        "Die Dateien sind da, wurden aber nicht von diesem Manager installiert (von Hand, vom Store oder von einem "
        "älteren Manager).",
    ),
    "ui.not_for_this_game": _t("Not for this version", "Nicht für diese Version"),
    "ui.not_for_this_game_hint": _t(
        "The database lists this patch for other game versions.",
        "Laut Datenbank ist der Patch für andere Spielversionen.",
    ),
    "ui.fits": _t("Fits", "Passt"),
    "ui.fits_hint": _t(
        "Made for your game version.", "Für deine Spielversion gemacht."
    ),
    "ui.requires": _t("Needs {names}", "Braucht {names}"),
    "ui.conflicts_with": _t("Not together with {names}", "Nicht zusammen mit {names}"),
    "ui.needed_by": _t("Needed by {names}", "Gebraucht von {names}"),
    "ui.author": _t("By {name}", "Von {name}"),
    "ui.install": _t("Install", "Installieren"),
    "ui.update": _t("Update", "Aktualisieren"),
    "ui.reinstall": _t("Take over", "Übernehmen"),
    "ui.reinstall_hint": _t(
        "Installs the current version through the manager; the present files are backed up and restored on uninstall.",
        "Installiert die aktuelle Version über den Manager; die vorhandenen Dateien werden gesichert und beim "
        "Deinstallieren wiederhergestellt.",
    ),
    "ui.uninstall": _t("Uninstall", "Deinstallieren"),
    "ui.homepage": _t("Website", "Webseite"),
    "ui.install_incompatible": _t(
        "{name} is not meant for your game version. Install anyway?",
        "{name} ist nicht für deine Spielversion gedacht. Trotzdem installieren?",
    ),
    "ui.install_with": _t(
        "{name} needs {others}. Install them too?",
        "{name} braucht {others}. Mit installieren?",
    ),
    "ui.uninstall_confirm": _t("Uninstall {name}?", "{name} deinstallieren?"),
    "ui.uninstall_dependents": _t(
        "{others} need {name} and will be uninstalled too. Continue?",
        "{others} brauchen {name} und werden mit deinstalliert. Fortfahren?",
    ),
    "ui.uninstalling": _t("Uninstalling {patch} ...", "Deinstalliere {patch} ..."),
    # game settings
    "ui.no_game_ini": _t(
        "game.ini not found in the game folder.",
        "Keine game.ini im Spielordner gefunden.",
    ),
    "ui.all_values": _t("All values (advanced)", "Alle Werte (fortgeschritten)"),
    "ui.all_values_hint": _t(
        "Every value of game.ini. Only change what you know; a backup of the original file is kept.",
        "Alle Werte der game.ini. Ändere nur, was du kennst; eine Sicherung der Originaldatei bleibt erhalten.",
    ),
    "ui.section": _t("Section", "Abschnitt"),
    "ui.key": _t("Key", "Schlüssel"),
    "ui.value": _t("Value", "Wert"),
    "ui.open_game_ini": _t("Open game.ini", "game.ini öffnen"),
    "ui.nothing_changed": _t("Nothing changed.", "Nichts geändert."),
    "ui.saved": _t("{count} value(s) saved.", "{count} Wert(e) gespeichert."),
    "ui.game_ini_backup": _t(
        "The original game.ini is kept as {name} in the game folder.",
        "Die ursprüngliche game.ini liegt als {name} im Spielordner.",
    ),
    # savegames
    "ui.name": _t("Name", "Name"),
    "ui.kind": _t("Kind", "Art"),
    "ui.modified": _t("Saved", "Gespeichert"),
    "ui.size": _t("Size", "Größe"),
    "ui.multiplayer": _t("Multiplayer", "Mehrspieler"),
    "ui.single_player": _t("Single player", "Einzelspieler"),
    "ui.backup_now": _t("Back up now", "Jetzt sichern"),
    "ui.restore": _t("Restore ...", "Wiederherstellen ..."),
    "ui.restore_this": _t("Restore", "Wiederherstellen"),
    "ui.open_save_folder": _t("Savegame folder", "Spielstand-Ordner"),
    "ui.open_backup_folder": _t("Backup folder", "Sicherungsordner"),
    "ui.backups": _t("Backups", "Sicherungen"),
    "ui.no_backups": _t("No backups yet.", "Noch keine Sicherungen."),
    "ui.backing_up": _t("Backing up savegames ...", "Sichere Spielstände ..."),
    "ui.backup_done": _t("Saved to {path}", "Gesichert in {path}"),
    "ui.restore_confirm": _t(
        "Restore the savegames from {name}? Your current savegames are backed up first.",
        "Spielstände aus {name} wiederherstellen? Deine aktuellen Spielstände werden vorher gesichert.",
    ),
    "ui.restoring": _t("Restoring savegames ...", "Stelle Spielstände wieder her ..."),
    "ui.restored": _t(
        "{count} savegame(s) restored.",
        "{count} Spielstand/Spielstände wiederhergestellt.",
    ),
    # manager settings
    "ui.game_folder": _t("Game folder", "Spielordner"),
    "ui.game_folder_hint": _t(
        "Several installations? Switch between them here.",
        "Mehrere Installationen? Hier wechselst du zwischen ihnen.",
    ),
    "ui.general": _t("General", "Allgemein"),
    "ui.language": _t("Language", "Sprache"),
    "ui.system_language": _t("System language", "Systemsprache"),
    "ui.restart_for_language": _t(
        "The language changes at the next start of the manager.",
        "Die Sprache ändert sich beim nächsten Start.",
    ),
    "ui.check_updates": _t(
        "Check for new manager versions at start",
        "Beim Start nach neuen Manager-Versionen suchen",
    ),
    "ui.database": _t("Patch database", "Patch-Datenbank"),
    "ui.db_state": _t("State", "Stand"),
    "ui.db_online": _t("Database up to date", "Datenbank aktuell"),
    "ui.db_cache": _t("Offline (saved database)", "Offline (gespeicherte Datenbank)"),
    "ui.db_local": _t("Local database (development)", "Lokale Datenbank (Entwicklung)"),
    "ui.db_none": _t("No database", "Keine Datenbank"),
    "ui.db_branch": _t("Branch", "Branch"),
    "ui.db_branch_hint": _t(
        "For testers: load the database from another branch of europa1400-database.",
        "Für Tester: Datenbank aus einem anderen Branch von europa1400-database laden.",
    ),
    "ui.files": _t("Files", "Dateien"),
    "ui.log_folder": _t("Log folder", "Log-Ordner"),
    "ui.settings_folder": _t("Settings folder", "Einstellungsordner"),
    "ui.cache": _t("Downloads", "Downloads"),
    "ui.clear_cache": _t("Delete downloaded files", "Heruntergeladene Dateien löschen"),
    "ui.cache_cleared": _t(
        "Downloaded files deleted.", "Heruntergeladene Dateien gelöscht."
    ),
    # about
    "ui.about_text": _t(
        "Installs community patches and fixes for Europa 1400: The Guild (Die Gilde), manages game settings and "
        "savegames. Made by the Europa 1400 community, free and open source (MIT).",
        "Installiert Community-Patches und Fixes für Die Gilde (Europa 1400), verwaltet Spieleinstellungen und "
        "Spielstände. Von der Europa-1400-Community, frei und quelloffen (MIT).",
    ),
    "ui.website": _t("Help", "Hilfe"),
    "ui.source": _t("Source code", "Quellcode"),
    "ui.report_problem": _t("Report a problem", "Problem melden"),
    "ui.discord": _t("Discord", "Discord"),
    "ui.licenses": _t("Licenses", "Lizenzen"),
    "ui.qt_notice": _t(
        "The window uses Qt for Python (PySide6) under the LGPL v3; its source is available at "
        "https://code.qt.io/cgit/pyside/pyside-setup.git.",
        "Das Fenster nutzt Qt for Python (PySide6) unter der LGPL v3; der Quellcode ist unter "
        "https://code.qt.io/cgit/pyside/pyside-setup.git verfügbar.",
    ),
    "ui.licenses_missing": _t(
        "License files not found.", "Lizenzdateien nicht gefunden."
    ),
    # updates
    "ui.update_title": _t("New version", "Neue Version"),
    "ui.update_text": _t(
        "Europa 1400 Manager {version} is available (you have {current}).",
        "Europa 1400 Manager {version} ist verfügbar (du hast {current}).",
    ),
    "ui.update_download": _t("Download", "Herunterladen"),
    "ui.update_skip": _t("Skip this version", "Diese Version überspringen"),
    # game metadata (database ids)
    "meta.edition.standard": _t("Standard edition", "Standard-Edition"),
    "meta.edition.gold": _t("Gold Edition", "Gold-Edition"),
    "meta.language.de": _t("German", "Deutsch"),
    "meta.language.en": _t("English", "Englisch"),
    "meta.language.ru": _t("Russian", "Russisch"),
    "meta.distribution.gog": _t("GOG", "GOG"),
    "meta.distribution.steam": _t("Steam", "Steam"),
    "meta.distribution.retail": _t("CD/DVD", "CD/DVD"),
    "meta.drm.steam": _t("Steam DRM", "Steam-DRM"),
    "meta.drm.securom": _t("SecuROM", "SecuROM"),
    # categories
    "category.multiplayer": _t("Multiplayer", "Mehrspieler"),
    "category.graphics": _t("Graphics", "Grafik"),
    "category.compatibility": _t("Compatibility", "Kompatibilität"),
    "category.gameplay": _t("Gameplay", "Spielmechanik"),
    "category.tools": _t("Tools", "Werkzeuge"),
    "category.other": _t("Other", "Sonstiges"),
}


def register() -> None:
    i18n.add(TEXTS)
