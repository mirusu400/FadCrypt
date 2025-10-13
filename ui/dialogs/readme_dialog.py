"""Fullscreen Readme Dialog with animated text"""

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont


class ReadmeDialog(QDialog):
    def __init__(self, resource_path, parent=None):
        super().__init__(parent)
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
        # Set fullscreen and remove window decorations
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        
        # White background
        self.setStyleSheet("QDialog { background-color: white; }")
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # Animated text label
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("QLabel { color: black; background-color: transparent; }")
        
        # Set font - try Ubuntu first, fallback to system default
        font = QFont("Ubuntu", 14)
        if not font.exactMatch():
            font = QFont("Arial", 14)
        self.text_label.setFont(font)
        
        layout.addWidget(self.text_label, 1)
        
        # OK Button
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(150, 40)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.load_readme_image()
        self.start_animation()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def load_readme_image(self):
        """Load and display the readme image in bottom left corner"""
        try:
            img_path = self.resource_path("img/readme.png")
            pixmap = QPixmap(img_path)
            
            if not pixmap.isNull():
                image_label = QLabel(self)
                scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.move(10, self.height() - 410)
                image_label.show()
        except Exception as e:
            print(f"Error loading readme image: {e}")
    
    def start_animation(self):
        """Start the typewriter animation"""
        self.current_index = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)
        self.animation_timer.start(2)
    
    def animate_text(self):
        """Animate text character by character"""
        if self.current_index < len(self.full_text):
            self.text_label.setText(self.full_text[:self.current_index + 1])
            self.current_index += 1
        else:
            self.animation_timer.stop()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
            self.accept()
        else:
            super().keyPressEvent(event)
