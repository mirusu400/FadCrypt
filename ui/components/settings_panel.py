"""Settings Panel Component for FadCrypt"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, 
    QCheckBox, QPushButton, QFrame, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


class SettingsPanel(QWidget):
    """Settings panel for FadCrypt configuration with preview sections"""
    
    # Signals for settings changes
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, resource_path_func=None):
        super().__init__()
        self.resource_path = resource_path_func or self._default_resource_path
        self.init_ui()
        
    def _default_resource_path(self, path):
        """Default resource path if none provided"""
        return os.path.join(os.path.abspath("."), path)
        
    def init_ui(self):
        """Initialize the settings panel UI"""
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        title_label = QLabel("Preferences")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)
        
        # Top frame (radio buttons + preview)
        top_frame = QHBoxLayout()
        
        # Left frame for radio buttons
        left_frame = QVBoxLayout()
        left_frame.setSpacing(10)
        
        # Password Dialog Style
        dialog_style_label = QLabel("Password Dialog Style:")
        dialog_style_label.setStyleSheet("font-weight: bold;")
        left_frame.addWidget(dialog_style_label)
        
        self.dialog_style_group = QButtonGroup()
        self.simple_dialog_radio = QRadioButton("Simple Dialog")
        self.simple_dialog_radio.setChecked(True)
        self.simple_dialog_radio.setStyleSheet("""
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        self.dialog_style_group.addButton(self.simple_dialog_radio, 0)
        left_frame.addWidget(self.simple_dialog_radio)
        
        self.fullscreen_dialog_radio = QRadioButton("Full Screen")
        self.fullscreen_dialog_radio.setStyleSheet("""
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        self.dialog_style_group.addButton(self.fullscreen_dialog_radio, 1)
        left_frame.addWidget(self.fullscreen_dialog_radio)
        
        left_frame.addSpacing(20)
        
        # Wallpaper Choice
        wallpaper_label = QLabel("Full Screen Wallpaper:")
        wallpaper_label.setStyleSheet("font-weight: bold;")
        left_frame.addWidget(wallpaper_label)
        
        self.wallpaper_group = QButtonGroup()
        
        # Common radio button style for wallpaper options
        wallpaper_radio_style = """
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #888888;
            }
        """
        
        self.lab_wallpaper_radio = QRadioButton("Lab (Default)")
        self.lab_wallpaper_radio.setChecked(True)
        self.lab_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.lab_wallpaper_radio, 0)
        left_frame.addWidget(self.lab_wallpaper_radio)
        
        self.hacker_wallpaper_radio = QRadioButton("H4ck3r")
        self.hacker_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.hacker_wallpaper_radio, 1)
        left_frame.addWidget(self.hacker_wallpaper_radio)
        
        self.binary_wallpaper_radio = QRadioButton("Binary")
        self.binary_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.binary_wallpaper_radio, 2)
        left_frame.addWidget(self.binary_wallpaper_radio)
        
        self.encrypted_wallpaper_radio = QRadioButton("Encryptedddddd")
        self.encrypted_wallpaper_radio.setStyleSheet(wallpaper_radio_style)
        self.wallpaper_group.addButton(self.encrypted_wallpaper_radio, 3)
        left_frame.addWidget(self.encrypted_wallpaper_radio)
        
        left_frame.addStretch()
        
        # Right frame for preview
        right_frame = QVBoxLayout()
        right_frame.setSpacing(10)
        
        preview_label = QLabel("Dialog Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        right_frame.addWidget(preview_label)
        
        # Preview frame - no border, just dark background
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Shape.NoFrame)
        self.preview_frame.setMinimumSize(400, 250)
        self.preview_frame.setMaximumSize(400, 250)
        self.preview_frame.setStyleSheet("background-color: #1a1a1a; border: none;")
        
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Don't use setScaledContents - we'll handle scaling manually with SmoothTransformation
        preview_layout.addWidget(self.preview_label)
        
        right_frame.addWidget(self.preview_frame)
        right_frame.addStretch()
        
        top_frame.addLayout(left_frame, 1)
        top_frame.addLayout(right_frame, 2)
        
        layout.addLayout(top_frame)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        
        # Bottom frame for checkboxes and info
        bottom_frame = QVBoxLayout()
        bottom_frame.setSpacing(10)
        
        # Disable Main Loopholes
        loopholes_title = QLabel("Disable Main loopholes")
        loopholes_title.setStyleSheet("font-weight: bold;")
        bottom_frame.addWidget(loopholes_title)
        
        self.lock_tools_checkbox = QCheckBox(
            "Disable common terminals and system monitors during monitoring."
        )
        self.lock_tools_checkbox.setChecked(True)
        self.lock_tools_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #d32f2f;
                background-color: #d32f2f;
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #888888;
            }
        """)
        bottom_frame.addWidget(self.lock_tools_checkbox)
        
        # Info text below checkbox in darker color
        lock_tools_info = QLabel(
            "(Default: gnome-terminal, konsole, xterm, gnome-system-monitor, htop, and top are disabled for best security. "
            "Tools are automatically re-enabled when monitoring is stopped. For added security, please disable other terminals manually; "
            "otherwise, FadCrypt could be terminated via terminal.)"
        )
        lock_tools_info.setStyleSheet("color: #666666; font-size: 11px; padding-left: 26px;")
        lock_tools_info.setWordWrap(True)
        bottom_frame.addWidget(lock_tools_info)
        
        # Uninstall Cleanup
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        bottom_frame.addWidget(separator3)
        
        cleanup_title = QLabel("🔧 Uninstall Cleanup")
        cleanup_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        bottom_frame.addWidget(cleanup_title)
        
        cleanup_info = QLabel(
            "Before uninstalling FadCrypt, run this cleanup to restore all system settings.\n"
            "This will re-enable disabled terminals, system monitors, and remove autostart entries."
        )
        cleanup_info.setStyleSheet("color: #888888;")
        cleanup_info.setWordWrap(True)
        bottom_frame.addWidget(cleanup_info)
        
        cleanup_button = QPushButton("Run Uninstall Cleanup")
        cleanup_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        cleanup_button.clicked.connect(lambda: self.on_cleanup_clicked())
        cleanup_button.setMaximumWidth(200)
        bottom_frame.addWidget(cleanup_button)
        
        layout.addLayout(bottom_frame)
        layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Connect signals
        self.dialog_style_group.buttonClicked.connect(self.on_settings_changed)
        self.wallpaper_group.buttonClicked.connect(self.on_settings_changed)
        self.lock_tools_checkbox.stateChanged.connect(self.on_settings_changed)
        
        # Initial preview update
        self.update_preview()
        
    def update_preview(self):
        """Update the preview image based on current settings"""
        dialog_style = "simple" if self.simple_dialog_radio.isChecked() else "fullscreen"
        wallpaper = self.get_wallpaper_choice()
        
        # Determine preview path based on selection
        if dialog_style == "simple":
            preview_path = self.resource_path("img/preview1.png")
        else:  # fullscreen
            if wallpaper == "default":
                preview_path = self.resource_path("img/wall1.png")
            elif wallpaper == "H4ck3r":
                preview_path = self.resource_path("img/wall2.png")
            elif wallpaper == "Binary":
                preview_path = self.resource_path("img/wall3.png")
            elif wallpaper == "encrypted":
                preview_path = self.resource_path("img/wall4.png")
            else:
                preview_path = self.resource_path("img/preview2.png")
        
        # Load and display preview image
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            scaled_pixmap = pixmap.scaled(400, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText(f"Preview not found:\n{os.path.basename(preview_path)}")
            self.preview_label.setStyleSheet("color: #999; font-size: 12px;")
        
    def on_settings_changed(self):
        """Emit settings changed signal and update preview"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        self.update_preview()
        
    def on_cleanup_clicked(self):
        """Handle cleanup button click"""
        # To be implemented by main window
        pass
        
    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            'dialog_style': 'simple' if self.simple_dialog_radio.isChecked() else 'fullscreen',
            'wallpaper': self.get_wallpaper_choice(),
            'lock_tools': self.lock_tools_checkbox.isChecked()
        }
        
    def get_wallpaper_choice(self):
        """Get selected wallpaper"""
        if self.lab_wallpaper_radio.isChecked():
            return 'default'
        elif self.hacker_wallpaper_radio.isChecked():
            return 'H4ck3r'
        elif self.binary_wallpaper_radio.isChecked():
            return 'Binary'
        elif self.encrypted_wallpaper_radio.isChecked():
            return 'encrypted'
        return 'default'
        
    def set_settings(self, settings):
        """Set settings from dictionary"""
        dialog_style = settings.get('dialog_style', 'simple')
        if dialog_style == 'fullscreen':
            self.fullscreen_dialog_radio.setChecked(True)
        else:
            self.simple_dialog_radio.setChecked(True)
            
        wallpaper = settings.get('wallpaper', 'default')
        if wallpaper == 'H4ck3r':
            self.hacker_wallpaper_radio.setChecked(True)
        elif wallpaper == 'Binary':
            self.binary_wallpaper_radio.setChecked(True)
        elif wallpaper == 'encrypted':
            self.encrypted_wallpaper_radio.setChecked(True)
        else:
            self.lab_wallpaper_radio.setChecked(True)
            
        self.lock_tools_checkbox.setChecked(settings.get('lock_tools', True))
        
        self.on_settings_changed()
    
    def apply_settings(self, settings):
        """Alias for set_settings - apply settings from dictionary"""
        self.set_settings(settings)

