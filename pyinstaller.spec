block_cipher = None

# CLI Analysis
a_cli = Analysis(
    ['europa1400_manager/__main__.py'],
    # add your virtualenv’s site-packages so PyInstaller can see yaml
    pathex=[
        '.',
        r'..\\venv\\Lib\\site-packages'
    ],
    binaries=[],
    datas=[
        ('LICENSE.md', '.'),
        ('NOTICE.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'yaml',
        'yaml.loader',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# GUI Analysis
a_gui = Analysis(
    ['europa1400_manager/__main_gui__.py'],
    # add your virtualenv's site-packages so PyInstaller can see yaml
    pathex=[
        '.',
        r'..\\venv\\Lib\\site-packages'
    ],
    binaries=[],
    datas=[
        ('LICENSE.md', '.'),
        ('NOTICE.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'yaml',
        'yaml.loader',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# CLI PYZ
pyz_cli = PYZ(a_cli.pure, cipher=block_cipher)

# GUI PYZ
pyz_gui = PYZ(a_gui.pure, cipher=block_cipher)

# CLI EXE (console application)
exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    a_cli.binaries,
    a_cli.datas,
    [],
    name='europa1400-manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='64bit',
    codesign_identity=None,
    entitlements_file=None,
)

# GUI EXE (windowed application)
exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    a_gui.binaries,
    a_gui.datas,
    [],
    name='europa1400-manager-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='64bit',
    codesign_identity=None,
    entitlements_file=None,
)
