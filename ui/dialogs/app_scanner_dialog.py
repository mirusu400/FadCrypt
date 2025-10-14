"""
App Scanner Dialog - Scan system for installed applications
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QFrame,
    QCheckBox, QProgressDialog, QMessageBox, QGridLayout,
    QLineEdit, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon, QFontMetrics
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
        apps = []
        program_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expanduser(r"~\AppData\Local\Programs")
        ]
        
        self.scan_progress.emit(f"Scanning {len(program_dirs)} directories...")
        
        for prog_dir in program_dirs:
            if not os.path.exists(prog_dir):
                continue
            
            self.scan_progress.emit(f"Scanning {prog_dir}...")
            
            try:
                for root, dirs, files in os.walk(prog_dir):
                    for file in files:
                        if file.endswith('.exe'):
                            filepath = os.path.join(root, file)
                            name = os.path.splitext(file)[0]
                            
                            # Skip system files and installers
                            if any(skip in name.lower() for skip in ['unins', 'uninst', 'setup', 'install']):
                                continue
                            
                            # Avoid duplicates
                            if not any(app['name'] == name for app in apps):
                                apps.append({
                                    'name': name,
                                    'path': filepath,
                                    'icon': filepath,  # Windows can extract icon from .exe
                                    'category': self._categorize_windows_app(filepath),
                                    'desktop_file': ''
                                })
                                self.scan_progress.emit(f"Found: {name}")
            except (PermissionError, OSError) as e:
                print(f"[Scanner] Error scanning {prog_dir}: {e}")
        
        return sorted(apps, key=lambda x: x['name'].lower())
    
    def _categorize_windows_app(self, filepath: str) -> str:
        """Categorize Windows app based on install location"""
        filepath_lower = filepath.lower()
        
        if 'steam' in filepath_lower or 'games' in filepath_lower:
            return 'Games'
        elif 'microsoft office' in filepath_lower or 'libreoffice' in filepath_lower:
            return 'Office'
        elif any(x in filepath_lower for x in ['chrome', 'firefox', 'edge', 'browser']):
            return 'Internet'
        elif any(x in filepath_lower for x in ['vscode', 'visual studio', 'pycharm', 'intellij', 'eclipse']):
            return 'Development'
        elif any(x in filepath_lower for x in ['photoshop', 'gimp', 'paint', 'illustrator']):
            return 'Graphics'
        elif any(x in filepath_lower for x in ['vlc', 'media', 'spotify', 'itunes', 'winamp']):
            return 'Multimedia'
        elif 'system32' in filepath_lower or 'windows' in filepath_lower:
            return 'System'
        else:
            return 'Other'
    
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
        # Prefer fixed size behavior so all cards are uniform
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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

        # Truncate long names to keep card heights consistent
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        fm = QFontMetrics(name_font)
        elided_name = fm.elidedText(self.app_data.get('name', ''), Qt.TextElideMode.ElideRight, 200)
        name_label = QLabel(elided_name)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #e5e7eb; background-color: transparent;")
        name_label.setWordWrap(False)
        name_label.setMaximumHeight(fm.height() * 2)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
        header_layout.addLayout(text_layout)
        layout.addLayout(header_layout)

        # Path label - single line elided to avoid changing card height
        path_text = self.app_data.get('path', '')
        pm = QFontMetrics(self.font())
        elided_path = pm.elidedText(path_text, Qt.TextElideMode.ElideRight, 260)
        path_label = QLabel(elided_path)
        path_label.setStyleSheet("color: #9ca3af; font-size: 10px; background-color: transparent;")
        path_label.setWordWrap(False)
        path_label.setMaximumHeight(pm.height())
        path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
        # Use a reasonable default minimum size (restore original)
        self.setMinimumSize(800, 600)
        # Default to 3 columns on open (responsive resizing will reflow)
        self.columns = 3

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
        # Current category/tag filter (None = show all)
        self.category_filter = None
        # Track if we've centered on first show (for Wayland compatibility)
        self._first_show = True

        self.init_ui()
        # Don't center here - will center on showEvent after dialog has proper size

        # Start scanning automatically
        self.start_scan()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        # Make overall dialog more compact
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        
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
        search_layout.setSpacing(8)
        
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

        # Category/tag bar (populated after scan)
        self.tag_bar_widget = QWidget()
        self.tag_bar_layout = QHBoxLayout()
        # Slightly tighter tag spacing for compactness
        self.tag_bar_layout.setSpacing(6)
        self.tag_bar_layout.setContentsMargins(0, 4, 0, 4)
        self.tag_bar_widget.setLayout(self.tag_bar_layout)
        self.tag_bar_widget.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.tag_bar_widget)

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
    # Slightly tighter grid spacing to make the area more compact
        self.scroll_layout.setSpacing(12)
        self.scroll_widget.setLayout(self.scroll_layout)
        # keep a reference to the scroll area so we can use its viewport width for responsive math
        self.scroll_area = scroll
        # Initialize column stretch to default columns so layout is balanced on open
        for i in range(self.columns):
            try:
                self.scroll_layout.setColumnStretch(i, 1)
            except Exception:
                pass
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll, stretch=1)
        # keep a reference to the scroll area so we can use its viewport width for responsive math
        self.scroll_area = scroll

        # Debounce timer for resize events to avoid jitter while dragging
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_debounced)
            
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
                padding: 8px 14px;
                font-size: 13px;
                min-width: 90px;
                min-height: 32px;
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
                padding: 8px 14px;
                font-size: 13px;
                min-width: 100px;
                min-height: 32px;
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
                padding: 8px 14px;
                font-size: 13px;
                min-width: 90px;
                min-height: 32px;
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
                padding: 8px 14px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
                min-height: 32px;
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
        # Ensure layout is computed after widgets are shown/laid out
        try:
            QTimer.singleShot(50, self._ensure_layout)
        except Exception:
            pass
    
    def compute_columns(self) -> int:
        """Compute number of columns that fit in the current scroll area width.

        Returns between 1 and 4.
        """
        try:
            # Prefer scroll area viewport width when available (more accurate during resize)
            try:
                available = (self.scroll_area.viewport().width() if getattr(self, 'scroll_area', None) is not None else self.scroll_widget.width()) or self.width()
            except Exception:
                available = self.scroll_widget.width() or self.width()
            # Estimate usable width: subtract margins/padding conservatively
            usable = max(200, available - 80)
            card_w = 300  # estimated card width including spacing
            cols = max(1, min(4, usable // card_w))
            return int(cols)
        except Exception:
            return 3

    def resizeEvent(self, event):
        """On resize, recompute columns and relayout cards."""
        super().resizeEvent(event)
        # Start debounce timer and defer actual re-layout to avoid repeated layout thrash while resizing
        try:
            self._resize_timer.start(120)
        except Exception:
            # fallback to immediate behavior if timer fails
            new_cols = self.compute_columns()
            if getattr(self, 'columns', None) != new_cols:
                self.columns = new_cols
                for i in range(4):
                    self.scroll_layout.setColumnStretch(i, 1 if i < self.columns else 0)
                self._relayout_cards()

    def _on_resize_debounced(self):
        """Handle deferred resize: compute columns and relayout once user stops/pauses resizing."""
        try:
            new_cols = self.compute_columns()
            if getattr(self, 'columns', None) != new_cols:
                self.columns = new_cols
                for i in range(4):
                    self.scroll_layout.setColumnStretch(i, 1 if i < self.columns else 0)
                self._relayout_cards()
        except Exception:
            pass

    def _relayout_cards(self):
        """Reposition existing cards according to current column count."""
        # Remove all widgets from layout first (detach them)
        # Note: we don't delete widgets, just remove them from layout so we can re-add
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget:
                try:
                    self.scroll_layout.removeWidget(widget)
                except Exception:
                    pass
        row = 0
        col = 0
        for card in self.app_cards:
            try:
                self.scroll_layout.addWidget(card, row, col, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter))
            except Exception:
                self.scroll_layout.addWidget(card, row, col)
            col += 1
            if col >= self.columns:
                col = 0
                row += 1

    def _ensure_layout(self):
        """Ensure columns are computed and cards relaid out once the dialog is shown."""
        try:
            new_cols = self.compute_columns()
            if getattr(self, 'columns', None) != new_cols:
                self.columns = new_cols
                for i in range(4):
                    self.scroll_layout.setColumnStretch(i, 1 if i < self.columns else 0)
            if self.app_cards:
                self._relayout_cards()
        except Exception:
            pass

    def _populate_category_tags(self):
        """Create tag buttons from scanned app categories."""
        # Clear previous
        for i in reversed(range(self.tag_bar_layout.count())):
            item = self.tag_bar_layout.takeAt(i)
            if not item:
                continue
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 'All' button
        all_btn = QPushButton("All")
        all_btn.setCheckable(True)
        all_btn.setChecked(self.category_filter is None)
        all_btn.clicked.connect(self.clear_category_filter)
        all_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #cbd5e1; border: 1px solid #3b3f46; padding: 6px 10px; border-radius: 6px; }
            QPushButton:checked { background-color: #3b82f6; color: white; }
        """)
        self.tag_bar_layout.addWidget(all_btn)
        # Build unique categories mapping using lowercase keys -> display label
        seen = {}
        for a in self.scanned_apps:
            disp = (a.get('category', 'Other') or 'Other').strip()
            key = disp.lower()
            if key not in seen:
                seen[key] = disp

        for key, display in seen.items():
            c_lower = key
            btn = QPushButton(display)
            btn.setCheckable(True)
            btn.setChecked(self.category_filter == c_lower)
            # pass lowercase category to handler
            btn.clicked.connect(lambda checked, c=c_lower: self._on_category_clicked(c))
            btn.setStyleSheet("""
                QPushButton { background-color: transparent; color: #93c5fd; border: 1px solid #3b3f46; padding: 6px 10px; border-radius: 6px; }
                QPushButton:checked { background-color: #2563eb; color: white; }
            """)
            self.tag_bar_layout.addWidget(btn)

    def _on_category_clicked(self, category: str):
        # category is expected lowercase from the buttons
        if self.category_filter == category:
            self.category_filter = None
        else:
            self.category_filter = category
        # refresh tags and filter
        self._populate_category_tags()
        self.filter_apps(self.search_input.text())

    def clear_category_filter(self):
        self.category_filter = None
        self._populate_category_tags()
        self.filter_apps(self.search_input.text())
    
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
        # Store scanned apps and add a normalized lowercase category key for reliable filtering
        self.scanned_apps = apps
        for a in self.scanned_apps:
            a['category_lc'] = (a.get('category', 'Other') or 'Other').strip().lower()
        
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
        card_max_w = 320  # keep cards readable and prevent full-row stretching
        card_fixed_h = 140
        for app in apps:
            card = AppCard(app, self)
            # enforce fixed size so cards are uniform
            card.setFixedSize(card_max_w, card_fixed_h)

            card.toggled.connect(lambda checked: self.update_selection_count())
            # Align top+center so cards don't expand horizontally and allow multiple columns
            self.scroll_layout.addWidget(card, row, col, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter))
            self.app_cards.append(card)

            col += 1
            if col >= self.columns:
                col = 0
                row += 1
        
        # Enable add button
        self.add_btn.setEnabled(True)
        # Populate category tags for filtering
        try:
            self._populate_category_tags()
        except Exception:
            pass
        # Ensure layout recalculation now that cards exist (fix initial single-column issue)
        try:
            QTimer.singleShot(0, self._ensure_layout)
        except Exception:
            pass
    
    def filter_apps(self, search_text: str):
        """Filter displayed apps based on search text."""
        search_text = search_text.lower().strip()
        
        visible_count = 0
        row = 0
        col = 0
        # Clear existing layout placements so we can re-add visible cards
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                try:
                    self.scroll_layout.removeWidget(widget)
                except Exception:
                    pass

        for card in self.app_cards:
            app_name = card.app_data.get('name', '').lower()
            app_path = card.app_data.get('path', '').lower()
            # prefer the normalized lowercase category key when available
            app_category = card.app_data.get('category_lc', card.app_data.get('category', '')).lower()

            # Text match
            matches_text = (not search_text) or (search_text in app_name) or (search_text in app_path) or (search_text in app_category)
            # Category match
            matches_category = (not self.category_filter) or (app_category == (self.category_filter or '').lower())

            matches = matches_text and matches_category

            if matches:
                card.setVisible(True)
                # Reposition visible cards
                try:
                    self.scroll_layout.addWidget(card, row, col, alignment=(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter))
                except Exception:
                    self.scroll_layout.addWidget(card, row, col)
                visible_count += 1
                col += 1
                if col >= self.columns:
                    col = 0
                    row += 1
            else:
                card.setVisible(False)
        
        # Update status
        # Update status
        if self.category_filter:
            self.status_label.setText(f"🔖 Filter: {self.category_filter} — Showing {visible_count} of {len(self.scanned_apps)} apps")
        elif search_text:
            self.status_label.setText(f"🔍 Showing {visible_count} of {len(self.scanned_apps)} applications")
        else:
            self.status_label.setText(f"✅ Found {len(self.scanned_apps)} applications - Select apps to add:")
    
    def clear_search(self):
        """Clear search input and show all apps."""
        self.search_input.clear()
        # Clear category filter as well and refresh
        self.category_filter = None
        try:
            self._populate_category_tags()
        except Exception:
            pass
        try:
            self.filter_apps("")
        except Exception:
            pass
    
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
        """Center dialog on screen (Wayland-aware)."""
        from PyQt6.QtWidgets import QApplication
        import os
        
        # Check if running under Wayland
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        is_wayland = 'wayland' in session_type or wayland_display
        
        if is_wayland:
            # On Wayland, window positioning is controlled by the compositor
            # move() calls are ignored - the compositor will place the window
            return
        
        # X11 / Windows / macOS - we can control position
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
    
    def showEvent(self, event):
        """Override showEvent to center dialog after it has proper size (Wayland-compatible)."""
        super().showEvent(event)
        # Center only on first show, after widget has proper geometry
        if getattr(self, '_first_show', False):
            self._first_show = False
            # Use QTimer to defer centering until after layout is fully computed
            QTimer.singleShot(0, self.center_on_screen)
