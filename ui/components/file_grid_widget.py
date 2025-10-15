"""File/Folder Grid Widget for FadCrypt Qt"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent, QCursor
import os


class FileCard(QFrame):
    """Individual file/folder card widget"""
    
    clicked = pyqtSignal(str)  # path
    double_clicked = pyqtSignal(str)  # path
    context_menu_requested = pyqtSignal(str, object)  # path, position
    
    def __init__(self, item_name, item_path, item_type="file", date_added=None, parent=None):
        super().__init__(parent)
        self.item_name = item_name
        self.item_path = item_path
        self.item_type = item_type  # "file" or "folder"
        self.date_added = date_added
        self.is_selected = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the card UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            FileCard {
                background-color: #2a2a2a;
                border: 2px solid #444444;
                border-radius: 10px;
                padding: 12px;
            }
            FileCard:hover {
                border: 2px solid #d32f2f;
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
        icon_label.setStyleSheet("background-color: transparent; font-size: 56px;")
        
        # Use emoji icons
        if self.item_type == "folder":
            icon_label.setText("📁")
        else:
            # File type detection based on extension
            ext = os.path.splitext(self.item_path)[1].lower()
            if ext in ['.txt', '.md', '.log']:
                icon_label.setText("📄")
            elif ext in ['.pdf']:
                icon_label.setText("📕")
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                icon_label.setText("🖼️")
            elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                icon_label.setText("🎬")
            elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
                icon_label.setText("🎵")
            elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z']:
                icon_label.setText("📦")
            elif ext in ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css']:
                icon_label.setText("💻")
            elif ext in ['.exe', '.msi', '.app']:
                icon_label.setText("⚙️")
            else:
                icon_label.setText("📃")
        
        layout.addWidget(icon_label)
        
        # Item name
        name_label = QLabel(self.item_name)
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
        
        # Path info (shortened)
        path_display = self.item_path
        if len(path_display) > 30:
            path_display = "..." + path_display[-27:]
        path_label = QLabel(f"📍 {path_display}")
        path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path_label.setToolTip(self.item_path)  # Full path on hover
        path_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # Date added
        if self.date_added:
            from datetime import datetime
            try:
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
        
        # Type label
        type_label = QLabel(f"📂 {self.item_type.capitalize()}")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(type_label)
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.item_path)
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self.item_path, event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.item_path)
        super().mouseDoubleClickEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selected state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                FileCard {
                    background-color: #3a3a3a;
                    border: 2px solid #d32f2f;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                FileCard {
                    background-color: #2a2a2a;
                    border: 2px solid #444444;
                    border-radius: 10px;
                    padding: 12px;
                }
                FileCard:hover {
                    border: 2px solid #d32f2f;
                    background-color: #333333;
                }
            """)


class FileGridWidget(QWidget):
    """Grid widget for displaying locked files and folders"""
    
    item_selected = pyqtSignal(str)  # path
    item_double_clicked = pyqtSignal(str)  # path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}  # path -> FileCard
        self.selected_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
        
        # Grid container
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)
    
    def add_item(self, item_path: str, item_type: str, date_added=None):
        """Add file or folder to grid"""
        if item_path in self.cards:
            return
        
        item_name = os.path.basename(item_path) or item_path
        
        card = FileCard(item_name, item_path, item_type, date_added)
        card.clicked.connect(self.on_card_clicked)
        card.double_clicked.connect(self.on_card_double_clicked)
        card.context_menu_requested.connect(self.on_context_menu)
        
        # Calculate grid position
        num_cards = len(self.cards)
        row = num_cards // 4
        col = num_cards % 4
        
        self.grid_layout.addWidget(card, row, col)
        self.cards[item_path] = card
    
    def remove_item(self, item_path: str):
        """Remove file or folder from grid"""
        if item_path not in self.cards:
            return
        
        card = self.cards[item_path]
        self.grid_layout.removeWidget(card)
        card.deleteLater()
        del self.cards[item_path]
        
        # Re-arrange remaining cards
        self.refresh_grid()
    
    def refresh_grid(self):
        """Refresh grid layout"""
        # Remove all widgets
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # Re-add in order
        for idx, (path, card) in enumerate(self.cards.items()):
            row = idx // 4
            col = idx % 4
            self.grid_layout.addWidget(card, row, col)
    
    def clear(self):
        """Clear all items"""
        for card in self.cards.values():
            card.deleteLater()
        self.cards.clear()
        self.selected_path = None
    
    def get_selected_path(self) -> str:
        """Get currently selected path"""
        return self.selected_path
    
    def on_card_clicked(self, path: str):
        """Handle card click"""
        # Deselect previous
        if self.selected_path and self.selected_path in self.cards:
            self.cards[self.selected_path].set_selected(False)
        
        # Select new
        self.selected_path = path
        if path in self.cards:
            self.cards[path].set_selected(True)
        
        self.item_selected.emit(path)
    
    def on_card_double_clicked(self, path: str):
        """Handle card double click"""
        self.item_double_clicked.emit(path)
    
    def on_context_menu(self, path: str, position):
        """Show context menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
            }
            QMenu::item:selected {
                background-color: #d32f2f;
            }
        """)
        
        remove_action = menu.addAction("🗑️  Remove")
        open_location_action = menu.addAction("📁 Open Location")
        
        action = menu.exec(position)
        
        if action == remove_action:
            self.remove_item(path)
        elif action == open_location_action:
            self.open_file_location(path)
    
    def open_file_location(self, path: str):
        """Open file/folder location in file manager"""
        import platform
        import subprocess
        
        try:
            if platform.system() == "Linux":
                # Open parent folder and select file
                parent = os.path.dirname(path)
                subprocess.Popen(['xdg-open', parent])
            elif platform.system() == "Windows":
                subprocess.Popen(['explorer', '/select,', path])
        except Exception as e:
            print(f"Error opening location: {e}")
