#!/usr/bin/env python3
"""
EchoScribe Application Entry Point

This module handles application initialization, path setup, and FFmpeg configuration.
"""

import sys
import os
from pathlib import Path

# Determine application root path for both development and packaged environments
if getattr(sys, 'frozen', False):
    # Running as packaged executable
    PROJECT_ROOT = Path(sys.executable).parent
else:
    # Running in development environment
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"Project root: {PROJECT_ROOT}")
print(f"Python search path: {sys.path[0]}")

# Import required libraries
from pydub import AudioSegment
from PySide6.QtWidgets import QApplication

# Configure FFmpeg paths for audio processing
ffmpeg_exe_path = PROJECT_ROOT / "vendor" / "ffmpeg" / "ffmpeg.exe"
ffprobe_exe_path = PROJECT_ROOT / "vendor" / "ffmpeg" / "ffprobe.exe"

# Try bundled FFmpeg first, fallback to system FFmpeg
if ffmpeg_exe_path.exists() and ffprobe_exe_path.exists() and ffmpeg_exe_path.stat().st_size > 0:
    print(f"Using bundled FFmpeg: {ffmpeg_exe_path}")
    AudioSegment.converter = str(ffmpeg_exe_path)
    AudioSegment.ffprobe = str(ffprobe_exe_path)
else:
    print("Using system FFmpeg (please ensure FFmpeg is installed on your system)")


def main():
    """Main entry point for EchoScribe application.
    
    Handles dynamic imports for different deployment scenarios:
    - Development environment: Direct package import
    - Packaged environment: Relative import fallback
    """
    try:
        # Try standard package import first
        from Echoscribe.ui.main_window import MainWindow
    except ImportError:
        try:
            # Fallback for packaged environment
            import ui.main_window
            MainWindow = ui.main_window.MainWindow
        except ImportError:
            # Final fallback with manual path adjustment
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)
            from ui.main_window import MainWindow
    
    # Initialize Qt application and main window
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()