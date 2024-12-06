# -*- mode: python ; coding: utf-8 -*-
import os
import site
import tkinterdnd2

# Get tkdnd library path
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

block_cipher = None

a = Analysis(
    ['FadCrypt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),
        (tkdnd_path, 'tkinterdnd2/tkdnd'),  # Include tkdnd library files
    ],
    hiddenimports=[
        'tkinterdnd2',
        'ttkbootstrap',
        'PIL',
        'pystray',
        'pygame',
        'tkinterdnd2.TkinterDnD',
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

# Add tkdnd DLL files
for site_packages in site.getsitepackages():
    tkdnd_dll = os.path.join(site_packages, 'tkinterdnd2', 'tkdnd', 'tkdnd2.8')
    if os.path.exists(tkdnd_dll):
        a.datas += [(f'tkinterdnd2/tkdnd/{os.path.basename(f)}', f, 'DATA') 
                    for f in os.listdir(tkdnd_dll) 
                    if f.endswith('.dll')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FadCrypt',
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
    icon=['img/1.ico'],
)
