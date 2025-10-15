"""
Button Panel - Control buttons for application management
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class ButtonPanel(QWidget):
    """
    Panel with control buttons for managing applications.
    
    Signals:
        add_app_clicked: User wants to add a new application
        edit_app_clicked: User wants to edit selected application
        remove_app_clicked: User wants to remove selected applications
        select_all_clicked: User wants to select all applications
        deselect_all_clicked: User wants to deselect all applications
    """
    
    add_app_clicked = pyqtSignal()
    edit_app_clicked = pyqtSignal()
    remove_app_clicked = pyqtSignal()
    select_all_clicked = pyqtSignal()
    deselect_all_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Add Application button
        self.add_button = QPushButton("➕ Add Application")
        self.add_button.setMinimumHeight(40)
        self.add_button.setMinimumWidth(140)
        self.add_button.clicked.connect(self.add_app_clicked.emit)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #009E60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #00b56f;
            }
        """)
        layout.addWidget(self.add_button)
        
        layout.addSpacing(30)
        
        # Edit button
        self.edit_button = QPushButton("✏️ Edit")
        self.edit_button.setMinimumHeight(40)
        self.edit_button.setMinimumWidth(100)
        self.edit_button.clicked.connect(self.edit_app_clicked.emit)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #FBBF24;
            }
        """)
        layout.addWidget(self.edit_button)
        
        # Remove button
        self.remove_button = QPushButton("🗑️ Remove")
        self.remove_button.setMinimumHeight(40)
        self.remove_button.setMinimumWidth(100)
        self.remove_button.clicked.connect(self.remove_app_clicked.emit)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """)
        layout.addWidget(self.remove_button)
        
        layout.addSpacing(30)
        
        # Select All button
        self.select_all_button = QPushButton("✅ Select All")
        self.select_all_button.setMinimumHeight(40)
        self.select_all_button.setMinimumWidth(100)
        self.select_all_button.clicked.connect(self.select_all_clicked.emit)
        self.select_all_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #60A5FA;
            }
        """)
        layout.addWidget(self.select_all_button)
        
        # Deselect All button
        self.deselect_all_button = QPushButton("❌ Deselect All")
        self.deselect_all_button.setMinimumHeight(40)
        self.deselect_all_button.setMinimumWidth(120)
        self.deselect_all_button.clicked.connect(self.deselect_all_clicked.emit)
        self.deselect_all_button.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #9CA3AF;
            }
        """)
        layout.addWidget(self.deselect_all_button)
        
        # Stretch at the end
        layout.addStretch()
