# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SistemaProExtreme.py'],
    pathex=[],
    binaries=[('matrix_effect.exe', '.')],
    datas=[('output.xml', '.')],
    hiddenimports=['wmi', 'win32com', 'win32com.client', 'pythoncom', 'comtypes', 'comtypes.client', 'pywintypes', 'win32api', 'win32con', 'GPUtil', 'cpuinfo'],
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
    name='SistemaProExtreme',
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
    name='SistemaProExtreme',
)
