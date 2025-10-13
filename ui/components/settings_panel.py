"""
Settings Panel - Application settings and preferences
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QCheckBox,
    QComboBox, QPushButton, QGroupBox, QLabel
)
from PyQt6.QtCore import pyqtSignal


class SettingsPanel(QWidget):
    """
    Settings panel for configuring FadCrypt behavior.
    
    Signals:
        lock_tools_changed: Emitted when "Lock System Tools" changes (bool)
        dialog_style_changed: Emitted when dialog style changes (str)
        wallpaper_changed: Emitted when wallpaper choice changes (str)
        autostart_changed: Emitted when autostart setting changes (bool)
        change_password_clicked: Emitted when change password button clicked
    """
    
    lock_tools_changed = pyqtSignal(bool)
    dialog_style_changed = pyqtSignal(str)
    wallpaper_changed = pyqtSignal(str)
    autostart_changed = pyqtSignal(bool)
    change_password_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # General Settings Group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()
        general_group.setLayout(general_layout)
        
        # Autostart
        self.autostart_checkbox = QCheckBox()
        self.autostart_checkbox.stateChanged.connect(
            lambda state: self.autostart_changed.emit(state == 2)
        )
        general_layout.addRow("Start with System:", self.autostart_checkbox)
        
        # Dialog Style
        self.dialog_style_combo = QComboBox()
        self.dialog_style_combo.addItems(["Simple", "Fullscreen"])
        self.dialog_style_combo.currentTextChanged.connect(
            lambda text: self.dialog_style_changed.emit(text.lower())
        )
        general_layout.addRow("Password Dialog:", self.dialog_style_combo)
        
        # Wallpaper Choice
        self.wallpaper_combo = QComboBox()
        self.wallpaper_combo.addItems(["Default", "Custom..."])
        self.wallpaper_combo.currentTextChanged.connect(
            lambda text: self.wallpaper_changed.emit(text.lower())
        )
        general_layout.addRow("Wallpaper:", self.wallpaper_combo)
        
        main_layout.addWidget(general_group)
        
        # Linux-Specific Settings Group
        linux_group = QGroupBox("Linux-Specific Settings")
        linux_layout = QFormLayout()
        linux_group.setLayout(linux_layout)
        
        # Lock System Tools
        self.lock_tools_checkbox = QCheckBox()
        self.lock_tools_checkbox.setChecked(True)
        self.lock_tools_checkbox.stateChanged.connect(
            lambda state: self.lock_tools_changed.emit(state == 2)
        )
        linux_layout.addRow("Lock System Tools:", self.lock_tools_checkbox)
        
        linux_layout.addRow("", QLabel("(Prevents access to terminal, system monitor, etc.)"))
        
        main_layout.addWidget(linux_group)
        
        # Security Settings Group
        security_group = QGroupBox("Security")
        security_layout = QVBoxLayout()
        security_group.setLayout(security_layout)
        
        # Change Password Button
        self.change_password_button = QPushButton("🔑 Change Master Password")
        self.change_password_button.setMinimumHeight(35)
        self.change_password_button.clicked.connect(self.change_password_clicked.emit)
        security_layout.addWidget(self.change_password_button)
        
        main_layout.addWidget(security_group)
        
        # Stretch at bottom
        main_layout.addStretch()
    
    def get_settings(self) -> dict:
        """Get current settings values."""
        return {
            'autostart': self.autostart_checkbox.isChecked(),
            'dialog_style': self.dialog_style_combo.currentText().lower(),
            'wallpaper': self.wallpaper_combo.currentText().lower(),
            'lock_tools': self.lock_tools_checkbox.isChecked()
        }
    
    def set_settings(self, settings: dict):
        """Set settings values."""
        if 'autostart' in settings:
            self.autostart_checkbox.setChecked(settings['autostart'])
        if 'dialog_style' in settings:
            index = self.dialog_style_combo.findText(settings['dialog_style'].title())
            if index >= 0:
                self.dialog_style_combo.setCurrentIndex(index)
        if 'wallpaper' in settings:
            index = self.wallpaper_combo.findText(settings['wallpaper'].title())
            if index >= 0:
                self.wallpaper_combo.setCurrentIndex(index)
        if 'lock_tools' in settings:
            self.lock_tools_checkbox.setChecked(settings['lock_tools'])
