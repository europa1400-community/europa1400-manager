from enum import StrEnum

ENV_CONFIG_FILE_PATH = "CONFIG_FILE_PATH"

DEFAULT_CONFIG_FILE_PATH = "config.yml"


class AppMode(StrEnum):
    CLI = "cli"
    GUI = "gui"


class PatchType(StrEnum):
    DDRAWCOMPAT = "ddrawcompat"


class GameEdition(StrEnum):
    STANDARD = "standard"
    GOLD = "gold"


class GameLanguage(StrEnum):
    ENGLISH = "en"
    GERMAN = "de"
    RUSSIAN = "ru"


class GameVersion(StrEnum):
    VERSION_1_01 = "v1.01"
    VERSION_1_02 = "v1.02"
    VERSION_1_03b = "v1.03b"
    VERSION_1_04 = "v1.04"
    VERSION_1_05b = "v1.05b"
    VERSION_2_01 = "v2.01"
    VERSION_2_02 = "v2.02"
    VERSION_2_03 = "v2.03"
    VERSION_2_04 = "v2.04"
    VERSION_2_05 = "v2.05"
    VERSION_2_06 = "v2.06"


class GameDistribution(StrEnum):
    STEAM = "steam"
    GOG = "gog"
    RETAIL = "retail"


class GameDrm(StrEnum):
    NONE = "none"
    STEAM = "steam"
    SECUROM_4 = "securom4"


GILDE_EXE_PATH = "Gilde.exe"
GILDE_GOLD_EXE_PATH = "GildeGold.exe"
EUROPA1400_EXE_PATH = "Europa1400.exe"
EUROPA1400_GOLD_EXE_PATH = "Europa1400Gold.exe"

GILDE_TL_EXE_PATH = "Gilde_TL.exe"
GILDE_GOLD_TL_EXE_PATH = "GildeGold_TL.exe"
EUROPA1400_TL_EXE_PATH = "Europa1400_TL.exe"
EUROPA1400_GOLD_TL_EXE_PATH = "Europa1400Gold_TL.exe"

EVENT_UPDATE_ALL_MODULES = "update_all_modules"
