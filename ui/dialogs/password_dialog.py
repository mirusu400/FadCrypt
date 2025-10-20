"""Password Dialog for FadCrypt"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont


class PasswordDialog(QDialog):
    """Custom password dialog with optional fullscreen wallpaper background"""
    
    def __init__(self, title, prompt, resource_path, fullscreen=False, wallpaper_choice=None, parent=None):
        # For fullscreen mode, don't use parent to avoid being hidden when parent is minimized
        if fullscreen:
            super().__init__(None)  # Independent top-level window
        else:
            super().__init__(parent)
        
        self.resource_path = resource_path
        self.fullscreen = fullscreen
        self.wallpaper_choice = wallpaper_choice
        self.password_value = None
        
        self.setWindowTitle(title)
        self.init_ui(title, prompt)
        
    def init_ui(self, title, prompt):
        """Initialize the password dialog UI"""
        if self.fullscreen:
            # Fullscreen mode with wallpaper - truly independent top-level window
            self.setWindowFlags(
                Qt.WindowType.Window |  # Independent window (not child)
                Qt.WindowType.FramelessWindowHint |  # No title bar
                Qt.WindowType.WindowStaysOnTopHint |  # Always on top
                Qt.WindowType.BypassWindowManagerHint  # Bypass window manager (ensures visibility)
            )
            # Make dialog modal to block all other windows
            self.setModal(True)
            
            # Show fullscreen on all screens
            self.showFullScreen()
            
            # Force activation and raise to top
            self.activateWindow()
            self.raise_()
            
            # Set wallpaper background
            self.set_wallpaper_background()
        else:
            # Simple dialog mode - responsive design
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            # Don't set size yet - let it calculate based on content
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout
        main_layout = QVBoxLayout()
        
        if self.fullscreen:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
        
        # Content frame - compact dark theme without border
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: none;
                border-radius: 10px;
            }
        """)
        
        if self.fullscreen:
            content_frame.setFixedSize(440, 240)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(12)
        
        # Title label - compact
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel { 
                font-size: 16px; 
                font-weight: bold; 
                color: #ffffff; 
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Prompt label - responsive with proper wrapping
        prompt_label = QLabel(prompt)
        prompt_label.setWordWrap(True)
        from PyQt6.QtWidgets import QSizePolicy
        prompt_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )
        # Set maximum width for text wrapping
        prompt_label.setMaximumWidth(380)
        prompt_label.setStyleSheet("""
            QLabel { 
                font-size: 11px; 
                color: #a0a0a0; 
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(prompt_label)
        
        # Spacer
        content_layout.addSpacing(8)
        
        # Password input - compact design with red theme
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        self.password_input.returnPressed.connect(self.on_ok)
        content_layout.addWidget(self.password_input)
        
        # Spacer before buttons
        content_layout.addSpacing(10)
        
        # "Forgot Password?" link
        forgot_link = QPushButton("🔑 Forgot Password?")
        forgot_link.setFlat(True)
        forgot_link.setCursor(self.cursor())
        forgot_link.setStyleSheet("""
            QPushButton {
                color: #00bfff;
                border: none;
                padding: 0;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #1e90ff;
            }
        """)
        forgot_link.clicked.connect(self.on_forgot_password)
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()
        forgot_layout.addWidget(forgot_link)
        forgot_layout.addStretch()
        content_layout.addLayout(forgot_layout)
        
        content_layout.addSpacing(10)
        
        # Buttons - compact design
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(120, 36)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #464646;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        ok_button = QPushButton("Unlock")
        ok_button.setFixedSize(120, 36)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """)
        ok_button.clicked.connect(self.on_ok)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        # Adjust dialog size to fit content
        self.adjustSize()
        
        # Set minimum size after calculating content size
        min_width = max(440, self.width())
        min_height = max(240, self.height())
        self.setMinimumSize(min_width, min_height)
        self.resize(min_width, min_height)
        
        # Center dialog on screen (must be done after setLayout and adjustSize)
        if not self.fullscreen:
            self.center_on_screen()
        
        # Focus on password input
        self.password_input.setFocus()
    
    def center_on_screen(self):
        """Center the dialog on the screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            print(f"[PasswordDialog] Centering dialog at ({x}, {y})")
            print(f"   Screen size: {screen_geometry.width()}x{screen_geometry.height()}")
            print(f"   Dialog size: {self.width()}x{self.height()}")
            self.move(x, y)
        else:
            print("[PasswordDialog] ⚠️  No screen found, cannot center")
        
    def set_wallpaper_background(self):
        """Set wallpaper background for fullscreen mode"""
        try:
            # Map wallpaper choices to actual wallpaper image files (.jpg, not preview .png)
            wallpaper_map = {
                'default': 'wall1.jpg',
                'H4ck3r': 'wall2.jpg',
                'Binary': 'wall3.jpg',
                'encrypted': 'wall4.jpg'
            }
            
            wallpaper_file = wallpaper_map.get(self.wallpaper_choice, 'wall1.jpg')
            wallpaper_path = self.resource_path(f"img/{wallpaper_file}")
            
            pixmap = QPixmap(wallpaper_path)
            if not pixmap.isNull():
                # Get screen size
                screen = self.screen()
                if screen:
                    screen_size = screen.size()
                    screen_width = screen_size.width()
                    screen_height = screen_size.height()
                else:
                    screen_width = self.width()
                    screen_height = self.height()
                
                # Scale to fit screen while maintaining aspect ratio (centered, not tiled)
                scaled_pixmap = pixmap.scaled(
                    screen_width, 
                    screen_height, 
                    Qt.AspectRatioMode.KeepAspectRatio,  # Maintain aspect ratio, centered
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Create a full-screen pixmap with black background
                full_pixmap = QPixmap(screen_width, screen_height)
                full_pixmap.fill(Qt.GlobalColor.black)
                
                # Draw the scaled image centered on the black background
                from PyQt6.QtGui import QPainter
                painter = QPainter(full_pixmap)
                x = (screen_width - scaled_pixmap.width()) // 2
                y = (screen_height - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                # Set as background using palette
                from PyQt6.QtGui import QPalette, QBrush
                palette = self.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(full_pixmap))
                self.setPalette(palette)
                
                print(f"[Wallpaper] Loaded: {wallpaper_file}")
                print(f"   Original: {pixmap.width()}x{pixmap.height()}")
                print(f"   Scaled: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                print(f"   Centered at: ({x}, {y})")
        except Exception as e:
            print(f"Error loading wallpaper: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to dark background
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
    
    def on_ok(self):
        """Handle OK button click"""
        self.password_value = self.password_input.text()
        if self.password_value:
            self.accept()
    
    def on_forgot_password(self):
        """Handle forgot password - user needs to recover with code"""
        self.password_value = "RECOVER"  # Special marker for recovery flow
        self.accept()
    
    def get_password(self):
        """Get the entered password"""
        return self.password_value
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


def ask_password(title, prompt, resource_path, style="simple", wallpaper="default", parent=None):
    """
    Helper function to show password dialog.
    
    Args:
        title: Dialog title
        prompt: Prompt text
        resource_path: Function to get resource paths
        style: "simple" or "fullscreen"
        wallpaper: Wallpaper choice ("default", "H4ck3r", "Binary", "encrypted")
        parent: Parent widget
    
    Returns:
        Password string or None if cancelled
    """
    fullscreen = (style == "fullscreen")
    dialog = PasswordDialog(title, prompt, resource_path, fullscreen, wallpaper, parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_password()
    return None
