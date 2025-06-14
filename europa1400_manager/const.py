from enum import StrEnum

from aenum import MultiValueEnum

ENV_CONFIG_FILE_PATH = "CONFIG_FILE_PATH"

DEFAULT_CONFIG_FILE_PATH = "config.yml"


class AppMode(StrEnum):
    CLI = "cli"
    GUI = "gui"


class ToolType(StrEnum):
    DDRAWCOMPAT = "ddrawcompat"


class GameEdition(MultiValueEnum):
    STANDARD = "standard", "Standard Edition"
    GOLD = "gold", "Gold Edition"


class GameLanguage(MultiValueEnum):
    ENGLISH = "en", "English"
    GERMAN = "de", "German"
    RUSSIAN = "ru", "Russian"


class GameVersion(MultiValueEnum):
    VERSION_1_01 = "v1.01", "Version 1.01"
    VERSION_1_02 = "v1.02", "Version 1.02"
    VERSION_1_03b = "v1.03b", "Version 1.03b"
    VERSION_1_04 = "v1.04", "Version 1.04"
    VERSION_1_05b = "v1.05b", "Version 1.05b"
    VERSION_2_01 = "v2.01", "Version 2.01"
    VERSION_2_02 = "v2.02", "Version 2.02"
    VERSION_2_03 = "v2.03", "Version 2.03"
    VERSION_2_04 = "v2.04", "Version 2.04"
    VERSION_2_05 = "v2.05", "Version 2.05"
    VERSION_2_06 = "v2.06", "Version 2.06"


class GameDistribution(MultiValueEnum):
    STEAM = "steam", "Steam"
    GOG = "gog", "GOG"
    RETAIL = "retail", "Retail"


class GameDrm(MultiValueEnum):
    NONE = "none", "None"
    STEAM = "steam", "Steam"
    SECUROM_4 = "securom4", "SecuROM 4"


GILDE_EXE_PATH = "Gilde.exe"
GILDE_GOLD_EXE_PATH = "GildeGold.exe"
EUROPA1400_EXE_PATH = "Europa1400.exe"
EUROPA1400_GOLD_EXE_PATH = "Europa1400Gold.exe"

GILDE_TL_EXE_PATH = "Gilde_TL.exe"
GILDE_GOLD_TL_EXE_PATH = "GildeGold_TL.exe"
EUROPA1400_TL_EXE_PATH = "Europa1400_TL.exe"
EUROPA1400_GOLD_TL_EXE_PATH = "Europa1400Gold_TL.exe"
