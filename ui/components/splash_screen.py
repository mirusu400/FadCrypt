"""Splash Screen for FadCrypt"""

from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPainter
import os


class FadCryptSplashScreen(QSplashScreen):
    """
    Splash screen displayed during application startup.
    Shows the FadCrypt banner in fullscreen mode with transparent background.
    This fixes Wayland centering issues by making the splash truly fullscreen.
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
        
        # Load transparent background image for fullscreen canvas
        screen = QApplication.primaryScreen()
        if screen:
            screen_size = screen.size()
            screen_width = screen_size.width()
            screen_height = screen_size.height()
        else:
            # Fallback size
            screen_width = 1920
            screen_height = 1080
        
        # Try to load transparent.png as background
        transparent_bg_path = self.resource_path('img/transparent.png')
        if os.path.exists(transparent_bg_path):
            fullscreen_pixmap = QPixmap(transparent_bg_path)
            # Scale to fullscreen size
            fullscreen_pixmap = fullscreen_pixmap.scaled(
                screen_width, screen_height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            print(f"[SplashScreen] Using transparent.png as background: {screen_width}x{screen_height}")
        else:
            # Fallback: create transparent pixmap
            fullscreen_pixmap = QPixmap(screen_width, screen_height)
            fullscreen_pixmap.fill(Qt.GlobalColor.transparent)
            print(f"[SplashScreen] transparent.png not found, using transparent fill: {screen_width}x{screen_height}")
        
        # Fullscreen mode with transparent background and bypass window manager
        super().__init__(
            fullscreen_pixmap,
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.BypassWindowManagerHint
        )
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Store the splash pixmap for drawing
        self.splash_pixmap = pixmap
        
        # Initialize message text
        self._message_text = ""
        self.splash_x = 0
        self.splash_y = 0
        
        # Show splash first
        self.showFullScreen()
        
        # Process events to ensure splash is visible
        QApplication.processEvents()
        
        
        print("[SplashScreen] Initialized in fullscreen mode with transparent background")
    
    def paintEvent(self, event):
        """Override paint event to draw centered splash image on transparent background"""
        painter = QPainter(self)
        
        # Note: We don't clear the background here because the base pixmap
        # (transparent.png) is already set and displayed by QSplashScreen.
        # We just draw the banner on top of it.
        
        # Draw the splash banner image centered
        if hasattr(self, 'splash_pixmap'):
            screen_width = self.width()
            screen_height = self.height()
            splash_width = self.splash_pixmap.width()
            splash_height = self.splash_pixmap.height()
            
            # Calculate center position
            self.splash_x = (screen_width - splash_width) // 2
            self.splash_y = (screen_height - splash_height) // 2
            
            # Draw centered banner image
            painter.drawPixmap(self.splash_x, self.splash_y, self.splash_pixmap)
            
            # Draw message text if exists (positioned at image bottom-center)
            if hasattr(self, '_message_text') and self._message_text:
                painter.setPen(Qt.GlobalColor.white)
                font = painter.font()
                font.setPointSize(12)
                painter.setFont(font)
                
                # Calculate text position: centered horizontally, at bottom of splash image
                text_rect = painter.fontMetrics().boundingRect(self._message_text)
                text_x = self.splash_x + (splash_width - text_rect.width()) // 2
                text_y = self.splash_y + splash_height - 20  # 20px from image bottom
                
                painter.drawText(text_x, text_y, self._message_text)
        
        # Note: Don't call painter.end() - Qt handles this automatically
        
        painter.end()
    
    def center_on_screen(self):
        """No longer needed - fullscreen mode handles centering via paintEvent"""
        pass
    
    def show_message(self, message):
        """
        Show a status message on the splash screen at image bottom-center.
        
        Args:
            message: Status message to display
        """
        self._message_text = message
        self.update()  # Trigger repaint to show message
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

