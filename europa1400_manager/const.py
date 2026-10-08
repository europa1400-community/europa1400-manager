from enum import StrEnum, auto

ENV_CONFIG_FILE_PATH = "CONFIG_FILE_PATH"
ENV_DATABASE_REPOSITORY_URL = "DATABASE_REPOSITORY_URL"
ENV_DATABASE_REPOSITORY_BRANCH = "DATABASE_REPOSITORY_BRANCH"
ENV_DATABASE_FILES_BASE_PATH = "DATABASE_FILES_BASE_PATH"


DEFAULT_CONFIG_FILE_PATH = "config.yml"
DEFAULT_DATABASE_REPOSITORY_URL = "https://raw.githubusercontent.com/europa1400-community/europa1400-database/refs/heads/"
DEFAULT_DATABASE_REPOSITORY_BRANCH = "master"
DEFAULT_DATABASE_FILES_BASE_PATH = "data"


class AppMode(StrEnum):
    CLI = "cli"
    GUI = "gui"


class PatchType(StrEnum):
    SIMPLE = auto()
    ARCHIVE = auto()
    # europa1400-patches: the loader (e1400patch/) and its patch modules (patches/<id>/)
    E1400PATCH_LOADER = auto()
    E1400PATCH_MODULE = auto()


EVENT_UPDATE_ALL_MODULES = "update_all_modules"
