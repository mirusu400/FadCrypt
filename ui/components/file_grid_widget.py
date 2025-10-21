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
    
    def __init__(self, item_name, item_path, item_type="file", unlock_count=0, date_added=None, parent=None):
        super().__init__(parent)
        self.item_name = item_name
        self.item_path = item_path
        self.item_type = item_type  # "file" or "folder"
        self.unlock_count = unlock_count
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
        self.setMinimumSize(180, 200)
        self.setMaximumSize(220, 240)
        
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
        
        # Unlock count (new metadata)
        unlock_label = QLabel(f"🔓 Unlocked {self.unlock_count}x")
        unlock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unlock_label.setStyleSheet("""
            color: #888888;
            font-size: 8pt;
            background-color: transparent;
        """)
        layout.addWidget(unlock_label)
        
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
        self.selected_paths = []  # Multiple selection support
        self.selected_path = None  # Backwards compatibility
        self.all_items = []  # Store all items for search filtering
        self.current_columns = 4  # Track current column count for responsive resize
        self.init_ui()
    
    def resizeEvent(self, event):
        """Handle resize event to make grid responsive"""
        super().resizeEvent(event)
        # Calculate new column count based on available width
        # Card width: 180-220px, spacing: 15px, margins: 10px each side
        available_width = self.grid_container.width() - 20  # Subtract margins
        card_min_width = 180 + 15  # Min card width + spacing
        new_columns = max(1, available_width // card_min_width)
        
        # Only rebuild grid if column count changed
        if new_columns != self.current_columns:
            self.current_columns = new_columns
            self._rebuild_grid()
    
    def init_ui(self):
        """Initialize UI"""
        from PyQt6.QtWidgets import QLineEdit, QPushButton, QComboBox
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Reduced from 10 to 5
        
        # Toolbar with search and buttons
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)  # Reduced vertical padding
        toolbar.setStyleSheet("background-color: #1a1a1a;")
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search files and folders...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
            }
        """)
        self.search_input.textChanged.connect(self.filter_items)
        toolbar_layout.addWidget(self.search_input, stretch=2)
        
        # Filter dropdown (Files/Folders/All)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Items", "Files Only", "Folders Only"])
        self.type_filter.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border: 2px solid #d32f2f;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #d32f2f;
            }
        """)
        self.type_filter.currentTextChanged.connect(self.filter_items)
        toolbar_layout.addWidget(self.type_filter)
        
        # Select All button
        select_all_btn = QPushButton("☑️  Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border: 2px solid #d32f2f;
            }
        """)
        select_all_btn.clicked.connect(self.select_all)
        toolbar_layout.addWidget(select_all_btn)
        
        # Deselect All button
        deselect_all_btn = QPushButton("❌ Deselect All")
        deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #666666;
                border: 2px solid #666666;
            }
        """)
        deselect_all_btn.clicked.connect(self.deselect_all)
        toolbar_layout.addWidget(deselect_all_btn)
        
        layout.addWidget(toolbar)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
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
        self.grid_container.setStyleSheet("background-color: #0f0f0f;")
        
        # Ensure container expands to fill scroll area
        from PyQt6.QtWidgets import QSizePolicy
        self.grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)  # Match AppGridWidget spacing
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        # Cards align top-center when present
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Placeholder (shown when no items) - wrapped in centered container
        self.placeholder_container = QWidget()
        placeholder_container_layout = QVBoxLayout(self.placeholder_container)
        placeholder_container_layout.setContentsMargins(0, 0, 0, 0)
        placeholder_container_layout.addStretch(1)
        
        self.placeholder = self._create_placeholder()
        placeholder_container_layout.addWidget(self.placeholder)
        placeholder_container_layout.addStretch(1)
        
        self.grid_layout.addWidget(self.placeholder_container, 0, 0, 1, self.current_columns)  # Span all columns
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)
    
    def add_item(self, item_path: str, item_type: str, unlock_count=0, date_added=None):
        """Add file or folder to grid"""
        if item_path in self.cards:
            return
        
        item_name = os.path.basename(item_path) or item_path
        
        card = FileCard(item_name, item_path, item_type, unlock_count, date_added)
        card.clicked.connect(self.on_card_clicked)
        card.double_clicked.connect(self.on_card_double_clicked)
        card.context_menu_requested.connect(self.on_context_menu)
        
        # Calculate grid position using current column count
        num_cards = len(self.cards)
        row = num_cards // self.current_columns
        col = num_cards % self.current_columns
        
        self.grid_layout.addWidget(card, row, col)
        self.cards[item_path] = card
        
        # Store in all_items for filtering
        self.all_items.append({
            'path': item_path,
            'type': item_type,
            'unlock_count': unlock_count,
            'date_added': date_added
        })
        
        # Update placeholder visibility
        self._update_placeholder_visibility()
    
    def remove_item(self, item_path: str, defer_refresh=False):
        """Remove file or folder from grid
        
        Args:
            item_path: Path of the item to remove
            defer_refresh: If True, skip grid refresh (for bulk operations)
        """
        if item_path not in self.cards:
            return
        
        card = self.cards[item_path]
        self.grid_layout.removeWidget(card)
        card.deleteLater()
        del self.cards[item_path]
        
        # Remove from all_items
        self.all_items = [item for item in self.all_items if item['path'] != item_path]
        
        # Remove from selected paths
        if item_path in self.selected_paths:
            self.selected_paths.remove(item_path)
        if self.selected_path == item_path:
            self.selected_path = None
        
        # Only refresh if not deferred (optimization for bulk removes)
        if not defer_refresh:
            self.refresh_grid()
        
        # Update placeholder visibility
        self._update_placeholder_visibility()
    
    def refresh_grid(self):
        """Refresh grid layout with current column count"""
        # Remove all widgets except placeholder container
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and widget != self.placeholder_container:
                    self.grid_layout.removeWidget(widget)
        
        # Re-add cards in responsive grid
        for idx, (path, card) in enumerate(self.cards.items()):
            row = idx // self.current_columns
            col = idx % self.current_columns
            self.grid_layout.addWidget(card, row, col)
        
        # Re-add placeholder container spanning all columns
        self.grid_layout.removeWidget(self.placeholder_container)
        self.grid_layout.addWidget(self.placeholder_container, 0, 0, 1, self.current_columns)
    
    def _rebuild_grid(self):
        """Rebuild grid when column count changes (responsive behavior)"""
        if not self.cards:
            return
        self.refresh_grid()
    
    def clear(self):
        """Clear all items"""
        for card in self.cards.values():
            card.deleteLater()
        self.cards.clear()
        self.all_items.clear()
        self.selected_paths.clear()
        self.selected_path = None
        self._update_placeholder_visibility()
    
    def get_selected_path(self) -> str:
        """Get currently selected path (single selection for backwards compatibility)"""
        return self.selected_path
    
    def get_selected_paths(self) -> list:
        """Get all selected paths (multi-selection)"""
        return self.selected_paths.copy()
    
    def on_card_clicked(self, path: str):
        """Handle card click - supports multi-selection"""
        # Multi-select: clicking adds to selection, doesn't clear others
        if path in self.selected_paths:
            # Already selected - deselect it
            self.selected_paths.remove(path)
            if path in self.cards:
                self.cards[path].set_selected(False)
            if self.selected_path == path:
                self.selected_path = self.selected_paths[0] if self.selected_paths else None
        else:
            # Not selected - add to selection
            self.selected_paths.append(path)
            if path in self.cards:
                self.cards[path].set_selected(True)
            self.selected_path = path  # Update single selection for backwards compat
        
        self.item_selected.emit(path)
        print(f"Selected: {len(self.selected_paths)} items")
    
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
    
    def select_all(self):
        """Select all cards"""
        for path, card in self.cards.items():
            card.set_selected(True)
            if path not in self.selected_paths:
                self.selected_paths.append(path)
        print(f"Selected {len(self.selected_paths)} items")
    
    def deselect_all(self):
        """Deselect all cards"""
        for card in self.cards.values():
            card.set_selected(False)
        self.selected_paths.clear()
        self.selected_path = None
        print("Deselected all items")
    
    def filter_items(self, text: str = None):
        """Filter displayed items by search text and type filter"""
        search_term = self.search_input.text().lower().strip()
        filter_type = self.type_filter.currentText()
        
        # Filter cards by both search and type
        visible_count = 0
        for path, card in self.cards.items():
            # Check search match
            item_name = os.path.basename(path).lower()
            name_match = (not search_term) or (search_term in item_name)
            
            # Check type match
            if filter_type == "Files Only":
                type_match = os.path.isfile(path)
            elif filter_type == "Folders Only":
                type_match = os.path.isdir(path)
            else:  # "All Items"
                type_match = True
            
            # Show card only if both conditions match
            if name_match and type_match:
                card.show()
                visible_count += 1
            else:
                card.hide()
        
        # Show placeholder if no results
        has_active_filter = (search_term != "" or filter_type != "All Items")
        self._update_placeholder_visibility(visible_count == 0 and has_active_filter)
        
        print(f"Filtered: {visible_count} items (search: '{search_term}', type: {filter_type})")
    
    def _create_placeholder(self) -> QWidget:
        """Create placeholder widget shown when no items"""
        placeholder = QWidget()
        # Don't set minimum height - let it fill available space naturally
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(20)
        placeholder_layout.addStretch(1)  # Push content to center
        
        # Icon
        icon_label = QLabel("📂")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 72px; background-color: transparent;")
        placeholder_layout.addWidget(icon_label)
        
        # Message
        msg_label = QLabel("No files or folders locked")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setStyleSheet("""
            color: #888888;
            font-size: 14pt;
            font-weight: bold;
            background-color: transparent;
        """)
        placeholder_layout.addWidget(msg_label)
        
        # Hint
        hint_label = QLabel("Use 'Add File' or 'Add Folder' buttons below to start protecting")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("""
            color: #666666;
            font-size: 10pt;
            background-color: transparent;
        """)
        placeholder_layout.addWidget(hint_label)
        placeholder_layout.addStretch(1)  # Push content to center
        
        placeholder.hide()  # Hidden by default
        return placeholder
    
    def _update_placeholder_visibility(self, force_show=False):
        """Update placeholder visibility based on card count"""
        if force_show or len(self.cards) == 0:
            self.placeholder.show()
            # Hide all cards when placeholder is shown
            for card in self.cards.values():
                card.hide()
        else:
            self.placeholder.hide()
            # Don't override card visibility - filter_items() handles that
