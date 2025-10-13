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
        select_all_clicked: User wants to select all applications
        deselect_all_clicked: User wants to deselect all applications
    """
    
    add_app_clicked = pyqtSignal()
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
        self.add_button.setMinimumHeight(35)
        self.add_button.clicked.connect(self.add_app_clicked.emit)
        layout.addWidget(self.add_button)
        
        # Select All button
        self.select_all_button = QPushButton("✅ Select All")
        self.select_all_button.setMinimumHeight(35)
        self.select_all_button.clicked.connect(self.select_all_clicked.emit)
        layout.addWidget(self.select_all_button)
        
        # Deselect All button
        self.deselect_all_button = QPushButton("❌ Deselect All")
        self.deselect_all_button.setMinimumHeight(35)
        self.deselect_all_button.clicked.connect(self.deselect_all_clicked.emit)
        layout.addWidget(self.deselect_all_button)
        
        # Stretch at the end
        layout.addStretch()
