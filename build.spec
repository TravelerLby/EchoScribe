# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Use version from _version.py
sys.path.insert(0, os.path.join(os.path.dirname(SPEC), 'Echoscribe'))
from _version import __version__

block_cipher = None

a = Analysis(
    ['Echoscribe/main.py'],
    pathex=['Echoscribe'],
    binaries=[
        ('vendor/ffmpeg/ffmpeg.exe', 'vendor/ffmpeg/'),
        ('vendor/ffmpeg/ffprobe.exe', 'vendor/ffmpeg/'),
    ],
    datas=[
        ('Assets', 'Assets'),
        ('Models/faster_whisper_base_en', 'Models/faster_whisper_base_en'),
        ('Echoscribe', 'Echoscribe'),
        ('LICENSE.txt', '.'),
        ('README.md', '.'),
        ('ACKNOWLEDGMENTS.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtMultimedia',
        'faster_whisper',
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'Echoscribe',
        'Echoscribe.ui',
        'Echoscribe.ui.main_window',
        'Echoscribe.ui.style',
        'Echoscribe.Core',
        'Echoscribe.Core.transcriber',
        'Echoscribe.Core.dictionary',
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
    name=f'EchoScribe-v{__version__}',
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
    icon='Assets/icons/echoscribe.ico',
    version_file=None,
)