"""Base Main Window for FadCrypt PyQt6 UI"""

import sys
import os
import webbrowser
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QFrame, QScrollArea, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase

from ui.components.app_list_widget import AppListWidget
from ui.components.button_panel import ButtonPanel
from ui.components.settings_panel import SettingsPanel
from ui.components.about_panel import AboutPanel
from ui.dialogs.readme_dialog import ReadmeDialog
from ui.dialogs.password_dialog import ask_password

# Import core managers
from core.crypto_manager import CryptoManager
from core.password_manager import PasswordManager
from core.config_manager import ConfigManager
from core.application_manager import ApplicationManager

# Import version info
from version import __version__, __version_code__


class MainWindowBase(QMainWindow):
    """
    Base main window class for FadCrypt application.
    
    This class provides the foundation for the FadCrypt UI with:
    - Main window setup (title, icon, geometry)
    - Menu bar structure
    - Tab widget for organizing features
    - Complete UI matching Tkinter version (banner, footer, all tabs)
    - Resource path handling for images
    """
    
    def __init__(self, version=None):
        super().__init__()
        self.version = version or __version__
        self.version_code = __version_code__
        self.monitoring_active = False
        
        # Initialize settings (will be loaded from JSON later)
        self.password_dialog_style = "simple"
        self.wallpaper_choice = "default"
        
        # Initialize core managers - simplified for now
        self.crypto_manager = CryptoManager()
        
        # Password file path
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        self.password_manager = PasswordManager(password_file, self.crypto_manager)
        
        # Config manager (will be fully integrated later)
        self.config_manager = None
        self.app_manager = None
        
        # Load custom font
        self.load_custom_font()
        
        # Initialize UI
        self.init_ui()
        
        # Connect settings signal
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        
    def load_custom_font(self):
        """Load Ubuntu Regular font for the entire application"""
        font_path = self.resource_path('core/fonts/ubuntu_regular.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.app_font_family = font_families[0]
                    # Set as default font for the application
                    font = QFont(self.app_font_family, 10)
                    from PyQt6.QtWidgets import QApplication
                    QApplication.instance().setFont(font)
                    print(f"✅ Loaded custom font: {self.app_font_family}")
                else:
                    print("⚠️ Font loaded but no families found")
                    self.app_font_family = "Ubuntu"
            else:
                print(f"⚠️ Failed to load font from {font_path}")
                self.app_font_family = "Ubuntu"
        else:
            print(f"⚠️ Font file not found at {font_path}")
            self.app_font_family = "Ubuntu"
        
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"FadCrypt v{self.version}")
        self.setGeometry(100, 100, 950, 700)
        
        # Set window icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create all tabs
        self.create_main_tab()
        self.create_applications_tab()
        self.create_config_tab()
        self.create_settings_tab()
        self.create_about_tab()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)
        
    def create_main_tab(self):
        """Create Main/Home tab with modern design"""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Banner image at top (using banner.png like Tkinter)
        banner_path = self.resource_path('img/banner.png')
        if os.path.exists(banner_path):
            banner_label = QLabel()
            banner_pixmap = QPixmap(banner_path)
            # Resize to 700x200 like Tkinter
            scaled_pixmap = banner_pixmap.scaled(700, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            banner_label.setPixmap(scaled_pixmap)
            banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(banner_label)
        
        main_layout.addSpacing(20)
        
        # Centered buttons frame (Start Monitoring + Read Me) - compact design
        centered_buttons_layout = QHBoxLayout()
        centered_buttons_layout.addStretch()
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setFixedWidth(180)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.start_button.clicked.connect(self.on_start_monitoring)
        centered_buttons_layout.addWidget(self.start_button)
        
        centered_buttons_layout.addSpacing(15)
        
        readme_button = QPushButton("Read Me")
        readme_button.setFixedWidth(180)
        readme_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        readme_button.clicked.connect(self.on_readme_clicked)
        centered_buttons_layout.addWidget(readme_button)
        
        centered_buttons_layout.addStretch()
        main_layout.addLayout(centered_buttons_layout)
        
        main_layout.addSpacing(20)
        
        # Content area with sidebar buttons
        content_layout = QHBoxLayout()
        
        # Left sidebar with compact vertical buttons
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(8)
        
        button_style = """
            QPushButton {
                background-color: #424242;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """
        
        stop_button = QPushButton("Stop Monitoring")
        stop_button.setFixedWidth(180)
        stop_button.setStyleSheet(button_style)
        stop_button.clicked.connect(self.on_stop_monitoring)
        sidebar_layout.addWidget(stop_button)
        
        create_pass_button = QPushButton("Create Password")
        create_pass_button.setFixedWidth(180)
        create_pass_button.setStyleSheet(button_style)
        create_pass_button.clicked.connect(self.on_create_password)
        sidebar_layout.addWidget(create_pass_button)
        
        change_pass_button = QPushButton("Change Password")
        change_pass_button.setFixedWidth(180)
        change_pass_button.setStyleSheet(button_style)
        change_pass_button.clicked.connect(self.on_change_password)
        sidebar_layout.addWidget(change_pass_button)
        
        snake_button = QPushButton("Snake 🪱")
        snake_button.setFixedWidth(180)
        snake_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        snake_button.clicked.connect(self.on_snake_game)
        sidebar_layout.addWidget(snake_button)
        
        sidebar_layout.addStretch()
        
        content_layout.addLayout(sidebar_layout)
        
        # Vertical separator
        separator_v = QFrame()
        separator_v.setFrameShape(QFrame.Shape.VLine)
        separator_v.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator_v)
        
        # Right side - spacer for clean look
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        
        # Horizontal Separator before footer
        separator_h = QFrame()
        separator_h.setFrameShape(QFrame.Shape.HLine)
        separator_h.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator_h)
        
        # Footer with logo, branding, GitHub link
        footer_layout = QHBoxLayout()
        
        # Logo on left
        logo_path = self.resource_path('img/fadsec-main-footer.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            # Scale to 40% as in Tkinter
            scaled_logo = logo_pixmap.scaledToWidth(int(logo_pixmap.width() * 0.4), Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            footer_layout.addWidget(logo_label)
        
        # Branding text
        branding_label = QLabel(" © 2024-2025 | faded.dev | Licensed under GPL 3.0")
        branding_label.setStyleSheet("color: gray; font-size: 10px;")
        footer_layout.addWidget(branding_label)
        
        footer_layout.addStretch()
        
        # GitHub link on right
        github_label = QLabel('<a href="https://github.com/anonfaded/FadCrypt" style="color: #FFD700; text-decoration: none;">⭐ Sponsor on GitHub</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("font-size: 10px;")
        footer_layout.addWidget(github_label)
        
        main_layout.addLayout(footer_layout)
        
        self.tabs.addTab(main_tab, "Main")
        
    def create_applications_tab(self):
        """Create Applications tab for managing locked apps"""
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)
        apps_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Manage Applications")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        apps_layout.addWidget(title_label)
        
        # App list widget
        self.app_list_widget = AppListWidget()
        apps_layout.addWidget(self.app_list_widget)
        
        # Button panel
        self.button_panel = ButtonPanel()
        apps_layout.addWidget(self.button_panel)
        
        # Helper text
        helper_label = QLabel("Just drop it in—I'll sort out the name and path, no worries")
        helper_label.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        helper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apps_layout.addWidget(helper_label)
        
        self.tabs.addTab(apps_tab, "Applications")
        
    def create_config_tab(self):
        """Create Config tab for viewing encrypted apps list"""
        config_tab = QWidget()
        
        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        config_layout = QVBoxLayout(scroll_content)
        config_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Config File")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        config_layout.addWidget(title_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        config_layout.addWidget(separator1)
        
        # Config text display
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setMinimumHeight(300)
        self.config_text.setPlaceholderText("No applications locked yet...")
        config_layout.addWidget(self.config_text)
        
        # Description
        desc_label = QLabel(
            "This is the list of applications currently locked by FadCrypt.\n"
            "It is displayed in plain text here for your convenience, "
            "but rest assured, the data is encrypted when saved on your computer,\n"
            "keeping your locked apps confidential."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray;")
        config_layout.addWidget(desc_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        config_layout.addWidget(separator2)
        
        # Export/Import section
        export_title = QLabel("Backup & Restore Configurations")
        export_title.setStyleSheet("font-weight: bold;")
        config_layout.addWidget(export_title)
        
        export_desc = QLabel("Export your lock list to a file or import a previously saved configuration.")
        export_desc.setWordWrap(True)
        export_desc.setStyleSheet("color: gray;")
        config_layout.addWidget(export_desc)
        
        # Export/Import buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("Export Config")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
        """)
        export_button.clicked.connect(self.on_export_config)
        button_layout.addWidget(export_button)
        
        import_button = QPushButton("Import Config")
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
        """)
        import_button.clicked.connect(self.on_import_config)
        button_layout.addWidget(import_button)
        
        button_layout.addStretch()
        config_layout.addLayout(button_layout)
        
        config_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout(config_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(config_tab, "Config")
        
    def create_settings_tab(self):
        """Create Settings tab"""
        settings_tab = QWidget()
        tab_layout = QVBoxLayout(settings_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the enhanced settings panel with resource_path
        self.settings_panel = SettingsPanel(self.resource_path)
        tab_layout.addWidget(self.settings_panel)
        
        self.tabs.addTab(settings_tab, "Settings")
        
    def create_about_tab(self):
        """Create About tab"""
        about_tab = QWidget()
        tab_layout = QVBoxLayout(about_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the enhanced about panel (pass version, version_code, resource_path_func)
        self.about_panel = AboutPanel(self.version, self.version_code, self.resource_path)
        tab_layout.addWidget(self.about_panel)
        
        self.tabs.addTab(about_tab, "About")
        
    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About FadCrypt",
            f"<h3>FadCrypt v{self.version}</h3>"
            "<p>An open-source application lock and encryption software.</p>"
            "<p>© 2024 FadSec Lab. All rights reserved.</p>"
        )
    
    # Helper methods
    def get_fadcrypt_folder(self):
        """Get FadCrypt configuration folder path"""
        home_dir = os.path.expanduser('~')
        fadcrypt_folder = os.path.join(home_dir, '.FadCrypt')
        
        # Create if not exists
        if not os.path.exists(fadcrypt_folder):
            os.makedirs(fadcrypt_folder, exist_ok=True)
        
        return fadcrypt_folder
    
    def on_settings_changed(self):
        """Handle settings changes from SettingsPanel"""
        # Get current settings
        settings = self.settings_panel.get_settings()
        
        # Update instance variables
        self.password_dialog_style = settings.get('password_dialog_style', 'simple')
        self.wallpaper_choice = settings.get('wallpaper_choice', 'default')
        
        # Save settings to file
        self.save_settings(settings)
        
        print(f"Settings updated: style={self.password_dialog_style}, wallpaper={self.wallpaper_choice}")
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        import json
        settings_file = os.path.join(self.get_fadcrypt_folder(), 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Settings saved to {settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        import json
        settings_file = os.path.join(self.get_fadcrypt_folder(), 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.password_dialog_style = settings.get('password_dialog_style', 'simple')
                    self.wallpaper_choice = settings.get('wallpaper_choice', 'default')
                    print(f"Settings loaded: {settings}")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def show_message(self, title, message, msg_type="info"):
        """Show a message dialog"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "success":
            QMessageBox.information(self, title, message)
        
    # Button handlers (to be overridden by subclasses)
    def on_start_monitoring(self):
        """Handle start monitoring button click"""
        pass
        
    def on_stop_monitoring(self):
        """Handle stop monitoring button click"""
        pass
        
    def on_readme_clicked(self):
        """Handle Read Me button click - show fullscreen dialog"""
        readme_dialog = ReadmeDialog(self.resource_path, self)
        readme_dialog.exec()
        
    def on_create_password(self):
        """Handle create password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        if os.path.exists(password_file):
            self.show_message("Info", "Password already exists. Use 'Change Password' to modify.", "info")
        else:
            password = ask_password(
                "Create Password",
                "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self
            )
            if password:
                try:
                    self.password_manager.create_password(password)
                    self.show_message("Success", "Password created successfully.", "success")
                except Exception as e:
                    self.show_message("Error", f"Failed to create password:\n{e}", "error")
        
    def on_change_password(self):
        """Handle change password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        if os.path.exists(password_file):
            old_password = ask_password(
                "Change Password",
                "Enter your old password:",
                self.resource_path,
                style=self.password_dialog_style,
                wallpaper=self.wallpaper_choice,
                parent=self
            )
            if old_password and self.password_manager.verify_password(old_password):
                new_password = ask_password(
                    "New Password",
                    "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:",
                    self.resource_path,
                    style=self.password_dialog_style,
                    wallpaper=self.wallpaper_choice,
                    parent=self
                )
                if new_password:
                    try:
                        self.password_manager.change_password(old_password, new_password)
                        self.show_message("Success", "Password changed successfully.", "success")
                    except Exception as e:
                        self.show_message("Error", f"Failed to change password:\n{e}", "error")
            else:
                self.show_message("Error", "Incorrect old password.", "error")
        else:
            self.show_message("Oops!", "How do I change a password that doesn't exist? :(", "warning")
        
    def on_snake_game(self):
        """Handle snake game button click"""
        try:
            from core.snake_game import start_snake_game
            # Pass self as the GUI instance
            start_snake_game(self)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Snake Game Error",
                f"Failed to start snake game:\n{e}"
            )
        
    def on_export_config(self):
        """Handle export config button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            os.path.expanduser("~/fadcrypt_config.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Export configuration (placeholder - will need ConfigManager integration)
                import json
                config_data = {
                    'version': self.version,
                    'settings': self.settings_panel.get_settings() if hasattr(self, 'settings_panel') else {},
                    'applications': []  # Will be populated when app_manager is integrated
                }
                
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                
                self.show_message("Success", f"Configuration exported to:\n{file_path}", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to export configuration:\n{e}", "error")
        
    def on_import_config(self):
        """Handle import config button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Configuration",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Import configuration (placeholder - will need ConfigManager integration)
                import json
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                
                # Apply imported settings
                if 'settings' in config_data and hasattr(self, 'settings_panel'):
                    # Will be implemented when settings panel supports loading
                    pass
                
                self.show_message("Success", f"Configuration imported from:\n{file_path}", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to import configuration:\n{e}", "error")
