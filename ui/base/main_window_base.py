"""Base Main Window for FadCrypt PyQt6 UI"""

import sys
import os
import json
import webbrowser
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QFrame, QScrollArea, QTextEdit, 
    QFileDialog, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase, QSyntaxHighlighter, QTextCharFormat, QColor

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


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON with dark theme colors"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define formats for different JSON elements
        self.formats = {}
        
        # Keys (blue)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#61afef"))  # Blue
        self.formats['key'] = key_format
        
        # String values (green)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#98c379"))  # Green
        self.formats['string'] = string_format
        
        # Numbers (orange)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#d19a66"))  # Orange
        self.formats['number'] = number_format
        
        # Booleans and null (purple)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#c678dd"))  # Purple
        self.formats['keyword'] = keyword_format
        
        # Braces and brackets (white)
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor("#abb2bf"))  # Light gray
        self.formats['brace'] = brace_format
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Highlight JSON keys (text before colon in quotes)
        key_pattern = QRegularExpression(r'"([^"]+)"\s*:')
        iterator = key_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['key'])
        
        # Highlight string values (text in quotes after colon)
        string_pattern = QRegularExpression(r':\s*"([^"]*)"')
        iterator = string_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart() + text[match.capturedStart():].index('"')
            length = match.capturedEnd() - start
            self.setFormat(start, length, self.formats['string'])
        
        # Highlight numbers
        number_pattern = QRegularExpression(r'\b\d+\.?\d*\b')
        iterator = number_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['number'])
        
        # Highlight booleans and null
        keyword_pattern = QRegularExpression(r'\b(true|false|null)\b')
        iterator = keyword_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['keyword'])
        
        # Highlight braces and brackets
        brace_pattern = QRegularExpression(r'[{}[\],]')
        iterator = brace_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['brace'])


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
    
    # Class-level signal for thread-safe password prompts
    password_prompt_requested = pyqtSignal(str, str)
    
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
        
        # Password file path - use platform-specific folder
        fadcrypt_folder = self.get_fadcrypt_folder()
        password_file = os.path.join(fadcrypt_folder, "encrypted_password.bin")
        self.password_manager = PasswordManager(password_file, self.crypto_manager)
        
        # Log important paths at startup
        print("\n📁 FadCrypt File Locations:")
        print(f"   Main Config Folder: {fadcrypt_folder}")
        print(f"   Password File: {password_file}")
        print(f"   Config File: {os.path.join(fadcrypt_folder, 'apps_config.json')}")
        print(f"   Settings File: {os.path.join(fadcrypt_folder, 'settings.json')}")
        print(f"   State File: {os.path.join(fadcrypt_folder, 'monitoring_state.json')}")
        if hasattr(self, 'get_backup_folder'):
            print(f"   Backup Folder: {self.get_backup_folder()}")
        print()
        
        # Config manager (will be fully integrated later)
        self.config_manager = None
        self.app_manager = None
        
        # Monitoring state
        self.monitoring_active = False
        self.unified_monitor = None
        self.pending_password_result = None
        
        # System tray (will be initialized after UI)
        self.system_tray = None
        
        # Load custom font
        self.load_custom_font()
        
        # Initialize UI
        # Initialize monitoring state
        self.monitoring_state = {
            'unlocked_apps': []
        }
        self.load_monitoring_state()
        
        self.init_ui()
        
        # Initialize system tray after UI
        self.init_system_tray()
        
        # Connect password prompt signal (for thread-safe dialog)
        self.password_prompt_requested.connect(self.show_password_prompt_for_app_sync)
        
        # Connect settings signal
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        
        # Center window after everything is initialized
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.center_on_screen)
        
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
        
        # Set initial size
        self.resize(950, 700)
        
        # Set darker app-wide stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f0f;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
            }
            QTabBar::tab {
                background-color: #222222;
                color: #ffffff;
                padding: 10px 20px;
                border: 1px solid #2a2a2a;
            }
            QTabBar::tab:selected {
                background-color: #2a2a2a;
                border-bottom: 3px solid #4ade80;
            }
            QTabBar::tab:hover {
                background-color: #282828;
            }
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #333333;
            }
        """)
        
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
        """Create menu bar with File and Help menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)
    
    def init_system_tray(self):
        """Initialize system tray icon"""
        from ui.components.system_tray import SystemTray
        
        self.system_tray = SystemTray(self.resource_path, self)
        
        # Connect system tray signals
        self.system_tray.show_window_requested.connect(self.show_window_from_tray)
        self.system_tray.hide_window_requested.connect(self.hide_to_tray)
        self.system_tray.start_monitoring_requested.connect(self.on_start_monitoring)
        self.system_tray.stop_monitoring_requested.connect(self.on_stop_monitoring)
        self.system_tray.exit_requested.connect(self.close)
        
        # Show tray icon
        self.system_tray.show()
        
        print("✅ System tray initialized")
    
    def show_window_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        if self.system_tray:
            self.system_tray.show_message(
                "FadCrypt",
                "FadCrypt is running in the background.\nClick the tray icon to show the window.",
                QSystemTrayIcon.MessageIcon.Information
            )
        
    def create_main_tab(self):
        """Create Main/Home tab with modern design"""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Banner image at top (using banner-rounder.png)
        banner_path = self.resource_path('img/banner-rounded.png')
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
        from ui.components.app_grid_widget import AppGridWidget
        from PyQt6.QtWidgets import QLineEdit, QComboBox
        
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)
        apps_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with app count
        header_layout = QHBoxLayout()
        self.app_count_label = QLabel("Applications: 0")
        self.app_count_label.setStyleSheet("""
            color: #ffffff;
            font-size: 13pt;
            font-weight: bold;
        """)
        header_layout.addWidget(self.app_count_label)
        header_layout.addStretch()
        apps_layout.addLayout(header_layout)
        
        # Search and filter bar
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(10)
        
        # Search icon label
        search_icon = QLabel("🔎")
        search_icon.setStyleSheet("font-size: 16px; color: #888888;")
        search_filter_layout.addWidget(search_icon)
        
        # Search input
        self.app_search_input = QLineEdit()
        self.app_search_input.setPlaceholderText("Search applications by name or path...")
        self.app_search_input.textChanged.connect(self.filter_applications)
        self.app_search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        search_filter_layout.addWidget(self.app_search_input, stretch=1)
        
        # Sort dropdown label
        sort_label = QLabel("Sort:")
        sort_label.setStyleSheet("color: #e5e7eb; font-size: 13px; padding-right: 8px;")
        search_filter_layout.addWidget(sort_label)
        
        self.app_sort_combo = QComboBox()
        self.app_sort_combo.addItems(["Name (A-Z)", "Name (Z-A)", "Recently Added", "Most Used"])
        self.app_sort_combo.currentTextChanged.connect(self.sort_applications)
        self.app_sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 8px 12px;
                padding-right: 35px;
                min-width: 140px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDdMMTEgMSIgc3Ryb2tlPSIjODg4ODg4IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
                width: 12px;
                height: 8px;
            }
            QComboBox::down-arrow:hover {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDdMMTEgMSIgc3Ryb2tlPSIjZTVlN2ViIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #e5e7eb;
                selection-background-color: #3b82f6;
                border: 1px solid #333333;
            }
        """)
        search_filter_layout.addWidget(self.app_sort_combo)
        
        # Clear search button
        self.clear_search_btn = QPushButton("✕")
        self.clear_search_btn.setToolTip("Clear search")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #888888;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                color: #e5e7eb;
            }
        """)
        search_filter_layout.addWidget(self.clear_search_btn)
        
        apps_layout.addLayout(search_filter_layout)
        
        # App grid widget (replaces simple list)
        self.app_list_widget = AppGridWidget()
        apps_layout.addWidget(self.app_list_widget)
        
        # Button panel
        self.button_panel = ButtonPanel()
        
        # Connect button panel signals
        self.button_panel.add_app_clicked.connect(self.add_application)
        self.button_panel.edit_app_clicked.connect(self.edit_application)
        self.button_panel.remove_app_clicked.connect(self.remove_application)
        self.button_panel.select_all_clicked.connect(self.select_all_apps)
        self.button_panel.deselect_all_clicked.connect(self.deselect_all_apps)
        
        # Connect app list widget signals
        self.app_list_widget.app_edited.connect(self.handle_app_edited)
        self.app_list_widget.app_removed.connect(self.handle_app_removed)
        self.app_list_widget.app_lock_toggled.connect(self.handle_lock_toggled)
        
        apps_layout.addWidget(self.button_panel)
        
        self.tabs.addTab(apps_tab, "Applications")
        
        # Load saved applications
        self.load_applications_config()
        
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
        
        # Apply JSON syntax highlighting
        self.json_highlighter = JsonSyntaxHighlighter(self.config_text.document())
        
        # Set dark background for better contrast with syntax colors
        self.config_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #abb2bf;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        
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
        
        # Initial update of config display
        self.update_config_display()
        
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
        self.password_dialog_style = settings.get('dialog_style', 'simple')
        self.wallpaper_choice = settings.get('wallpaper', 'default')
        
        # Handle autostart
        autostart_enabled = settings.get('autostart', False)
        self.handle_autostart_setting(autostart_enabled)
        
        # Save settings to file
        self.save_settings(settings)
        
        print(f"Settings updated: style={self.password_dialog_style}, wallpaper={self.wallpaper_choice}, autostart={autostart_enabled}")
    
    def handle_autostart_setting(self, enable):
        """
        Handle autostart setting change. Platform-specific classes should override this.
        
        Args:
            enable: True to enable autostart, False to disable
        """
        # Base implementation does nothing, platform-specific classes override
        print(f"Autostart {'enabled' if enable else 'disabled'} (base implementation)")
        pass
    
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
    
    def center_on_screen(self):
        """Center the main window on the screen (Wayland-aware)"""
        from PyQt6.QtWidgets import QApplication
        import os
        
        # Check if running under Wayland
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        is_wayland = 'wayland' in session_type or wayland_display
        
        if is_wayland:
            print(f"[MainWindow] Detected Wayland session - window manager controls positioning")
            # On Wayland, window positioning is controlled by the compositor
            # We can't use move() - the window will be placed by the WM
            # The window will typically be centered automatically on first show
            return
        
        # X11 / Windows / macOS - we can control position
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            print(f"[MainWindow] Centering window at ({x}, {y})")
            print(f"   Screen size: {screen_geometry.width()}x{screen_geometry.height()}")
            print(f"   Window size: {self.width()}x{self.height()}")
            self.move(x, y)
        else:
            print("[MainWindow] ⚠️  No screen found, cannot center")
    
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
    
    # Application management methods
    def add_application(self):
        """Open the Add Application dialog"""
        from ui.dialogs.add_application_dialog import AddApplicationDialog
        
        dialog = AddApplicationDialog(self.resource_path, self)
        dialog.application_added.connect(self.on_application_added)
        dialog.exec()
    
    def on_application_added(self, app_name, app_path):
        """Handle application added from dialog"""
        # Check if already added
        if app_name in self.app_list_widget.apps_data:
            self.show_message("Info", f"Application '{app_name}' is already in the list.", "info")
            return
        
        # Add to the grid (with unlock_count=0 by default)
        self.app_list_widget.add_app(app_name, app_path, unlock_count=0)
        self.save_applications_config()
        self.update_app_count()
        self.show_message("Success", f"Application '{app_name}' added successfully.", "success")
    
    def update_app_count(self):
        """Update the application count label"""
        count = len(self.app_list_widget.apps_data)
        self.app_count_label.setText(f"Applications: {count}")
    
    def remove_application(self):
        """Remove selected applications from the list"""
        selected_apps = self.app_list_widget.get_selected_apps()
        
        if not selected_apps:
            self.show_message("Info", "Please select at least one application to remove.", "info")
            return
        
        # Confirm removal
        app_names = ", ".join(selected_apps)
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove:\n{app_names}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for app_name in selected_apps:
                self.app_list_widget.remove_app(app_name)
            self.save_applications_config()
            self.update_app_count()
            self.show_message("Success", f"Removed {len(selected_apps)} application(s) successfully.", "success")
    
    def toggle_app_lock(self):
        """Toggle lock status of selected applications - NOT USED IN PyQt6 VERSION"""
        # This method is for backward compatibility but not used in new design
        pass
    
    def select_all_apps(self):
        """Select all applications in the list"""
        if not self.app_list_widget.apps_data:
            self.show_message("Info", "No applications to select.", "info")
            return
        
        self.app_list_widget.selectAll()
        self.show_message("Success", "All applications selected.", "success")
    
    def deselect_all_apps(self):
        """Deselect all applications in the list"""
        if not self.app_list_widget.apps_data:
            self.show_message("Info", "No applications to deselect.", "info")
            return
        
        self.app_list_widget.clearSelection()
        self.show_message("Success", "All applications deselected.", "success")
    
    def filter_applications(self, search_text):
        """Filter applications based on search text"""
        search_text = search_text.lower().strip()
        
        if not search_text:
            # Show all apps
            for app_name, card in self.app_list_widget.app_cards.items():
                card.show()
            self.update_app_count()
            return
        
        # Filter apps by name or path
        visible_count = 0
        for app_name, card in self.app_list_widget.app_cards.items():
            app_data = self.app_list_widget.apps_data.get(app_name, {})
            app_path = app_data.get('path', '').lower()
            
            if search_text in app_name.lower() or search_text in app_path:
                card.show()
                visible_count += 1
            else:
                card.hide()
        
        # Update count label to show filtered results
        total = len(self.app_list_widget.apps_data)
        if visible_count < total:
            self.app_count_label.setText(f"Applications: {visible_count} of {total}")
        else:
            self.app_count_label.setText(f"Applications: {total}")
    
    def sort_applications(self, sort_option):
        """Sort applications based on selected option"""
        if not self.app_list_widget.apps_data:
            return
        
        apps_list = list(self.app_list_widget.apps_data.items())
        
        if sort_option == "Name (A-Z)":
            apps_list.sort(key=lambda x: x[0].lower())
        elif sort_option == "Name (Z-A)":
            apps_list.sort(key=lambda x: x[0].lower(), reverse=True)
        elif sort_option == "Recently Added":
            # Keep original order (assuming last added are at the end)
            apps_list.reverse()
        elif sort_option == "Most Used":
            # Sort by unlock_count descending
            apps_list.sort(key=lambda x: x[1].get('unlock_count', 0), reverse=True)
        
        # Rebuild apps_data dict in sorted order
        self.app_list_widget.apps_data = dict(apps_list)
        self.app_list_widget.refresh_grid()
        
        # Reapply current search filter if any
        if hasattr(self, 'app_search_input') and self.app_search_input.text():
            self.filter_applications(self.app_search_input.text())
    
    def clear_search(self):
        """Clear search input and show all applications"""
        if hasattr(self, 'app_search_input'):
            self.app_search_input.clear()
            # filter_applications will be called automatically via textChanged signal
    
    def scan_for_applications(self):
        """Open App Scanner dialog to scan system for installed apps"""
        from ui.dialogs.app_scanner_dialog import AppScannerDialog
        
        print("[MainWindow] Opening app scanner dialog...")
        dialog = AppScannerDialog(self)
        dialog.apps_selected.connect(self.on_apps_scanned)
        dialog.exec()
    
    def on_apps_scanned(self, selected_apps):
        """Handle batch adding of scanned applications"""
        added_count = 0
        skipped_count = 0
        
        for app in selected_apps:
            app_name = app['name']
            app_path = app['path']
            
            # Check if already added
            if app_name in self.app_list_widget.apps_data:
                print(f"[Scanner] Skipping duplicate: {app_name}")
                skipped_count += 1
                continue
            
            # Add to the grid
            self.app_list_widget.add_app(app_name, app_path, unlock_count=0)
            added_count += 1
        
        if added_count > 0:
            self.save_applications_config()
            self.update_app_count()
        
        # Show summary
        message = f"✅ Added {added_count} application(s)"
        if skipped_count > 0:
            message += f"\n⚠️ Skipped {skipped_count} duplicate(s)"
        
        self.show_message("Scan Complete", message, "success")
        print(f"[Scanner] Added: {added_count}, Skipped: {skipped_count}")
    
    def edit_application(self):
        """Edit selected application"""
        selected_apps = self.app_list_widget.get_selected_apps()
        
        if not selected_apps:
            self.show_message("Info", "Please select an application to edit.", "info")
            return
        
        if len(selected_apps) > 1:
            self.show_message("Info", "Please select only one application to edit.", "info")
            return
        
        app_name = selected_apps[0]
        app_data = self.app_list_widget.apps_data[app_name]
        app_path = app_data['path']
        
        # Open edit dialog
        from ui.dialogs.edit_application_dialog import EditApplicationDialog
        dialog = EditApplicationDialog(app_name, app_path, self)
        dialog.app_updated.connect(self.on_application_edited)
        dialog.exec()
    
    def on_application_edited(self, old_name, new_name, new_path):
        """Handle application edit from dialog"""
        # Check if new name conflicts with existing app (excluding the old one)
        if new_name != old_name and new_name in self.app_list_widget.apps_data:
            self.show_message("Error", f"An application named '{new_name}' already exists.", "error")
            return
        
        # Get old app data
        old_data = self.app_list_widget.apps_data.get(old_name)
        if not old_data:
            print(f"[Edit] Error: Could not find old app data for '{old_name}'")
            return
        
        # Preserve unlock count
        unlock_count = old_data.get('unlock_count', 0)
        
        # Remove old entry
        self.app_list_widget.remove_app(old_name)
        
        # Add new entry
        self.app_list_widget.add_app(new_name, new_path, unlock_count=unlock_count)
        
        # Save config
        self.save_applications_config()
        self.update_app_count()
        
        self.show_message("Success", f"Application updated successfully:\n'{old_name}' → '{new_name}'", "success")
        print(f"[Edit] Updated: '{old_name}' -> '{new_name}', path: '{new_path}'")
    
    def handle_app_edited(self, old_name, new_name, new_path):
        """Handle app edit from context menu (app_list_widget signal)"""
        # Reuse the edit dialog
        app_data = self.app_list_widget.apps_data.get(old_name)
        if not app_data:
            return
        
        from ui.dialogs.edit_application_dialog import EditApplicationDialog
        dialog = EditApplicationDialog(old_name, app_data['path'], self)
        dialog.app_updated.connect(self.on_application_edited)
        dialog.exec()
    
    def handle_app_removed(self, app_name):
        """Handle app removal from context menu (app_list_widget signal)"""
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove '{app_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from widget
            self.app_list_widget.remove_app(app_name)
            # Save config
            self.save_applications_config()
            self.update_app_count()
            self.show_message("Success", f"Application '{app_name}' removed.", "success")
            print(f"[Remove] Removed app: {app_name}")
    
    def handle_lock_toggled(self, app_name, is_locked):
        """Handle lock toggle from context menu (app_list_widget signal)"""
        print(f"[LockToggle] {app_name} is now {'locked' if is_locked else 'unlocked'}")
        # Lock state is already updated in widget, just save config
        self.save_applications_config()
        status = "locked" if is_locked else "unlocked"
        self.show_message("Success", f"Application '{app_name}' is now {status}.", "success")
    
    def save_applications_config(self):
        """Save applications configuration to JSON file"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        # Build config data
        config_data = {}
        for app_name, app_data in self.app_list_widget.apps_data.items():
            config_data[app_name] = {
                'path': app_data['path'],
                'unlock_count': app_data.get('unlock_count', 0),
                'date_added': app_data.get('date_added', None)
            }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"Applications config saved: {len(config_data)} apps")
            
            # Also update the config tab display
            self.update_config_display()
        except Exception as e:
            print(f"Error saving applications config: {e}")
    
    def update_config_display(self):
        """Update the config display in Config tab - show raw JSON"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Display raw JSON with proper formatting
                raw_json = json.dumps(config_data, indent=4)
                self.config_text.setPlainText(raw_json)
                print(f"[Config Display] Updated with {len(config_data)} apps")
            except Exception as e:
                error_msg = f"Error loading config: {e}"
                self.config_text.setPlainText(error_msg)
                print(f"[Config Display] {error_msg}")
        else:
            empty_msg = "No configuration file found. Add applications to create config."
            self.config_text.setPlainText(empty_msg)
            print(f"[Config Display] {empty_msg}")
    
    def load_applications_config(self):
        """Load applications configuration from JSON file"""
        config_file = os.path.join(self.get_fadcrypt_folder(), 'apps_config.json')
        
        if not os.path.exists(config_file):
            return
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Clear current grid
            self.app_list_widget.apps_data.clear()
            
            # Load apps
            for app_name, app_data in config_data.items():
                self.app_list_widget.add_app(
                    app_name,
                    app_data['path'],
                    unlock_count=app_data.get('unlock_count', 0),
                    date_added=app_data.get('date_added', None)
                )
            
            self.update_app_count()
            print(f"Applications config loaded: {len(config_data)} apps")
            
            # Update config display to show the loaded apps (if config tab has been created)
            if hasattr(self, 'config_text'):
                self.update_config_display()
        except Exception as e:
            print(f"Error loading applications config: {e}")
        
    # Button handlers (to be overridden by subclasses)
    def on_start_monitoring(self):
        """Handle start monitoring button click"""
        # Check if password is set
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        if not os.path.exists(password_file):
            self.show_message(
                "Hey!",
                "Please set your password, and I'll enjoy some biryani 🍚.\nBy the way, do you like biryani as well?",
                "info"
            )
            return
        
        # Check if any apps are added
        if not self.app_list_widget.apps_data:
            self.show_message(
                "No Applications",
                "Please add applications to monitor first.",
                "info"
            )
            return
        
        # Prepare applications list for monitoring
        applications = []
        for app_name, app_data in self.app_list_widget.apps_data.items():
            applications.append({
                'name': app_name,
                'path': app_data['path']
            })
        
        print(f"\n🚀 Starting monitoring for {len(applications)} applications...")
        for app in applications:
            print(f"   📦 {app['name']}: {app['path']}")
        
        # Initialize UnifiedMonitor
        from core.unified_monitor import UnifiedMonitor
        
        self.unified_monitor = UnifiedMonitor(
            get_state_func=self.get_monitoring_state,
            set_state_func=self.set_monitoring_state,
            show_dialog_func=self.show_password_prompt_for_app,
            is_linux=True,  # TODO: Platform detection
            sleep_interval=1.0,
            enable_profiling=True
        )
        
        # Start monitoring
        self.unified_monitor.start_monitoring(applications)
        self.monitoring_active = True
        
        # Update UI
        if self.system_tray:
            self.system_tray.set_monitoring_active(True)
            self.system_tray.show_message(
                "Monitoring Started",
                f"FadCrypt is now monitoring {len(applications)} application(s).",
                QSystemTrayIcon.MessageIcon.Information
            )
        
        # Hide to tray
        self.hide_to_tray()
        
        print(f"✅ Monitoring started successfully for {len(applications)} apps")
        
    def on_stop_monitoring(self):
        """Handle stop monitoring button click"""
        if not self.monitoring_active:
            self.show_message("Info", "Monitoring is not running.", "info")
            return
        
        # Ask for password
        from ui.dialogs.password_dialog import ask_password
        password = ask_password(
            "Stop Monitoring",
            "Enter your password to stop monitoring:",
            self.resource_path,
            style=self.password_dialog_style,
            wallpaper=self.wallpaper_choice,
            parent=self
        )
        
        if password and self.password_manager.verify_password(password):
            # Stop monitoring
            if self.unified_monitor:
                self.unified_monitor.stop_monitoring()
                print("🛑 Monitoring stopped successfully")
            
            self.monitoring_active = False
            
            # Update UI
            if self.system_tray:
                self.system_tray.set_monitoring_active(False)
            
            # Show window
            self.show_window_from_tray()
            
            self.show_message(
                "Success",
                "Monitoring stopped successfully.",
                "success"
            )
        else:
            self.show_message(
                "Error",
                "Incorrect password. Monitoring will continue.",
                "error"
            )
    
    def get_monitoring_state(self):
        """Get current monitoring state for UnifiedMonitor"""
        return self.monitoring_state.copy()
    
    def set_monitoring_state(self, key, value):
        """Save monitoring state"""
        self.monitoring_state[key] = value
        self.save_monitoring_state()
        print(f"💾 State saved: {key} = {value}")
    
    def save_monitoring_state(self):
        """Save monitoring state to JSON file"""
        import json
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        try:
            with open(state_file, 'w') as f:
                json.dump(self.monitoring_state, f, indent=4)
        except Exception as e:
            print(f"Error saving monitoring state: {e}")
    
    def load_monitoring_state(self):
        """Load monitoring state from JSON file"""
        import json
        state_file = os.path.join(self.get_fadcrypt_folder(), 'monitoring_state.json')
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    self.monitoring_state = json.load(f)
                    print(f"Loaded monitoring state: {len(self.monitoring_state.get('unlocked_apps', []))} unlocked apps")
            else:
                self.monitoring_state = {'unlocked_apps': []}
        except Exception as e:
            print(f"Error loading monitoring state: {e}")
            self.monitoring_state = {'unlocked_apps': []}
    
    def show_password_prompt_for_app(self, app_name, app_path):
        """Show password prompt when blocked app is detected (called from monitoring thread)"""
        print(f"\n🔒 Blocked app detected: {app_name}")
        print(f"   Path: {app_path}")
        
        # Emit signal to show dialog in main thread (thread-safe)
        self.pending_password_result = None
        self.password_prompt_requested.emit(app_name, app_path)
        
        # Wait for result (blocking the monitoring thread until password is entered)
        import time
        timeout = 60  # 60 second timeout
        elapsed = 0
        while self.pending_password_result is None and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1
        
        result = self.pending_password_result
        self.pending_password_result = None
        return result if result is not None else False
    
    def show_password_prompt_for_app_sync(self, app_name, app_path):
        """Show password dialog in main thread (thread-safe)"""
        from ui.dialogs.password_dialog import ask_password
        
        password = ask_password(
            f"Unlock {app_name}",
            f"Application '{app_name}' is locked.\n\nEnter your password to unlock it:",
            self.resource_path,
            style=self.password_dialog_style,
            wallpaper=self.wallpaper_choice,
            parent=self
        )
        
        if password and self.password_manager.verify_password(password):
            print(f"✅ Password correct - Unlocking {app_name}")
            
            # Increment unlock count
            if app_name in self.app_list_widget.apps_data:
                self.app_list_widget.apps_data[app_name]['unlock_count'] = \
                    self.app_list_widget.apps_data[app_name].get('unlock_count', 0) + 1
                self.save_applications_config()
            
            self.pending_password_result = True
        else:
            print(f"❌ Password incorrect - Keeping {app_name} locked")
            self.pending_password_result = False
        
    def on_readme_clicked(self):
        """Handle Read Me button click - show fullscreen dialog"""
        readme_dialog = ReadmeDialog(self.resource_path, self)
        readme_dialog.exec()
        
    def on_create_password(self):
        """Handle create password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        print(f"\n🔐 Create Password Request")
        print(f"   Checking password file: {password_file}")
        print(f"   File exists: {os.path.exists(password_file)}")
        
        if os.path.exists(password_file):
            print(f"   ⚠️  Password file already exists, cannot create")
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
                    print(f"   Creating password file at: {password_file}")
                    self.password_manager.create_password(password)
                    print(f"   ✅ Password created successfully")
                    self.show_message("Success", "Password created successfully.", "success")
                except Exception as e:
                    print(f"   ❌ Error creating password: {e}")
                    self.show_message("Error", f"Failed to create password:\n{e}", "error")
        
    def on_change_password(self):
        """Handle change password button click"""
        password_file = os.path.join(self.get_fadcrypt_folder(), "encrypted_password.bin")
        
        print(f"\n🔄 Change Password Request")
        print(f"   Checking password file: {password_file}")
        print(f"   File exists: {os.path.exists(password_file)}")
        
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
                print(f"   ✅ Old password verified")
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
                        print(f"   Changing password at: {password_file}")
                        self.password_manager.change_password(old_password, new_password)
                        print(f"   ✅ Password changed successfully")
                        self.show_message("Success", "Password changed successfully.", "success")
                    except Exception as e:
                        print(f"   ❌ Error changing password: {e}")
                        self.show_message("Error", f"Failed to change password:\n{e}", "error")
            else:
                print(f"   ❌ Old password verification failed")
                self.show_message("Error", "Incorrect old password.", "error")
        else:
            print(f"   ⚠️  No password file found")
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
                # Build applications list from current data
                applications = []
                for app_name, app_data in self.app_list_widget.apps_data.items():
                    applications.append({
                        'name': app_name,
                        'path': app_data['path'],
                        'unlock_count': app_data.get('unlock_count', 0),
                        'date_added': app_data.get('date_added', None)
                    })
                
                # Export configuration with all data
                config_data = {
                    'version': self.version,
                    'settings': self.settings_panel.get_settings() if hasattr(self, 'settings_panel') else {},
                    'applications': applications
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
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                
                # Validate config structure
                if 'applications' not in config_data:
                    self.show_message("Error", "Invalid configuration file: missing 'applications' key", "error")
                    return
                
                # Clear current applications
                self.app_list_widget.apps_data.clear()
                
                # Import applications
                imported_count = 0
                for app in config_data.get('applications', []):
                    app_name = app.get('name')
                    app_path = app.get('path')
                    
                    if app_name and app_path:
                        self.app_list_widget.add_app(
                            app_name,
                            app_path,
                            unlock_count=app.get('unlock_count', 0),
                            date_added=app.get('date_added', None)
                        )
                        imported_count += 1
                
                # Save the imported config
                self.save_applications_config()
                self.update_app_count()
                
                self.show_message("Success", f"Imported {imported_count} application(s) from:\n{file_path}", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to import configuration:\n{e}", "error")
