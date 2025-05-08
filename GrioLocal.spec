# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

a = Analysis(
    ['src\\grio_main.py'],
    pathex=['S:\\HOME\\PROJETO_GRIO_LOCAL\\venv\\Lib\\site-packages'],
    binaries=[
        ('venv/Lib/site-packages/vosk/libgcc_s_seh-1.dll', 'vosk'),
        ('venv/Lib/site-packages/vosk/libstdc++-6.dll', 'vosk'),
        ('venv/Lib/site-packages/vosk/libvosk.dll', 'vosk'),
        ('venv/Lib/site-packages/vosk/libwinpthread-1.dll', 'vosk'),
        ('venv/Lib/site-packages/_sounddevice_data/portaudio-binaries/libportaudio64bit.dll', '.'),
        ('venv/Lib/site-packages/_sounddevice_data/portaudio-binaries/libportaudio64bit-asio.dll', '.')
    ] + collect_dynamic_libs('cffi'),
    datas=[
        ('config', 'config'),
        ('sons', 'sons'),
        ('modelos_vosk/vosk-model-small-pt-0.3', 'modelos_vosk/vosk-model-small-pt-0.3')
    ] + collect_data_files('cffi'),
    hiddenimports=['sounddevice', 'vosk', 'cffi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GrioLocal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GrioLocal',
)
