# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['d:\\drzqr\\Documents\\GitHub\\MarkerGUI\\main.py'],
    pathex=['d:\\drzqr\\Documents\\GitHub\\MarkerGUI\\src'],
    binaries=[],
    datas=[('d:\\drzqr\\Documents\\GitHub\\MarkerGUI\\config', 'config'), ('d:\\drzqr\\Documents\\GitHub\\MarkerGUI\\src\\markergui\\config', 'markergui/config')],
    hiddenimports=[],
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
    name='MarkerGUI',
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
    name='MarkerGUI',
)
