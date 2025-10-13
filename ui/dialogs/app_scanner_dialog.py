"""
App Scanner Dialog - Scan system for installed applications
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QFrame,
    QCheckBox, QProgressDialog, QMessageBox, QGridLayout,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os
import sys
from typing import List, Dict, Optional


class AppScannerThread(QThread):
    """Background thread for scanning installed applications."""
    
    scan_complete = pyqtSignal(list)  # List of found apps
    scan_progress = pyqtSignal(str)  # Progress message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        """Scan system for installed applications."""
        self.scan_progress.emit("Scanning system...")
        apps = self.scan_installed_applications()
        self.scan_complete.emit(apps)
    
    def scan_installed_applications(self) -> List[Dict[str, str]]:
        """Scan system for installed applications (cross-platform)."""
        apps = []
        
        if sys.platform.startswith('linux'):
            apps = self._scan_linux_applications()
        elif sys.platform.startswith('win'):
            apps = self._scan_windows_applications()
        else:
            apps = self._scan_macos_applications()
        
        return apps
    
    def _scan_linux_applications(self) -> List[Dict[str, str]]:
        """Scan Linux system for applications."""
        apps = []
        desktop_dirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]
        
        self.scan_progress.emit(f"Scanning {len(desktop_dirs)} directories...")
        
        for desktop_dir in desktop_dirs:
            if not os.path.exists(desktop_dir):
                continue
            
            try:
                for filename in os.listdir(desktop_dir):
                    if not filename.endswith('.desktop'):
                        continue
                    
                    desktop_file = os.path.join(desktop_dir, filename)
                    app_info = self._parse_desktop_file(desktop_file)
                    
                    if app_info and app_info['name'] and app_info['path']:
                        # Avoid duplicates
                        if not any(app['name'] == app_info['name'] for app in apps):
                            apps.append(app_info)
                            self.scan_progress.emit(f"Found: {app_info['name']}")
            except (PermissionError, OSError) as e:
                print(f"[Scanner] Error scanning {desktop_dir}: {e}")
        
        return sorted(apps, key=lambda x: x['name'].lower())
    
    def _parse_desktop_file(self, desktop_file: str) -> Optional[Dict[str, str]]:
        """Parse a .desktop file and extract app info."""
        try:
            with open(desktop_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            name = None
            exec_path = None
            icon = None
            categories = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('Name=') and not name:
                    name = line.split('=', 1)[1]
                elif line.startswith('Exec='):
                    exec_cmd = line.split('=', 1)[1]
                    # Remove field codes (%f, %F, %u, %U, etc.)
                    exec_cmd = exec_cmd.split('%')[0].strip()
                    # Get first command (ignore arguments)
                    exec_path = exec_cmd.split()[0] if exec_cmd else None
                elif line.startswith('Icon='):
                    icon = line.split('=', 1)[1]
                elif line.startswith('Categories='):
                    cat_line = line.split('=', 1)[1]
                    categories = [c.strip() for c in cat_line.split(';') if c.strip()]
            
            if name and exec_path:
                # Determine primary category
                category = self._categorize_app(categories)
                
                return {
                    'name': name,
                    'path': exec_path,
                    'icon': icon or '',
                    'category': category,
                    'desktop_file': desktop_file
                }
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"[Scanner] Error parsing {desktop_file}: {e}")
        
        return None
    
    def _categorize_app(self, categories: List[str]) -> str:
        """Categorize app based on .desktop Categories field"""
        # Category mapping (first match wins)
        category_map = {
            'Internet': ['Network', 'WebBrowser', 'Email', 'Chat', 'InstantMessaging'],
            'Development': ['Development', 'IDE', 'Debugger', 'GUIDesigner'],
            'Graphics': ['Graphics', 'Photography', 'RasterGraphics', 'VectorGraphics', '2DGraphics', '3DGraphics'],
            'Multimedia': ['AudioVideo', 'Audio', 'Video', 'Player', 'Recorder'],
            'Office': ['Office', 'WordProcessor', 'Spreadsheet', 'Presentation', 'Database'],
            'System': ['System', 'Settings', 'Monitor', 'Security', 'PackageManager'],
            'Games': ['Game', 'ActionGame', 'AdventureGame', 'ArcadeGame', 'BoardGame', 'CardGame'],
            'Utilities': ['Utility', 'Archiving', 'Compression', 'FileTools', 'TextEditor'],
            'Education': ['Education', 'Science', 'Math', 'Languages'],
        }
        
        for category, keywords in category_map.items():
            if any(kw in categories for kw in keywords):
                return category
        
        return 'Other'
    
    def _scan_windows_applications(self) -> List[Dict[str, str]]:
        """Scan Windows system for applications."""
        # Placeholder - Windows implementation
        return []
    
    def _scan_macos_applications(self) -> List[Dict[str, str]]:
        """Scan macOS system for applications."""
        # Placeholder - macOS implementation
        return []


class AppCard(QFrame):
    """Card widget for displaying a scanned application."""
    
    toggled = pyqtSignal(bool)  # Emitted when card is clicked
    
    def __init__(self, app_data: Dict[str, str], parent=None):
        super().__init__(parent)
        
        self.app_data = app_data
        self.checkbox = None
        self._is_checked = False
        
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Hand cursor on hover
        self.setStyleSheet("""
            AppCard {
                background-color: #353749;
                border: 2px solid #4a4c5e;
                border-radius: 10px;
                padding: 12px;
            }
            AppCard:hover {
                background-color: #404050;
                border: 2px solid #3b82f6;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize card UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Checkbox + Icon + Name
        header_layout = QHBoxLayout()
        
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(False)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 1px solid #9ca3af;
                border-radius: 4px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border: 1px solid #2563eb;
            }
            QCheckBox::indicator:unchecked {
                background-color: transparent;
            }
            QCheckBox {
                background-color: transparent;
                color: #e5e7eb;
            }
        """)
        # Connect checkbox signal but don't let it stop event propagation
        self.checkbox.stateChanged.connect(lambda state: self._on_checkbox_changed(state))
        header_layout.addWidget(self.checkbox)
        
        # App icon
        icon_label = QLabel()
        icon_pixmap = self.load_app_icon()
        if icon_pixmap:
            icon_label.setPixmap(icon_pixmap.scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            icon_label.setStyleSheet("background-color: transparent;")
        else:
            # Fallback emoji based on category
            category_emoji = {
                'Internet': '🌐',
                'Development': '💻',
                'Graphics': '🎨',
                'Multimedia': '🎵',
                'Office': '📝',
                'System': '⚙️',
                'Games': '🎮',
                'Utilities': '🔧',
                'Education': '📚',
                'Other': '📦'
            }
            emoji = category_emoji.get(self.app_data.get('category', 'Other'), '📦')
            icon_label.setText(emoji)
            icon_label.setStyleSheet("font-size: 36px; background-color: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # App name and category
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name_label = QLabel(self.app_data['name'])
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #e5e7eb; background-color: transparent;")
        name_label.setWordWrap(True)
        text_layout.addWidget(name_label)
        
        # Category badge
        category = self.app_data.get('category', 'Other')
        category_label = QLabel(f"📂 {category}")
        category_label.setStyleSheet("""
            color: #93c5fd;
            font-size: 9px;
            padding: 2px 6px;
            background-color: transparent;
            border-radius: 8px;
        """)
        text_layout.addWidget(category_label)
        
        header_layout.addLayout(text_layout, stretch=1)
        layout.addLayout(header_layout)
        
        # Path
        path_label = QLabel(f"📁 {self.app_data['path']}")
        path_label.setStyleSheet("color: #9ca3af; font-size: 10px; background-color: transparent;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        self.setLayout(layout)
    
    def load_app_icon(self) -> Optional[QPixmap]:
        """Load application icon from system."""
        icon_name = self.app_data.get('icon', '')
        if not icon_name:
            return None
        
        # Try common icon paths
        icon_paths = [
            f"/usr/share/pixmaps/{icon_name}.png",
            f"/usr/share/pixmaps/{icon_name}.svg",
            f"/usr/share/pixmaps/{icon_name}.xpm",
            f"/usr/share/icons/hicolor/48x48/apps/{icon_name}.png",
            f"/usr/share/icons/hicolor/scalable/apps/{icon_name}.svg",
            icon_name if icon_name.startswith('/') else None
        ]
        
        for path in icon_paths:
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap
        
        return None
    
    def _on_checkbox_changed(self, state):
        """Handle checkbox state change programmatically"""
        self._is_checked = (state == Qt.CheckState.Checked.value)
        self.update_style()
        self.toggled.emit(self._is_checked)
    
    def mousePressEvent(self, event):
        """Handle mouse press - toggle checkbox when card is clicked"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle checkbox
            self._is_checked = not self._is_checked
            if self.checkbox:
                self.checkbox.setChecked(self._is_checked)
            self.update_style()
            self.toggled.emit(self._is_checked)
        super().mousePressEvent(event)
    
    def update_style(self):
        """Update card style based on checked state"""
        if self._is_checked:
            self.setStyleSheet("""
                AppCard {
                    background-color: #1e3a5f;
                    border: 2px solid #3b82f6;
                    border-radius: 10px;
                    padding: 12px;
                }
                AppCard:hover {
                    background-color: #2d4a6f;
                    border: 2px solid #60a5fa;
                }
            """)
        else:
            self.setStyleSheet("""
                AppCard {
                    background-color: #353749;
                    border: 2px solid #4a4c5e;
                    border-radius: 10px;
                    padding: 12px;
                }
                AppCard:hover {
                    background-color: #404050;
                    border: 2px solid #3b82f6;
                }
            """)
    
    def is_checked(self) -> bool:
        """Check if this app is selected."""
        return self._is_checked


class AppScannerDialog(QDialog):
    """
    Dialog for scanning and batch-adding installed applications.
    
    Shows a grid of found applications with checkboxes.
    User can select multiple apps to add at once.
    
    Signals:
        apps_selected: Emitted when user selects apps (list of app dicts)
    """
    
    apps_selected = pyqtSignal(list)  # List of selected app dicts
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Scan for Applications")
        self.setModal(True)
        self.columns = 4
        self.setMinimumSize(1400, 700)  # Wider to fit 4 columns without scrollbar

        # Apply dark theme and make input backgrounds transparent for consistency
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2d3a;
            }
            QLabel {
                color: #e5e7eb;
                background-color: transparent;
            }
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: transparent;
                color: #e5e7eb;
                border: 1px solid #3b3f46;
            }
            QPushButton {
                background-color: transparent;
                color: #e5e7eb;
                border: 1px solid #3b3f46;
            }
            QCheckBox, QRadioButton {
                background-color: transparent;
                color: #e5e7eb;
            }
            QScrollArea {
                background-color: transparent;
            }
        """)

        self.scanned_apps = []
        self.app_cards = []

        self.init_ui()
        self.center_on_screen()

        # Start scanning automatically
        self.start_scan()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔍 Scan System for Applications")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Scanning system...")
        self.status_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.status_label)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_label = QLabel("🔎 Search:")
        search_label.setStyleSheet("font-weight: bold; color: #e5e7eb;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter applications...")
        self.search_input.textChanged.connect(self.filter_apps)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #44464f;
                border-radius: 6px;
                background-color: transparent;
                color: #e5e7eb;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        search_layout.addWidget(self.search_input, stretch=1)
        # Prefer translucent background where supported
        try:
            self.search_input.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.search_input.setAutoFillBackground(False)
        except Exception:
            pass
        
        self.clear_search_btn = QPushButton("✕ Clear")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e5e7eb;
                border: 1px solid #44464f;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3b3f46;
            }
            QPushButton:pressed {
                background-color: #32353a;
            }
        """)
        search_layout.addWidget(self.clear_search_btn)
        try:
            self.clear_search_btn.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.clear_search_btn.setAutoFillBackground(False)
        except Exception:
            pass
        
        layout.addLayout(search_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Scroll area for app cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_widget")
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QGridLayout()
        self.scroll_layout.setSpacing(15)
        # Make columns stretch equally so cards are evenly sized
        for i in range(self.columns):
            self.scroll_layout.setColumnStretch(i, 1)
        self.scroll_widget.setLayout(self.scroll_layout)
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll, stretch=1)
        
        # Selection counter
        self.selection_label = QLabel("0 apps selected")
        self.selection_label.setStyleSheet("""
            color: #3b82f6;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
            background-color: transparent;
        """)
        self.selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.selection_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Select/Deselect buttons
        self.select_all_btn = QPushButton("☑️ Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        button_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("☐ Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        button_layout.addWidget(self.deselect_all_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Add Selected button
        self.add_btn = QPushButton("➕ Add Selected")
        self.add_btn.clicked.connect(self.add_selected_apps)
        self.add_btn.setEnabled(False)
        self.add_btn.setDefault(True)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #009E60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 140px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #00b56f;
            }
            QPushButton:pressed {
                background-color: #008852;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_scan(self):
        """Start scanning for applications in background thread."""
        self.scanner_thread = AppScannerThread(self)
        self.scanner_thread.scan_progress.connect(self.update_progress)
        self.scanner_thread.scan_complete.connect(self.display_results)
        self.scanner_thread.start()
    
    def update_progress(self, message: str):
        """Update progress label."""
        self.status_label.setText(message)
    
    def display_results(self, apps: List[Dict[str, str]]):
        """Display scanned applications in grid."""
        self.scanned_apps = apps
        
        if not apps:
            self.status_label.setText("❌ No applications found")
            return
        
        self.status_label.setText(f"✅ Found {len(apps)} applications - Select apps to add:")
        
        # Clear previous cards
        for card in self.app_cards:
            card.deleteLater()
        self.app_cards.clear()
        
        # Create cards in grid (N columns)
        row = 0
        col = 0
        for app in apps:
            card = AppCard(app, self)
            card.toggled.connect(lambda checked: self.update_selection_count())
            self.scroll_layout.addWidget(card, row, col)
            self.app_cards.append(card)
            
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
        
        # Enable add button
        self.add_btn.setEnabled(True)
    
    def filter_apps(self, search_text: str):
        """Filter displayed apps based on search text."""
        search_text = search_text.lower().strip()
        
        visible_count = 0
        row = 0
        col = 0
        
        for card in self.app_cards:
            app_name = card.app_data.get('name', '').lower()
            app_path = card.app_data.get('path', '').lower()
            app_category = card.app_data.get('category', '').lower()
            
            # Check if search matches name, path or category
            matches = (
                search_text in app_name or 
                search_text in app_path or 
                search_text in app_category
            )
            
            if matches or not search_text:
                card.setVisible(True)
                # Reposition visible cards
                self.scroll_layout.addWidget(card, row, col)
                visible_count += 1
                col += 1
                if col >= self.columns:
                    col = 0
                    row += 1
            else:
                card.setVisible(False)
        
        # Update status
        if search_text:
            self.status_label.setText(
                f"🔍 Showing {visible_count} of {len(self.scanned_apps)} applications"
            )
        else:
            self.status_label.setText(
                f"✅ Found {len(self.scanned_apps)} applications - Select apps to add:"
            )
    
    def clear_search(self):
        """Clear search input and show all apps."""
        self.search_input.clear()
    
    def update_selection_count(self):
        """Update the selection counter label."""
        selected_count = sum(1 for card in self.app_cards if card.is_checked())
        if selected_count == 0:
            self.selection_label.setText("0 apps selected")
            self.selection_label.setStyleSheet("""
                color: #6b7280;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
                background-color: transparent;
            """)
        else:
            self.selection_label.setText(f"✓ {selected_count} app{'s' if selected_count != 1 else ''} selected")
            self.selection_label.setStyleSheet("""
                color: #009E60;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
                background-color: transparent;
            """)
    
    def select_all(self):
        """Select all application cards."""
        for card in self.app_cards:
            if card.checkbox:
                card.checkbox.setChecked(True)
        self.update_selection_count()
    
    def deselect_all(self):
        """Deselect all application cards."""
        for card in self.app_cards:
            if card.checkbox:
                card.checkbox.setChecked(False)
        self.update_selection_count()
    
    def add_selected_apps(self):
        """Emit signal with selected apps and close dialog."""
        selected_apps = []
        
        for card in self.app_cards:
            if card.is_checked():
                selected_apps.append(card.app_data)
        
        if not selected_apps:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one application to add."
            )
            return
        
        print(f"[AppScanner] User selected {len(selected_apps)} apps to add")
        self.apps_selected.emit(selected_apps)
        self.accept()
    
    def center_on_screen(self):
        """Center dialog on screen."""
        from PyQt6.QtWidgets import QApplication
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_x = screen_geometry.x()
            screen_y = screen_geometry.y()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            dialog_width = self.width()
            dialog_height = self.height()
            
            center_x = screen_x + (screen_width - dialog_width) // 2
            center_y = screen_y + (screen_height - dialog_height) // 2
            
            self.move(center_x, center_y)
