#!/usr/bin/env python3
"""
FadCrypt - PyQt6 Entry Point (Cross-Platform)
Modern application locker with PyQt6 UI

Detects platform and loads appropriate platform-specific main window.
"""

import sys
import os
import platform
import signal
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
except ImportError as e:
    print("❌ PyQt6 is not installed!")
    print("📦 Install with: pip install PyQt6")
    print(f"   Error: {e}")
    sys.exit(1)

from version import __version__, __version_code__


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    import sys
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_main_window_class(force_windows=False):
    """
    Detect platform and return appropriate main window class.
    
    Args:
        force_windows: If True, force Windows UI (for mock testing on Linux)
    
    Returns:
        MainWindowLinux or MainWindowWindows depending on platform
    """
    system = platform.system()
    
    # Force Windows UI if mock mode is enabled
    if force_windows:
        print("🧪 [MOCK] Forcing Windows UI (system detected: {})".format(system))
        from ui.windows.main_window_windows import MainWindowWindows
        return MainWindowWindows
    
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
    
    # Check for --windows flag BEFORE any imports
    mock_windows = '--windows' in sys.argv
    if mock_windows:
        print("🧪 Mock Windows mode enabled - simulating Windows environment on Linux")
        from win_mock import setup_windows_mocks
        setup_windows_mocks()
    
    # Detect platform
    system = platform.system()
    
    # Step 1: Single Instance Check - Prevent multiple instances
    from core.single_instance_manager import check_single_instance
    single_instance = check_single_instance(exit_if_running=True)
    print("🔒 Single instance lock acquired - no other FadCrypt instances running")
    
    # Step 2: Start File Monitor Daemon - Monitors and backs up config files
    from core.file_monitor import start_file_monitor_daemon
    
    # Store reference to prevent garbage collection
    _file_monitor = None
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("FadCrypt")
    app.setApplicationVersion(__version__)
    
    # Note: High DPI scaling is automatic in Qt6, no need to set attributes
    
    # Show splash screen
    from ui.components.splash_screen import FadCryptSplashScreen
    splash = FadCryptSplashScreen(resource_path)
    splash.show_message("Initializing FadCrypt...")
    
    print(f"✅ FadCrypt v{__version__} starting...")
    print(f"🔢 Version Code: {__version_code__}")
    print(f"🎨 UI Framework: PyQt6")
    print(f"💻 Platform: {system}")
    if mock_windows:
        print(f"🧪 Mock Mode: Windows UI on Linux")
    print(f"📁 Project Root: {project_root}")
    
    # Get platform-specific window class
    splash.show_message("Loading platform modules...")
    MainWindowClass = get_main_window_class(force_windows=mock_windows)
    
    # Create main window (but don't show yet)
    splash.show_message("Creating main window...")
    window = MainWindowClass(version=__version__)
    
    # Setup Ctrl+C signal handler for graceful shutdown after window is created
    # This allows us to access window._force_quit flag
    def signal_handler(sig, frame):
        print("\n🛑 Ctrl+C detected - Shutting down gracefully...")
        window._force_quit = True  # Set flag to bypass minimize-to-tray
        QTimer.singleShot(0, app.quit)  # Schedule quit on next event loop iteration
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Make Python check for signals by installing a very low-overhead timer
    # This only wakes up the event loop, doesn't execute heavy code
    signal_check_timer = QTimer()
    signal_check_timer.start(100)  # 100ms is sufficient and barely noticeable
    signal_check_timer.timeout.connect(lambda: None)  # Empty slot - just processes signals
    
    # Close splash and show main window with proper centering
    # Splash will display for 2.5 seconds - quick but visible
    splash.show_message("Starting application...")
    splash.close_splash(window, delay_ms=2500)
    
    # Check for --auto-monitor flag (startup autostart mode)
    auto_monitor_mode = '--auto-monitor' in sys.argv
    
    if auto_monitor_mode:
        print("🚀 Auto-monitor mode detected - will start monitoring automatically")
    
    # Show window after splash closes
    def show_window():
        window.show()
        # Re-center after window is fully rendered
        QTimer.singleShot(100, window.center_on_screen)
        
        # Start file monitor for config protection
        # This monitors config files and auto-restores them if deleted
        nonlocal _file_monitor
        _file_monitor = start_file_monitor_daemon(
            config_folder_func=window.get_fadcrypt_folder,
            backup_folder_func=window.get_backup_folder if hasattr(window, 'get_backup_folder') else window.get_fadcrypt_folder
        )
        print("✅ Config file monitor started")
        
        print("✅ FadCrypt started successfully!")
        
        # If --auto-monitor flag is present, start monitoring automatically
        if auto_monitor_mode:
            print("🔄 Starting automatic monitoring...")
            QTimer.singleShot(500, window.on_start_monitoring)  # Start monitoring after 500ms
    
    QTimer.singleShot(2550, show_window)  # Show window 50ms after splash closes
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
