#!/usr/bin/env python3
"""
FadCrypt - PyQt6 Entry Point (Testing)
Modern application locker with PyQt6 UI

This is a temporary entry point for testing the PyQt6 migration.
Once complete, this will replace FadCrypt.py and FadCrypt_Linux.py
"""

import sys
import os
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

from ui.base.main_window_base import MainWindowBase
from version import __version__, __version_code__


def main():
    """Main entry point for FadCrypt PyQt6 application."""
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("FadCrypt")
    app.setApplicationVersion(__version__)
    
    # Note: High DPI scaling is automatic in Qt6, no need to set attributes
    
    # Create and show main window
    window = MainWindowBase(version=__version__)
    window.show()
    
    print(f"✅ FadCrypt v{__version__} started successfully!")
    print(f"🔢 Version Code: {__version_code__}")
    print(f"🎨 UI Framework: PyQt6")
    print(f"📁 Project Root: {project_root}")
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
