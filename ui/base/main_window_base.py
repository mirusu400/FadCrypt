"""
Base Main Window for FadCrypt
Platform-agnostic PyQt6 main window implementation
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QLabel, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
import os


class MainWindowBase(QMainWindow):
    """
    Base main window class for FadCrypt application.
    
    This class provides the foundation for the FadCrypt UI with:
    - Main window setup (title, icon, geometry)
    - Menu bar structure
    - Tab widget for organizing features
    - Status bar for app state
    
    Platform-specific implementations should inherit from this class
    and override methods as needed.
    """
    
    def __init__(self, app_name: str = "FadCrypt", version: str = "0.4.0"):
        """
        Initialize the main window.
        
        Args:
            app_name: Application name to display in title bar
            version: Application version string
        """
        super().__init__()
        
        self.app_name = app_name
        self.version = version
        
        # Initialize UI components
        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._create_tab_widget()
        
    def _init_ui(self):
        """Initialize basic window properties."""
        # Set window title
        self.setWindowTitle(f"{self.app_name} v{self.version}")
        
        # Set window size (same as Tkinter version: 700x650)
        self.resize(700, 650)
        
        # Center window on screen
        self._center_window()
        
        # Set fixed size (prevent resizing like Tkinter version)
        self.setFixedSize(self.size())
        
        # Set window icon (will be implemented when resource_path is available)
        # icon_path = self.resource_path("img/icon.png")
        # if os.path.exists(icon_path):
        #     self.setWindowIcon(QIcon(icon_path))
        
    def _center_window(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Import/Export actions (placeholder)
        export_action = QAction("&Export Configuration...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_config)
        file_menu.addAction(export_action)
        
        import_action = QAction("&Import Configuration...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._on_import_config)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Monitoring menu
        monitor_menu = menu_bar.addMenu("&Monitoring")
        
        self.start_monitor_action = QAction("&Start Monitoring", self)
        self.start_monitor_action.triggered.connect(self._on_start_monitoring)
        monitor_menu.addAction(self.start_monitor_action)
        
        self.stop_monitor_action = QAction("S&top Monitoring", self)
        self.stop_monitor_action.setEnabled(False)
        self.stop_monitor_action.triggered.connect(self._on_stop_monitoring)
        monitor_menu.addAction(self.stop_monitor_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About FadCrypt", self)
        about_action.triggered.connect(self._on_show_about)
        help_menu.addAction(about_action)
        
        github_action = QAction("View on &GitHub", self)
        github_action.triggered.connect(self._on_open_github)
        help_menu.addAction(github_action)
        
    def _create_status_bar(self):
        """Create the application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label (left side)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Monitoring status label (right side)
        self.monitor_status_label = QLabel("Monitoring: Not Running")
        self.status_bar.addPermanentWidget(self.monitor_status_label)
        
    def _create_tab_widget(self):
        """Create the central tab widget."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create placeholder tabs
        self._create_home_tab()
        self._create_settings_tab()
        self._create_about_tab()
        
    def _create_home_tab(self):
        """Create the Home tab (application list and controls)."""
        from ..components.app_list_widget import AppListWidget
        from ..components.button_panel import ButtonPanel
        
        home_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        home_tab.setLayout(layout)
        
        # Application list
        self.app_list = AppListWidget()
        self.app_list.app_selected.connect(self._on_app_selected)
        self.app_list.app_removed.connect(self._on_app_removed)
        self.app_list.app_lock_toggled.connect(self._on_app_lock_toggled)
        layout.addWidget(self.app_list)
        
        # Button panel
        self.button_panel = ButtonPanel()
        self.button_panel.add_app_clicked.connect(self._on_add_app_clicked)
        self.button_panel.lock_all_clicked.connect(self._on_lock_all_clicked)
        self.button_panel.unlock_all_clicked.connect(self._on_unlock_all_clicked)
        layout.addWidget(self.button_panel)
        
        self.tab_widget.addTab(home_tab, "Home")
        
    def _create_settings_tab(self):
        """Create the Settings tab."""
        from ..components.settings_panel import SettingsPanel
        
        self.settings_panel = SettingsPanel()
        self.settings_panel.lock_tools_changed.connect(self._on_lock_tools_changed)
        self.settings_panel.dialog_style_changed.connect(self._on_dialog_style_changed)
        self.settings_panel.wallpaper_changed.connect(self._on_wallpaper_changed)
        self.settings_panel.autostart_changed.connect(self._on_autostart_changed)
        self.settings_panel.change_password_clicked.connect(self._on_change_password_clicked)
        
        self.tab_widget.addTab(self.settings_panel, "Settings")
        
    def _create_about_tab(self):
        """Create the About tab."""
        from ..components.about_panel import AboutPanel
        
        self.about_panel = AboutPanel(self.version, version_code=3)
        self.tab_widget.addTab(self.about_panel, "About")
        
    # ========== Menu Action Handlers (Placeholder) ==========
    
    def _on_app_selected(self, app_name: str, app_path: str):
        """Handle app selection in list."""
        self.status_label.setText(f"Selected: {app_name}")
    
    def _on_app_removed(self, app_name: str):
        """Handle app removal."""
        self.status_label.setText(f"Removed: {app_name}")
    
    def _on_app_lock_toggled(self, app_name: str, is_locked: bool):
        """Handle lock status toggle."""
        status = "locked" if is_locked else "unlocked"
        self.status_label.setText(f"{app_name} {status}")
    
    def _on_add_app_clicked(self):
        """Handle add application button."""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Executables (*);;All Files (*)"
        )
        if file_path:
            import os
            app_name = os.path.basename(file_path)
            self.app_list.add_app(app_name, file_path, is_locked=True)
            self.status_label.setText(f"Added: {app_name}")
    
    def _on_lock_all_clicked(self):
        """Handle lock all button."""
        for app in self.app_list.get_all_apps():
            self.app_list.update_app_status(app['name'], True)
        self.status_label.setText("All applications locked")
    
    def _on_unlock_all_clicked(self):
        """Handle unlock all button."""
        for app in self.app_list.get_all_apps():
            self.app_list.update_app_status(app['name'], False)
        self.status_label.setText("All applications unlocked")
    
    def _on_lock_tools_changed(self, enabled: bool):
        """Handle lock system tools setting change."""
        self.status_label.setText(f"Lock system tools: {'enabled' if enabled else 'disabled'}")
    
    def _on_dialog_style_changed(self, style: str):
        """Handle dialog style change."""
        self.status_label.setText(f"Dialog style: {style}")
    
    def _on_wallpaper_changed(self, wallpaper: str):
        """Handle wallpaper choice change."""
        self.status_label.setText(f"Wallpaper: {wallpaper}")
    
    def _on_autostart_changed(self, enabled: bool):
        """Handle autostart setting change."""
        self.status_label.setText(f"Autostart: {'enabled' if enabled else 'disabled'}")
    
    def _on_change_password_clicked(self):
        """Handle change password button."""
        from PyQt6.QtWidgets import QMessageBox
        from ..dialogs.password_dialog import ChangePasswordDialog
        
        dialog = ChangePasswordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            old_pwd, new_pwd = dialog.get_passwords()
            # TODO: Actually change password using PasswordManager
            QMessageBox.information(
                self,
                "Success",
                "Password changed successfully!\n(Not implemented yet - Phase 5)"
            )
            self.status_label.setText("Password changed")
        else:
            self.status_label.setText("Password change cancelled")
    
    # ========== Original Menu Handlers ==========
    
    def _on_export_config(self):
        """Handle export configuration action."""
        self.status_label.setText("Export configuration (not implemented)")
        
    def _on_import_config(self):
        """Handle import configuration action."""
        self.status_label.setText("Import configuration (not implemented)")
        
    def _on_start_monitoring(self):
        """Handle start monitoring action."""
        self.start_monitor_action.setEnabled(False)
        self.stop_monitor_action.setEnabled(True)
        self.monitor_status_label.setText("Monitoring: Running")
        self.status_label.setText("Monitoring started")
        
    def _on_stop_monitoring(self):
        """Handle stop monitoring action."""
        self.start_monitor_action.setEnabled(True)
        self.stop_monitor_action.setEnabled(False)
        self.monitor_status_label.setText("Monitoring: Stopped")
        self.status_label.setText("Monitoring stopped")
        
    def _on_show_about(self):
        """Handle show about dialog action."""
        self.status_label.setText("About FadCrypt")
        
    def _on_open_github(self):
        """Handle open GitHub repository action."""
        import webbrowser
        webbrowser.open("https://github.com/anonfaded/FadCrypt")
        self.status_label.setText("Opening GitHub repository...")
        
    # ========== Public Methods ==========
    
    def update_status(self, message: str):
        """
        Update the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        
    def update_monitoring_status(self, is_running: bool, app_count: int = 0):
        """
        Update the monitoring status display.
        
        Args:
            is_running: Whether monitoring is currently active
            app_count: Number of apps being monitored
        """
        if is_running:
            self.monitor_status_label.setText(f"Monitoring: {app_count} app(s)")
        else:
            self.monitor_status_label.setText("Monitoring: Not Running")
