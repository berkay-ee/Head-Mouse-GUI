# -*- mode: python ; coding: utf-8 -*-
import mediapipe
import os

# Automatically finds the exact Mediapipe installation in your active environment
mediapipe_path = os.path.dirname(mediapipe.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # Grabs the ENTIRE mediapipe folder (not just modules) and bundles it safely
    datas=[(mediapipe_path, 'mediapipe')],
    hiddenimports=['mediapipe.solutions', 'mediapipe.solutions.face_mesh'],
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
    a.binaries,
    a.datas,
    [],
    name='HeadMouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:/Users/aydin/AppData/Local/Temp/e089d46d-67d2-4f77-b98b-6c257b75afdb',
)