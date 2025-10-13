#!/usr/bin/env python3
"""
FadCrypt - PyQt6 Entry Point (Cross-Platform)
Modern application locker with PyQt6 UI

Detects platform and loads appropriate platform-specific main window.
"""

import sys
import os
import platform
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
except ImportError as e:
    print("❌ PyQt6 is not installed!")
    print("📦 Install with: pip install PyQt6")
    print(f"   Error: {e}")
    sys.exit(1)

from version import __version__, __version_code__


def get_main_window_class():
    """
    Detect platform and return appropriate main window class.
    
    Returns:
        MainWindowLinux or MainWindowWindows depending on platform
    """
    system = platform.system()
    
    if system == "Linux":
        from ui.linux.main_window_linux import MainWindowLinux
        return MainWindowLinux
    elif system == "Windows":
        from ui.windows.main_window_windows import MainWindowWindows
        return MainWindowWindows
    else:
        # Fall back to base class for other platforms (macOS, BSD, etc.)
        print(f"⚠️  Warning: Unsupported platform '{system}', using base implementation")
        from ui.base.main_window_base import MainWindowBase
        return MainWindowBase


def main():
    """Main entry point for FadCrypt PyQt6 application."""
    
    # Detect platform
    system = platform.system()
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("FadCrypt")
    app.setApplicationVersion(__version__)
    
    # Note: High DPI scaling is automatic in Qt6, no need to set attributes
    
    # Get platform-specific window class
    MainWindowClass = get_main_window_class()
    
    # Create and show main window
    window = MainWindowClass(version=__version__)
    window.show()
    
    print(f"✅ FadCrypt v{__version__} started successfully!")
    print(f"🔢 Version Code: {__version_code__}")
    print(f"🎨 UI Framework: PyQt6")
    print(f"💻 Platform: {system}")
    print(f"📁 Project Root: {project_root}")
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
