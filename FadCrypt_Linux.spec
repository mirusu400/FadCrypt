# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import tkinterdnd2

# Get tkdnd library path
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

block_cipher = None

a = Analysis(
    ['FadCrypt_Linux.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),
        (tkdnd_path, 'tkinterdnd2/tkdnd'),
        ('ttkbootstrap', 'ttkbootstrap'),  # Include ttkbootstrap themes
    ],
    hiddenimports=[
        'tkinterdnd2',
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'pystray',
        'pystray._xorg',
        'pygame',
        'tkinterdnd2.TkinterDnD',
        'cryptography',
        'psutil',
        'watchdog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fadcrypt',  # Lowercase for Linux CLI convention
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
