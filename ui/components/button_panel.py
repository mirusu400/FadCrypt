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
        lock_all_clicked: User wants to lock all applications
        unlock_all_clicked: User wants to unlock all applications
    """
    
    add_app_clicked = pyqtSignal()
    lock_all_clicked = pyqtSignal()
    unlock_all_clicked = pyqtSignal()
    
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
        
        # Lock All button
        self.lock_all_button = QPushButton("🔒 Lock All")
        self.lock_all_button.setMinimumHeight(35)
        self.lock_all_button.clicked.connect(self.lock_all_clicked.emit)
        layout.addWidget(self.lock_all_button)
        
        # Unlock All button
        self.unlock_all_button = QPushButton("🔓 Unlock All")
        self.unlock_all_button.setMinimumHeight(35)
        self.unlock_all_button.clicked.connect(self.unlock_all_clicked.emit)
        layout.addWidget(self.unlock_all_button)
        
        # Stretch at the end
        layout.addStretch()
