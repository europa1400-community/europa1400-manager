# PyInstaller build of the two executables (`uv run pyinstaller pyinstaller.spec`):
#   europa1400-manager      command line, without Qt (small)
#   europa1400-manager-gui  window (PySide6, only the Qt modules the manager uses)
# The icon (build/icon.ico) is rendered from europa1400_manager/resources/icon.svg by scripts/make_icon.py.
import os
import sys

block_cipher = None

DATAS = [
    ("LICENSE.md", "."),
    ("NOTICE.md", "."),
    ("README.md", "."),
    ("europa1400_manager/resources", "europa1400_manager/resources"),
]
ICON = "build/icon.ico" if os.path.exists("build/icon.ico") and sys.platform == "win32" else None
QT_UNUSED = [
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtSql",
    "PySide6.QtTest", "PySide6.QtXml", "PySide6.QtDBus", "PySide6.QtConcurrent", "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets", "PySide6.QtPrintSupport", "PySide6.QtHelp", "PySide6.QtDesigner",
    "PySide6.QtUiTools", "PySide6.QtMultimedia", "PySide6.QtPdf", "PySide6.QtWebEngineCore",
]


def analysis(script, excludes):
    return Analysis(
        [script],
        pathex=["."],
        binaries=[],
        datas=DATAS,
        hiddenimports=["yaml", "yaml.loader", "platformdirs"],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=excludes + ["tkinter", "pytest"],
        noarchive=False,
        optimize=0,
    )


def executable(built, name, console):
    return EXE(
        PYZ(built.pure, cipher=block_cipher),
        built.scripts,
        built.binaries,
        built.datas,
        [],
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=console,
        disable_windowed_traceback=False,
        argv_emulation=False,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON,
    )


exe_cli = executable(analysis("europa1400_manager/__main__.py", ["PySide6", "shiboken6", "qasync"]), "europa1400-manager", True)
exe_gui = executable(analysis("europa1400_manager/__main_gui__.py", QT_UNUSED), "europa1400-manager-gui", False)
