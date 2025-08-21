# -*- mode: python ; coding: utf-8 -*-
"""
EchoScribe PyInstaller Build Configuration

This spec file has been updated to support the new features:
- 🎵 Lyrics Mode: NetEase-style word-by-word centering display
- ⭐ Favorite Words: Word collection and tooltip favorites
- 🎯 Auto-scroll: Real-time word highlighting and centering
- 🔧 Enhanced Settings: Complete configuration management

Last Updated: For lyrics mode and favorite functionality
"""

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
        # ('ACKNOWLEDGMENTS.md', '.'),  # File does not exist, commented out
    ],
    hiddenimports=[
        # PySide6 Core Components
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtSvg',  # For better icon support
        
        # PySide6 Animation Components (for lyrics mode)
        'PySide6.QtCore.QPropertyAnimation',
        'PySide6.QtCore.QEasingCurve',
        'PySide6.QtWidgets.QGraphicsOpacityEffect',
        
        # Audio and Media Components
        'faster_whisper',
        'faster_whisper.transcribe',
        'faster_whisper.audio',
        
        # Text-to-Speech Components
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'pyttsx3.engine',
        
        # Application Modules
        'Echoscribe',
        'Echoscribe.ui',
        'Echoscribe.ui.main_window',
        'Echoscribe.ui.style',
        'Echoscribe.Core',
        'Echoscribe.Core.transcriber',
        'Echoscribe.Core.dictionary',
        
        # Standard Library Components (ensure compatibility)
        'json',
        'threading',
        'time',
        'pathlib',
        'csv',
        'io',
        'sys',
        'os',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce package size
        'tkinter',
        'matplotlib',
        'PIL',
        'test',
        'unittest',
    ],
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
    upx_exclude=[
        # Exclude critical files from UPX compression to prevent issues
        'ffmpeg.exe',
        'ffprobe.exe',
        '*.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Set to True if debugging is needed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Assets/icons/echoscribe.ico',
    version_file=None,
    
    # Additional optimization for lyrics mode features
    optimize=2,  # Enable Python bytecode optimization
)