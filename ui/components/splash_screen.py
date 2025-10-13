"""Splash Screen for FadCrypt"""

from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor
import os


class FadCryptSplashScreen(QSplashScreen):
    """
    Splash screen displayed during application startup.
    Shows the FadCrypt banner while initialization happens.
    """
    
    def __init__(self, resource_path_func):
        """
        Initialize splash screen.
        
        Args:
            resource_path_func: Function to get resource paths
        """
        self.resource_path = resource_path_func
        
        # Load splash image
        splash_image_path = self.resource_path('img/banner-rounded.png')
        
        if os.path.exists(splash_image_path):
            pixmap = QPixmap(splash_image_path)
            
            print(f"[SplashScreen] Loaded splash image: {splash_image_path}")
            print(f"   Original image size: {pixmap.width()}x{pixmap.height()}")
            
            # Scale image slightly bigger than original (around 800px width for better visibility)
            # The original 600x171 was too small, so we'll make it ~33% bigger
            target_width = 800
            target_height = int((target_width / pixmap.width()) * pixmap.height())
            
            pixmap = pixmap.scaled(
                target_width, target_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            print(f"   Scaled to: {pixmap.width()}x{pixmap.height()}")
        else:
            # Fallback: create a simple colored splash
            print(f"[SplashScreen] ⚠️  Splash image not found: {splash_image_path}")
            pixmap = QPixmap(800, 500)
            pixmap.fill(QColor("#1a1b26"))
        
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        
        # Show splash first
        self.show()
        
        # Process events to ensure splash is visible
        QApplication.processEvents()
        
        # Center splash screen after it's fully rendered (Linux/X11 needs this delay)
        QTimer.singleShot(50, self.center_on_screen)
        
    def center_on_screen(self):
        """Center splash screen on the primary display (Wayland-aware).
        
        Industry standard approach for Qt splash centering:
        1. Get primary screen geometry (actual available screen space)
        2. Get splash screen size (the pixmap dimensions)
        3. Calculate center: (screen_width - splash_width) / 2, (screen_height - splash_height) / 2
        4. Use absolute positioning with move() to place splash at calculated center
        5. Account for screen offset (for multi-monitor setups)
        
        Note: On Wayland, move() is ignored - window positioning is controlled by compositor.
        """
        import os
        
        # Check if running under Wayland
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        is_wayland = 'wayland' in session_type or wayland_display
        
        if is_wayland:
            print(f"[SplashScreen] Detected Wayland - compositor controls window positioning")
            # On Wayland, we cannot control window position - compositor decides
            return
        
        # X11 / Windows / macOS - we can control position
        screen = QApplication.primaryScreen()
        if screen:
            # Get the screen's available geometry (excludes taskbars, etc.)
            screen_geometry = screen.availableGeometry()
            screen_x = screen_geometry.x()
            screen_y = screen_geometry.y()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Get splash dimensions
            splash_width = self.width()
            splash_height = self.height()
            
            # Calculate center position (absolute coordinates)
            # Formula: screen_offset + (screen_size - widget_size) / 2
            center_x = screen_x + (screen_width - splash_width) // 2
            center_y = screen_y + (screen_height - splash_height) // 2
            
            print(f"[SplashScreen] Screen geometry: {screen_width}x{screen_height} at ({screen_x}, {screen_y})")
            print(f"[SplashScreen] Splash size: {splash_width}x{splash_height}")
            print(f"[SplashScreen] Centering splash at ({center_x}, {center_y})")
            
            # Move to center
            self.move(center_x, center_y)
        else:
            print("⚠️ [SplashScreen] Could not get primary screen for centering")
    
    def show_message(self, message):
        """
        Show a status message on the splash screen.
        
        Args:
            message: Status message to display
        """
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.white
        )
        QApplication.processEvents()
    
    def close_splash(self, main_window, delay_ms=2500):
        """
        Close splash screen and show main window.
        
        Args:
            main_window: Main window to show after splash
            delay_ms: Minimum display time in milliseconds (default: 2500ms = 2.5 seconds)
                     This ensures the splash is visible but doesn't slow down startup too much
        """
        def finish_splash():
            self.finish(main_window)
            print("[SplashScreen] Closed after minimum display time")
        
        QTimer.singleShot(delay_ms, finish_splash)

