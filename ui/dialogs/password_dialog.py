"""
Password Dialog - Master password input dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional


class PasswordDialog(QDialog):
    """
    Simple password input dialog.
    
    Args:
        title: Dialog window title
        prompt: Password prompt message
        parent: Parent widget
    """
    
    def __init__(self, title: str = "Password Required", prompt: str = "Enter master password:", parent=None):
        super().__init__(parent)
        
        self.password_value: Optional[str] = None
        
        # Window setup
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setFixedHeight(180)
        
        # Center on screen
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - 400) // 2
            y = parent_geo.y() + (parent_geo.height() - 180) // 2
            self.move(x, y)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Title label
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Prompt label
        prompt_label = QLabel(prompt)
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setWordWrap(True)
        layout.addWidget(prompt_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setPlaceholderText("Password")
        self.password_input.returnPressed.connect(self._on_ok_clicked)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus on password input
        self.password_input.setFocus()
    
    def _on_ok_clicked(self):
        """Handle OK button click."""
        self.password_value = self.password_input.text()
        if self.password_value:
            self.accept()
    
    def get_password(self) -> Optional[str]:
        """Get the entered password."""
        return self.password_value
    
    @staticmethod
    def get_password_input(title: str = "Password Required", 
                          prompt: str = "Enter master password:",
                          parent=None) -> Optional[str]:
        """
        Show password dialog and return entered password.
        
        Args:
            title: Dialog title
            prompt: Password prompt message
            parent: Parent widget
            
        Returns:
            Entered password or None if cancelled
        """
        dialog = PasswordDialog(title, prompt, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return None


class ChangePasswordDialog(QDialog):
    """
    Dialog for changing the master password.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.old_password: Optional[str] = None
        self.new_password: Optional[str] = None
        
        # Window setup
        self.setWindowTitle("Change Master Password")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setFixedHeight(260)
        
        # Center on screen
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - 450) // 2
            y = parent_geo.y() + (parent_geo.height() - 260) // 2
            self.move(x, y)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("🔑 Change Master Password")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Old password
        old_label = QLabel("Current Password:")
        layout.addWidget(old_label)
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setMinimumHeight(35)
        self.old_password_input.setPlaceholderText("Current password")
        layout.addWidget(self.old_password_input)
        
        # New password
        new_label = QLabel("New Password:")
        layout.addWidget(new_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setMinimumHeight(35)
        self.new_password_input.setPlaceholderText("New password")
        layout.addWidget(self.new_password_input)
        
        # Confirm password
        confirm_label = QLabel("Confirm New Password:")
        layout.addWidget(confirm_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.returnPressed.connect(self._on_ok_clicked)
        layout.addWidget(self.confirm_password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.ok_button = QPushButton("Change Password")
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus on old password
        self.old_password_input.setFocus()
    
    def _on_ok_clicked(self):
        """Handle OK button click."""
        from PyQt6.QtWidgets import QMessageBox
        
        old_pwd = self.old_password_input.text()
        new_pwd = self.new_password_input.text()
        confirm_pwd = self.confirm_password_input.text()
        
        # Validation
        if not old_pwd:
            QMessageBox.warning(self, "Error", "Please enter your current password.")
            self.old_password_input.setFocus()
            return
        
        if not new_pwd:
            QMessageBox.warning(self, "Error", "Please enter a new password.")
            self.new_password_input.setFocus()
            return
        
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return
        
        if len(new_pwd) < 4:
            QMessageBox.warning(self, "Error", "Password must be at least 4 characters.")
            self.new_password_input.setFocus()
            return
        
        # Store passwords
        self.old_password = old_pwd
        self.new_password = new_pwd
        self.accept()
    
    def get_passwords(self) -> tuple[Optional[str], Optional[str]]:
        """Get old and new passwords."""
        return self.old_password, self.new_password
