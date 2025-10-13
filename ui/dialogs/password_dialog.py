"""Password Dialog for FadCrypt"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont


class PasswordDialog(QDialog):
    """Custom password dialog with optional fullscreen wallpaper background"""
    
    def __init__(self, title, prompt, resource_path, fullscreen=False, wallpaper_choice=None, parent=None):
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
            # Fullscreen mode with wallpaper
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.showFullScreen()
            
            # Set wallpaper background
            self.set_wallpaper_background()
        else:
            # Simple dialog mode - modern design with proper sizing
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            self.setFixedSize(480, 280)
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
            
            # Center on screen
            screen_geometry = self.screen().geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        if self.fullscreen:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
        
        # Content frame (modern dark theme with gradient-like effect)
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #4ade80;
                border-radius: 12px;
            }
        """)
        
        if self.fullscreen:
            content_frame.setFixedSize(480, 280)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(35, 35, 35, 35)
        content_layout.setSpacing(18)
        
        # Title label - clean and bold
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel { 
                font-size: 18px; 
                font-weight: bold; 
                color: #ffffff; 
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setMaximumHeight(30)
        content_layout.addWidget(title_label)
        
        # Prompt label - better readability with proper wrapping
        prompt_label = QLabel(prompt)
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #b3b3b3; 
                border: none;
                padding: 0;
                margin: 0;
                line-height: 1.5;
            }
        """)
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setMaximumWidth(410)
        content_layout.addWidget(prompt_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacer
        content_layout.addSpacing(5)
        
        # Password input - refined design
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(48)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 0 16px;
                font-size: 14px;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #4ade80;
                background-color: #2e2e2e;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        self.password_input.returnPressed.connect(self.on_ok)
        content_layout.addWidget(self.password_input)
        
        # Spacer before buttons
        content_layout.addSpacing(8)
        
        # Buttons - modern flat design
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(135, 44)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-size: 14px;
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
        ok_button.setFixedSize(135, 44)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        ok_button.clicked.connect(self.on_ok)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        # Set focus to password input
        self.password_input.setFocus()
        
    def set_wallpaper_background(self):
        """Set wallpaper background for fullscreen mode"""
        try:
            # Map wallpaper choices to image files
            wallpaper_map = {
                'default': 'wall1.png',
                'H4ck3r': 'wall2.png',
                'Binary': 'wall3.png',
                'encrypted': 'wall4.png'
            }
            
            wallpaper_file = wallpaper_map.get(self.wallpaper_choice, 'wall1.png')
            wallpaper_path = self.resource_path(f"img/{wallpaper_file}")
            
            pixmap = QPixmap(wallpaper_path)
            if not pixmap.isNull():
                # Scale to screen size
                scaled_pixmap = pixmap.scaled(
                    self.width(), 
                    self.height(), 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Set as background using palette
                from PyQt6.QtGui import QPalette, QBrush
                palette = self.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
        except Exception as e:
            print(f"Error loading wallpaper: {e}")
            # Fallback to dark background
            self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
    
    def on_ok(self):
        """Handle OK button click"""
        self.password_value = self.password_input.text()
        if self.password_value:
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
