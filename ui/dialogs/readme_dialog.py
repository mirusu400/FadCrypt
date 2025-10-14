"""Fullscreen Readme Dialog with animated text"""

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont


class ReadmeDialog(QDialog):
    def __init__(self, resource_path, parent=None):
        # Make it independent top-level window (no parent) so it stays visible
        super().__init__(None)
        self.resource_path = resource_path
        self.current_index = 0
        self.animation_timer = None
        
        # Full readme text
        self.full_text = (
            "Welcome to FadCrypt!\n\n"
            "Experience top-notch security and sleek design with FadCrypt.\n\n"
            "Features:\n"
            "- Application Locking: Secure apps with an encrypted password. Save your password safely;\nit can't be recovered if lost!\n"
            "- Real-time Monitoring: Detects and auto-recovers critical files if they are deleted.\n"
            "- Auto-Startup: After starting monitoring, the app will be automatically enabled for every session.\n"
            "- Aesthetic UI: Choose custom wallpapers or a minimal style with smooth animations.\n\n"
            "Security:\n"
            "- System Tools Disabled: Disables common terminals (gnome-terminal, konsole, xterm) and system monitors\n  (gnome-system-monitor, htop, top); a real nightmare for attackers trying to bypass it.\n  Manual disabling of other terminals is recommended as it's a significant loophole!\n"
            "- Encrypted Storage: Passwords and config file data (list of locked apps) are encrypted and backed up.\n\n"
            "Testing:\n"
            "- Test blocked tools by trying to run disabled terminals and system monitors to confirm effectiveness.\n\n"
            "Upcoming Features:\n"
            "- Password Recovery: In case of a forgotten password, users will be able to recover their passwords.\n"
            "- Logging and Alerts: Includes screenshots, email alerts on wrong password attempts, and detailed logs.\n"
            "- Community Input: Integrating feedback for improved security and usability.\n\n"
            "Extras:\n"
            "- Snake Game: Enjoy the classic Snake game on the main tab or from the tray icon for a bit of fun!\n\n"
            "# Join our Discord community via the 'Settings' tab\nfor help, questions, or to share your ideas and feedback."
        )
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the fullscreen dialog UI"""
        # Set fullscreen and remove window decorations - truly independent window
        self.setWindowFlags(
            Qt.WindowType.Window |  # Independent window (not child)
            Qt.WindowType.FramelessWindowHint |  # No title bar
            Qt.WindowType.WindowStaysOnTopHint |  # Always on top
            Qt.WindowType.BypassWindowManagerHint  # Bypass window manager
        )
        # Make dialog modal
        self.setModal(True)
        
        # Show fullscreen
        self.showFullScreen()
        
        # Force activation
        self.activateWindow()
        self.raise_()
        
        # Dark background theme
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout - use grid for image + text
        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)
        
        # Content grid (text on left, image on right)
        content_grid = QGridLayout()
        content_grid.setSpacing(30)
        
        # Text label with dark theme (spans full height)
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("QLabel { color: white; background-color: transparent; }")
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set font
        font = QFont("Ubuntu", 15)
        if not font.exactMatch():
            font = QFont("Arial", 15)
        self.text_label.setFont(font)
        
        # Image label - smaller size, anchored to bottom
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Add to grid: text takes 75%, image takes 25%
        content_grid.addWidget(self.text_label, 0, 0, 1, 8)  # Text: 8 columns
        content_grid.addWidget(self.image_label, 0, 8, 1, 2)  # Image: 2 columns
        content_grid.setColumnStretch(0, 8)  # Text column stretch
        content_grid.setColumnStretch(8, 2)  # Image column stretch
        
        main_layout.addLayout(content_grid, 1)
        
        # OK Button (red theme)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(150, 40)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        self.load_readme_image()
        self.start_animation()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def load_readme_image(self):
        """Load and display the readme image using layout"""
        import os
        try:
            img_path = self.resource_path("img/readme.png")
            print(f"\n[README IMAGE] Loading from: {img_path}")
            
            if not os.path.exists(img_path):
                print(f"[README IMAGE] ❌ File not found!")
                return
            
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                print(f"[README IMAGE] ❌ Failed to load pixmap")
                return
            
            print(f"[README IMAGE] Original size: {pixmap.width()}x{pixmap.height()}")
            
            # Scale to smaller size (250px instead of 400px)
            scaled_pixmap = pixmap.scaled(
                250, 250,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            print(f"[README IMAGE] Scaled size: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
            self.image_label.setPixmap(scaled_pixmap)
            # Don't set fixed size - let it expand to fill column height
            
            print(f"[README IMAGE] ✅ Image loaded and displayed")
            
        except Exception as e:
            print(f"[README IMAGE] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def start_animation(self):
        """Start the typewriter animation with fast speed"""
        self.current_index = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)
        # Fast speed: 1ms per character for quick display
        self.animation_timer.start(1)
    
    def animate_text(self):
        """Animate text character by character"""
        if self.current_index < len(self.full_text):
            self.text_label.setText(self.full_text[:self.current_index + 1])
            self.current_index += 1
        else:
            if self.animation_timer:
                self.animation_timer.stop()
                print("[README] Animation complete")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
            self.accept()
        else:
            super().keyPressEvent(event)
