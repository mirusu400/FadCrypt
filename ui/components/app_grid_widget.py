"""Application Grid Widget for FadCrypt Qt"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent, QCursor
import os
import subprocess


class AppCard(QFrame):
    """Individual application card widget"""
    
    clicked = pyqtSignal(str)  # app_name
    double_clicked = pyqtSignal(str)  # app_name
    context_menu_requested = pyqtSignal(str, object)  # app_name, position
    
    def __init__(self, app_name, app_path, unlock_count=0, date_added=None, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.app_path = app_path
        self.unlock_count = unlock_count
        self.date_added = date_added
        self.is_selected = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the card UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            AppCard {
                background-color: #2a2a2a;
                border: 2px solid #444444;
                border-radius: 10px;
                padding: 12px;
            }
            AppCard:hover {
                border: 2px solid #4ade80;
                background-color: #333333;
            }
        """)
        self.setMinimumSize(220, 220)
        self.setMaximumSize(280, 280)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")
        try:
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            icon_label.setAutoFillBackground(False)
        except Exception:
            pass
        
        # Try to load app icon
        pixmap = self.load_app_icon()
        if pixmap:
            icon_label.setPixmap(pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Fallback emoji
            icon_label.setText("📦")
            icon_label.setStyleSheet("font-size: 42px; background-color: transparent;")
        
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel(self.app_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(40)
        name_label.setStyleSheet("""
            color: #ffffff;
            font-size: 11pt;
            font-weight: bold;
            background-color: transparent;
        """)
        layout.addWidget(name_label)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444444; max-height: 1px;")
        layout.addWidget(separator)
        
        # Path info
        path_display = os.path.basename(self.app_path)
        if len(path_display) > 25:
            path_display = path_display[:22] + "..."
        path_label = QLabel(f"📁 {path_display}")
        path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path_label.setToolTip(self.app_path)  # Full path on hover
        path_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(path_label)
        
        # Date added
        if self.date_added:
            from datetime import datetime
            try:
                # If date_added is timestamp
                if isinstance(self.date_added, (int, float)):
                    date_obj = datetime.fromtimestamp(self.date_added)
                else:
                    date_obj = datetime.fromisoformat(self.date_added)
                date_str = date_obj.strftime("%b %d, %Y")
            except:
                date_str = str(self.date_added)
        else:
            date_str = "Recently added"
        
        date_label = QLabel(f"📅 {date_str}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(date_label)
        
        # Stats
        stats_label = QLabel(f"🔓 {self.unlock_count}× unlocked")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(stats_label)
        
        self.setLayout(layout)
    
    def load_app_icon(self):
        """Load icon for the application"""
        try:
            # Try to find icon from .desktop file
            icon_path = self.find_desktop_icon()
            if icon_path and os.path.exists(icon_path):
                if not icon_path.endswith('.svg'):
                    return QPixmap(icon_path)
            
            # Try common icon locations
            app_name = os.path.basename(self.app_path).lower()
            icon_locations = [
                f'/usr/share/pixmaps/{app_name}.png',
                f'/usr/share/icons/hicolor/48x48/apps/{app_name}.png',
                f'/usr/share/icons/hicolor/64x64/apps/{app_name}.png',
            ]
            
            for path in icon_locations:
                if os.path.exists(path):
                    return QPixmap(path)
        except Exception as e:
            print(f"Error loading icon for {self.app_name}: {e}")
        
        return None
    
    def find_desktop_icon(self):
        """Find icon from .desktop file"""
        try:
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/local/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            app_name = os.path.basename(self.app_path)
            
            for desktop_dir in desktop_dirs:
                if not os.path.exists(desktop_dir):
                    continue
                
                for filename in os.listdir(desktop_dir):
                    if not filename.endswith('.desktop'):
                        continue
                    
                    filepath = os.path.join(desktop_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            exec_path = None
                            icon_path = None
                            
                            for line in f:
                                line = line.strip()
                                if line.startswith('Exec='):
                                    exec_path = line.split('=', 1)[1].split()[0]
                                elif line.startswith('Icon='):
                                    icon_path = line.split('=', 1)[1]
                            
                            if exec_path and (app_name in exec_path or exec_path in self.app_path):
                                if icon_path:
                                    # If icon_path is not absolute, search for it
                                    if not os.path.isabs(icon_path):
                                        return self.find_icon_by_name(icon_path)
                                    return icon_path
                    except:
                        continue
        except Exception as e:
            print(f"Error finding desktop icon: {e}")
        return None
    
    def find_icon_by_name(self, icon_name):
        """Find icon by name in standard directories"""
        icon_dirs = [
            '/usr/share/icons/hicolor/48x48/apps',
            '/usr/share/icons/hicolor/64x64/apps',
            '/usr/share/pixmaps',
        ]
        
        for icon_dir in icon_dirs:
            if not os.path.exists(icon_dir):
                continue
            
            for ext in ['.png', '.xpm', '']:
                icon_path = os.path.join(icon_dir, icon_name + ext)
                if os.path.exists(icon_path):
                    return icon_path
        
        return None
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                AppCard {
                    background-color: #064e3b;
                    border: 2px solid #10b981;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                AppCard {
                    background-color: #2a2a2a;
                    border: 2px solid #444444;
                    border-radius: 10px;
                    padding: 10px;
                }
                AppCard:hover {
                    border: 2px solid #4ade80;
                    background-color: #333333;
                }
            """)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.app_name)
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self.app_name, event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.app_name)
        super().mouseDoubleClickEvent(event)


class AppGridWidget(QWidget):
    """Grid widget for displaying application cards"""
    
    # Signals for parent communication
    app_edited = pyqtSignal(str, str, str)  # old_name, new_name, new_path
    app_removed = pyqtSignal(str)  # app_name
    app_lock_toggled = pyqtSignal(str, bool)  # app_name, is_locked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apps_data = {}  # {app_name: {'path': path, 'unlock_count': count}}
        self.app_cards = {}  # {app_name: AppCard widget}
        self.selected_apps = set()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
            }
        """)
        
        # Container for grid
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #0f0f0f;")
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.container.setLayout(self.grid_layout)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
        # Show empty state initially
        self.empty_state_widget = None
        self.show_empty_state()
    
    def show_empty_state(self):
        """Show empty state message when no apps"""
        if self.empty_state_widget is None:
            self.empty_state_widget = QWidget()
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(15)
            
            # Icon
            icon_label = QLabel("📭")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 72px;")
            empty_layout.addWidget(icon_label)
            
            # Title
            title_label = QLabel("No Applications Added")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
            """)
            empty_layout.addWidget(title_label)
            
            # Description
            desc_label = QLabel("Click the 'Add Application' button below to start\nprotecting your applications with encryption")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                color: #888888;
                font-size: 11pt;
            """)
            empty_layout.addWidget(desc_label)
            
            self.empty_state_widget.setLayout(empty_layout)
        
        # Add to grid (center it by spanning columns)
        self.grid_layout.addWidget(self.empty_state_widget, 0, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        self.empty_state_widget.show()
    
    def hide_empty_state(self):
        """Hide empty state message"""
        if self.empty_state_widget:
            self.empty_state_widget.hide()
            self.grid_layout.removeWidget(self.empty_state_widget)
    
    def add_app(self, app_name, app_path, unlock_count=0, date_added=None):
        """Add an application to the grid"""
        import time
        self.apps_data[app_name] = {
            'path': app_path,
            'unlock_count': unlock_count,
            'date_added': date_added if date_added else time.time()
        }
        self.refresh_grid()
    
    def remove_app(self, app_name):
        """Remove an application from the grid"""
        if app_name in self.apps_data:
            del self.apps_data[app_name]
            self.selected_apps.discard(app_name)
            self.refresh_grid()
    
    def refresh_grid(self):
        """Refresh the grid display"""
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        self.app_cards.clear()
        
        # Show empty state if no apps
        if not self.apps_data:
            self.show_empty_state()
            return
        else:
            self.hide_empty_state()
        
        if not self.apps_data:
            # Show empty state with icon
            empty_widget = QWidget()
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setSpacing(20)
            
            # Icon
            icon_label = QLabel("📦")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 72px;")
            empty_layout.addWidget(icon_label)
            
            # Text
            text_label = QLabel("No Applications Yet")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet("""
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
            """)
            empty_layout.addWidget(text_label)
            
            # Instruction
            instruction_label = QLabel("Click '➕ Add Application' to add your first app")
            instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            instruction_label.setStyleSheet("""
                color: #888888;
                font-size: 13pt;
            """)
            empty_layout.addWidget(instruction_label)
            
            empty_widget.setLayout(empty_layout)
            self.grid_layout.addWidget(empty_widget, 0, 0, 1, 3)
        else:
            # Create grid of cards (3 columns)
            columns = 3
            row = 0
            col = 0
            
            for app_name, app_data in self.apps_data.items():
                card = AppCard(
                    app_name,
                    app_data['path'],
                    app_data.get('unlock_count', 0),
                    app_data.get('date_added', None)
                )
                card.clicked.connect(self.on_card_clicked)
                card.double_clicked.connect(self.on_card_double_clicked)
                card.context_menu_requested.connect(self.show_context_menu)
                
                self.grid_layout.addWidget(card, row, col)
                self.app_cards[app_name] = card
                
                # Update selection state
                if app_name in self.selected_apps:
                    card.set_selected(True)
                
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
    
    def on_card_clicked(self, app_name):
        """Handle card click - toggle selection"""
        if app_name in self.selected_apps:
            self.selected_apps.discard(app_name)
            self.app_cards[app_name].set_selected(False)
        else:
            self.selected_apps.add(app_name)
            self.app_cards[app_name].set_selected(True)
    
    def on_card_double_clicked(self, app_name):
        """Handle card double click - could open edit dialog"""
        print(f"Double clicked: {app_name}")
        # Emit signal to parent for edit
        app_data = self.apps_data.get(app_name)
        if app_data:
            self.app_edited.emit(app_name, app_name, app_data['path'])
    
    def show_context_menu(self, app_name, position):
        """Show right-click context menu for an app card"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #e5e7eb;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
            }
        """)
        
        # Edit action
        edit_action = menu.addAction("✏️  Edit Application")
        edit_action.triggered.connect(lambda: self.request_edit_app(app_name))
        
        # Remove action
        remove_action = menu.addAction("🗑️  Remove Application")
        remove_action.triggered.connect(lambda: self.request_remove_app(app_name))
        
        menu.addSeparator()
        
        # Open file location
        open_location_action = menu.addAction("📁 Open File Location")
        open_location_action.triggered.connect(lambda: self.open_file_location(app_name))
        
        menu.exec(position)
    
    def request_edit_app(self, app_name):
        """Request to edit application (signal to parent)"""
        app_data = self.apps_data.get(app_name)
        if app_data:
            print(f"[AppGrid] Requesting edit for: {app_name}")
            self.app_edited.emit(app_name, app_name, app_data['path'])
    
    def request_remove_app(self, app_name):
        """Request to remove application (signal to parent)"""
        print(f"[AppGrid] Requesting removal for: {app_name}")
        self.app_removed.emit(app_name)
    
    def open_file_location(self, app_name):
        """Open the file manager at the application's location"""
        app_data = self.apps_data.get(app_name)
        if not app_data:
            return
        
        app_path = app_data['path']
        if not os.path.exists(app_path):
            print(f"File not found: {app_path}")
            return
        
        # Get directory containing the file
        file_dir = os.path.dirname(app_path)
        
        try:
            # Try xdg-open first (works on most Linux DEs)
            subprocess.Popen(['xdg-open', file_dir])
        except:
            try:
                # Fallback to nautilus (GNOME)
                subprocess.Popen(['nautilus', file_dir])
            except:
                try:
                    # Fallback to dolphin (KDE)
                    subprocess.Popen(['dolphin', file_dir])
                except:
                    print(f"Could not open file manager for: {file_dir}")
    
    def selectAll(self):
        """Select all applications"""
        self.selected_apps = set(self.apps_data.keys())
        for app_name, card in self.app_cards.items():
            card.set_selected(True)
    
    def clearSelection(self):
        """Clear all selections"""
        self.selected_apps.clear()
        for card in self.app_cards.values():
            card.set_selected(False)
    
    def get_selected_apps(self):
        """Get list of selected app names"""
        return list(self.selected_apps)
