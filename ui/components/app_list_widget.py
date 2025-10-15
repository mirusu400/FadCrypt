"""
Application List Widget - Display and manage locked applications
"""

from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QBrush
from typing import List, Dict, Optional


class AppListWidget(QListWidget):
    """
    Custom list widget for displaying applications.
    
    Features:
    - Display app name and path
    - Show lock/unlock status with icons
    - Right-click context menu (Edit, Remove, Open Location)
    - Drag-and-drop support for adding apps
    
    Signals:
        app_selected: Emitted when an app is selected (app_name, app_path)
        app_removed: Emitted when an app is removed (app_name)
        app_edited: Emitted when an app is edited (old_name, new_name, new_path)
        app_lock_toggled: Emitted when lock status changes (app_name, is_locked)
    """
    
    app_selected = pyqtSignal(str, str)  # app_name, app_path
    app_removed = pyqtSignal(str)  # app_name
    app_edited = pyqtSignal(str, str, str)  # old_name, new_name, new_path
    app_lock_toggled = pyqtSignal(str, bool)  # app_name, is_locked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.apps_data: Dict[str, Dict] = {}  # {app_name: {path, is_locked}}
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Enable drag-and-drop
        self.setAcceptDrops(True)
        self.setDragEnabled(False)
        
        # Selection mode
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # Connect item click
        self.itemClicked.connect(self._on_item_clicked)
    
    def add_app(self, app_name: str, app_path: str, is_locked: bool = True):
        """
        Add an application to the list.
        
        Args:
            app_name: Name of the application
            app_path: Full path to the application executable
            is_locked: Whether the app is currently locked
        """
        # Store app data
        self.apps_data[app_name] = {
            'path': app_path,
            'is_locked': is_locked
        }
        
        # Create list item
        item = QListWidgetItem()
        item.setText(f"{'🔒' if is_locked else '🔓'} {app_name}")
        item.setData(Qt.ItemDataRole.UserRole, app_name)  # Store app_name in item data
        
        # Set tooltip with full path
        item.setToolTip(f"Path: {app_path}\nStatus: {'Locked' if is_locked else 'Unlocked'}")
        
        # Color coding
        if is_locked:
            item.setForeground(QBrush(QColor(255, 100, 100)))  # Red for locked
        else:
            item.setForeground(QBrush(QColor(100, 255, 100)))  # Green for unlocked
        
        self.addItem(item)
    
    def remove_app(self, app_name: str):
        """Remove an application from the list."""
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == app_name:
                self.takeItem(i)
                if app_name in self.apps_data:
                    del self.apps_data[app_name]
                break
    
    def update_app_status(self, app_name: str, is_locked: bool):
        """
        Update the lock status of an application.
        
        Args:
            app_name: Name of the application
            is_locked: New lock status
        """
        if app_name in self.apps_data:
            self.apps_data[app_name]['is_locked'] = is_locked
            
            # Update list item
            for i in range(self.count()):
                item = self.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == app_name:
                    item.setText(f"{'🔒' if is_locked else '🔓'} {app_name}")
                    item.setToolTip(
                        f"Path: {self.apps_data[app_name]['path']}\n"
                        f"Status: {'Locked' if is_locked else 'Unlocked'}"
                    )
                    if is_locked:
                        item.setForeground(QBrush(QColor(255, 100, 100)))
                    else:
                        item.setForeground(QBrush(QColor(100, 255, 100)))
                    break
    
    def get_all_apps(self) -> List[Dict[str, str]]:
        """
        Get all applications in the list.
        
        Returns:
            List of dicts with keys: name, path, is_locked
        """
        return [
            {
                'name': app_name,
                'path': data['path'],
                'is_locked': data['is_locked']
            }
            for app_name, data in self.apps_data.items()
        ]
    
    def clear_all(self):
        """Clear all applications from the list."""
        self.clear()
        self.apps_data.clear()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click."""
        app_name = item.data(Qt.ItemDataRole.UserRole)
        if app_name and app_name in self.apps_data:
            app_path = self.apps_data[app_name]['path']
            self.app_selected.emit(app_name, app_path)
    
    def _show_context_menu(self, position):
        """Show context menu on right-click."""
        item = self.itemAt(position)
        if not item:
            return
        
        app_name = item.data(Qt.ItemDataRole.UserRole)
        if not app_name or app_name not in self.apps_data:
            return
        
        is_locked = self.apps_data[app_name]['is_locked']
        
        # Create context menu
        menu = QMenu(self)
        
        # Toggle lock/unlock
        toggle_action = menu.addAction("🔓 Unlock" if is_locked else "🔒 Lock")
        toggle_action.triggered.connect(lambda: self._toggle_lock(app_name))
        
        menu.addSeparator()
        
        # Edit
        edit_action = menu.addAction("✏️ Edit")
        edit_action.triggered.connect(lambda: self._edit_app(app_name))
        
        # Remove
        remove_action = menu.addAction("🗑️ Remove")
        remove_action.triggered.connect(lambda: self._remove_app(app_name))
        
        menu.addSeparator()
        
        # Open location
        open_action = menu.addAction("📁 Open Location")
        open_action.triggered.connect(lambda: self._open_location(app_name))
        
        # Show menu
        menu.exec(self.mapToGlobal(position))
    
    def _toggle_lock(self, app_name: str):
        """Toggle lock status of an app."""
        if app_name in self.apps_data:
            current_status = self.apps_data[app_name]['is_locked']
            new_status = not current_status
            self.update_app_status(app_name, new_status)
            self.app_lock_toggled.emit(app_name, new_status)
    
    def _edit_app(self, app_name: str):
        """Edit an app (placeholder - emits signal for parent to handle)."""
        if app_name in self.apps_data:
            # Parent should show edit dialog
            self.app_edited.emit(app_name, app_name, self.apps_data[app_name]['path'])
    
    def _remove_app(self, app_name: str):
        """Remove an app with confirmation."""
        reply = QMessageBox.question(
            self,
            "Remove Application",
            f"Are you sure you want to remove '{app_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_app(app_name)
            self.app_removed.emit(app_name)
    
    def _open_location(self, app_name: str):
        """Open the folder containing the app executable."""
        if app_name in self.apps_data:
            import os
            import subprocess
            import sys
            
            app_path = self.apps_data[app_name]['path']
            folder = os.path.dirname(app_path)
            
            if os.path.exists(folder):
                if sys.platform.startswith('linux'):
                    subprocess.Popen(['xdg-open', folder])
                elif sys.platform.startswith('win'):
                    subprocess.Popen(['explorer', folder])
                else:
                    subprocess.Popen(['open', folder])  # macOS
            else:
                QMessageBox.warning(
                    self,
                    "Folder Not Found",
                    f"The folder does not exist:\n{folder}"
                )
    
    # Drag-and-drop support
    def dragEnterEvent(self, event):
        """Accept drag events with file URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle dropped files."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:
                    # Parent should handle adding the app
                    # For now, just print
                    print(f"Dropped file: {file_path}")
            event.acceptProposedAction()
