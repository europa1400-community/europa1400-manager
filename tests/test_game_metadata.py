import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest

from europa1400_manager.game_metadata import GameMetadata
from europa1400_manager.const import (
    GameEdition,
    GameLanguage,
    EUROPA1400_EXE_PATH,
    EUROPA1400_GOLD_EXE_PATH,
    EUROPA1400_TL_EXE_PATH,
    EUROPA1400_GOLD_TL_EXE_PATH,
    GILDE_EXE_PATH,
    GILDE_GOLD_EXE_PATH,
    GILDE_TL_EXE_PATH,
    GILDE_GOLD_TL_EXE_PATH,
)


@pytest.mark.parametrize(
    "edition,language,exp_exe,exp_tl",
    [
        (GameEdition.STANDARD, GameLanguage.ENGLISH, EUROPA1400_EXE_PATH, EUROPA1400_TL_EXE_PATH),
        (GameEdition.STANDARD, GameLanguage.GERMAN, GILDE_EXE_PATH, GILDE_TL_EXE_PATH),
        (GameEdition.GOLD, GameLanguage.ENGLISH, EUROPA1400_GOLD_EXE_PATH, EUROPA1400_GOLD_TL_EXE_PATH),
        (GameEdition.GOLD, GameLanguage.GERMAN, GILDE_GOLD_EXE_PATH, GILDE_GOLD_TL_EXE_PATH),
    ],
)
def test_executable_paths(edition, language, exp_exe, exp_tl):
    meta = GameMetadata(edition=edition, language=language)
    assert meta.executable_path == Path(exp_exe)
    assert meta.tl_executable_path == Path(exp_tl)
