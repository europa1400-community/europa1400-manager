block_cipher = None

a = Analysis(
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

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
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
