"""Password Recovery Dialog - For using recovery codes to reset password"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame,
    QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class RecoveryCodeDialog(QDialog):
    """Dialog for entering recovery code and creating new password"""
    
    def __init__(self, title, resource_path, parent=None):
        super().__init__(parent)
        self.resource_path = resource_path
        self.recovery_code_value = None
        self.new_password_value = None
        
        self.setWindowTitle(title)
        self.init_ui(title)
    
    def init_ui(self, title):
        """Initialize recovery code dialog UI"""
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content frame
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: none;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel { 
                font-size: 16px; 
                font-weight: bold; 
                color: #ffffff; 
                border: none;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Tab widget for recovery code and new password
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background-color: #2a2a2a; color: #e0e0e0; padding: 8px 15px; }
            QTabBar::tab:selected { background-color: #d32f2f; color: white; }
        """)
        
        # Tab 1: Recovery Code
        code_tab = QFrame()
        code_layout = QVBoxLayout(code_tab)
        code_layout.setContentsMargins(15, 15, 15, 15)
        code_layout.setSpacing(12)
        
        code_help = QLabel(
            "Enter one of your 10 recovery codes saved when you created your password.\n"
            "Format: XXXX-XXXX-XXXX-XXXX (or spaces: XXXX XXXX XXXX XXXX)"
        )
        code_help.setWordWrap(True)
        code_help.setStyleSheet("""
            QLabel { 
                font-size: 10px; 
                color: #a0a0a0; 
                padding: 0;
            }
        """)
        code_layout.addWidget(code_help)
        
        self.recovery_code_input = QLineEdit()
        self.recovery_code_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.recovery_code_input.setFixedHeight(38)
        self.recovery_code_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                font-family: monospace;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
        """)
        code_layout.addWidget(self.recovery_code_input)
        
        warning_label = QLabel(
            "⚠️ Warning: Each recovery code can only be used ONCE.\n"
            "After using a code, you won't be able to use it again."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            QLabel { 
                font-size: 10px; 
                color: #ff6b6b; 
                padding: 10px;
                background-color: #3a2a2a;
                border-radius: 4px;
            }
        """)
        code_layout.addWidget(warning_label)
        code_layout.addStretch()
        
        tab_widget.addTab(code_tab, "Recovery Code")
        
        # Tab 2: New Password
        pwd_tab = QFrame()
        pwd_layout = QVBoxLayout(pwd_tab)
        pwd_layout.setContentsMargins(15, 15, 15, 15)
        pwd_layout.setSpacing(12)
        
        pwd_help = QLabel(
            "Enter a NEW master password for your account.\n"
            "This will replace your old password completely.\n"
            "After recovery, you'll receive 10 new recovery codes."
        )
        pwd_help.setWordWrap(True)
        pwd_help.setStyleSheet("""
            QLabel { 
                font-size: 10px; 
                color: #a0a0a0; 
                padding: 0;
            }
        """)
        pwd_layout.addWidget(pwd_help)
        
        pwd_label = QLabel("New Master Password:")
        pwd_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 11px; }")
        pwd_layout.addWidget(pwd_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new master password")
        self.new_password_input.setFixedHeight(38)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
        """)
        pwd_layout.addWidget(self.new_password_input)
        
        confirm_label = QLabel("Confirm Password:")
        confirm_label.setStyleSheet("QLabel { color: #e0e0e0; font-size: 11px; }")
        pwd_layout.addWidget(confirm_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setFixedHeight(38)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 0 14px;
                font-size: 13px;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #d32f2f;
                background-color: #2e2e2e;
            }
        """)
        pwd_layout.addWidget(self.confirm_password_input)
        
        pwd_warning = QLabel(
            "⚠️ Important: Your new password cannot be recovered if forgotten.\n"
            "Make it strong and memorable, or you'll need a recovery code again."
        )
        pwd_warning.setWordWrap(True)
        pwd_warning.setStyleSheet("""
            QLabel { 
                font-size: 10px; 
                color: #ff6b6b; 
                padding: 10px;
                background-color: #3a2a2a;
                border-radius: 4px;
            }
        """)
        pwd_layout.addWidget(pwd_warning)
        pwd_layout.addStretch()
        
        tab_widget.addTab(pwd_tab, "New Password")
        
        content_layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(120, 36)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #464646; }
            QPushButton:pressed { background-color: #2e2e2e; }
        """)
        cancel_button.clicked.connect(self.reject)
        
        recover_button = QPushButton("Recover")
        recover_button.setFixedSize(120, 36)
        recover_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #b71c1c; }
            QPushButton:pressed { background-color: #9a0007; }
        """)
        recover_button.clicked.connect(self.on_recover)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(recover_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        # Set size
        self.setMinimumSize(550, 400)
        self.resize(550, 400)
        
        # Center on screen
        self.center_on_screen()
        
        # Focus on recovery code input
        self.recovery_code_input.setFocus()
    
    def center_on_screen(self):
        """Center dialog on screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def on_recover(self):
        """Handle recovery button"""
        code = self.recovery_code_input.text().strip()
        pwd1 = self.new_password_input.text()
        pwd2 = self.confirm_password_input.text()
        
        # Validate inputs
        if not code:
            self.show_error("Recovery Code Required", "Please enter your recovery code")
            return
        
        if not pwd1:
            self.show_error("Password Required", "Please enter a new password")
            return
        
        if pwd1 != pwd2:
            self.show_error("Passwords Don't Match", "The passwords you entered do not match")
            return
        
        if len(pwd1) < 6:
            self.show_error("Password Too Short", "Password must be at least 6 characters")
            return
        
        self.recovery_code_value = code
        self.new_password_value = pwd1
        self.accept()
    
    def show_error(self, title, message):
        """Show error message"""
        from PyQt6.QtWidgets import QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; }
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 5px 20px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        msg_box.exec()
    
    def get_recovery_code(self):
        """Get entered recovery code"""
        return self.recovery_code_value
    
    def get_new_password(self):
        """Get new password"""
        return self.new_password_value
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class RecoveryCodesDisplayDialog(QDialog):
    """Dialog to display generated recovery codes to user"""
    
    def __init__(self, codes: list, resource_path=None, parent=None):
        super().__init__(parent)
        self.codes = codes
        self.resource_path = resource_path
        
        self.setWindowTitle("Recovery Codes - Save These!")
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog { background-color: #1a1a1a; }")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Warning title
        warning_title = QLabel("🔐 SAVE YOUR RECOVERY CODES")
        warning_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        warning_title.setStyleSheet("QLabel { color: #ff6b6b; }")
        warning_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(warning_title)
        
        # Important message
        message = QLabel(
            "If you forget your FadCrypt master password, you can use these codes to recover access.\n\n"
            "⚠️  IMPORTANT:\n"
            "• Each code can ONLY be used ONCE\n"
            "• Save these codes in a SAFE PLACE (print, password manager, etc.)\n"
            "• Do NOT share these codes with anyone\n"
            "• If all codes are used and you forget your password, you will lose access\n"
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                padding: 15px;
                background-color: #2a2a2a;
                border-radius: 5px;
                border-left: 4px solid #ff6b6b;
            }
        """)
        main_layout.addWidget(message)
        
        # Codes display area
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
            }
        """)
        scroll.setWidgetResizable(True)
        
        codes_container = QFrame()
        codes_layout = QVBoxLayout(codes_container)
        codes_layout.setContentsMargins(15, 15, 15, 15)
        codes_layout.setSpacing(10)
        
        for i, code in enumerate(self.codes, 1):
            code_label = QLabel(f"{i:2d}. {code}")
            code_label.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
            code_label.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    padding: 8px;
                    background-color: #1a1a1a;
                    border: 1px solid #004400;
                    border-radius: 3px;
                    font-family: monospace;
                }
            """)
            codes_layout.addWidget(code_label)
        
        codes_layout.addStretch()
        scroll.setWidget(codes_container)
        main_layout.addWidget(scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        copy_button = QPushButton("📋 Copy All")
        copy_button.setFixedHeight(36)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #1a4620;
                color: #00ff00;
                border: 1px solid #004400;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #215028; }
        """)
        copy_button.clicked.connect(self.copy_codes)
        button_layout.addWidget(copy_button)
        
        close_button = QPushButton("I Have Saved These Codes")
        close_button.setFixedHeight(36)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def copy_codes(self):
        """Copy all codes to clipboard"""
        from PyQt6.QtGui import QClipboard
        from PyQt6.QtWidgets import QApplication
        
        text = "FadCrypt Recovery Codes:\n\n"
        for i, code in enumerate(self.codes, 1):
            text += f"{i:2d}. {code}\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Copied")
        msg.setText("✅ All recovery codes copied to clipboard!")
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; }
            QMessageBox QLabel { color: #e0e0e0; }
            QPushButton { background-color: #d32f2f; color: white; padding: 5px 20px; }
        """)
        msg.exec()


def ask_recovery_code(resource_path=None, parent=None):
    """
    Show recovery code dialog.
    
    Returns:
        Tuple of (recovery_code: str, new_password: str) or (None, None) if cancelled
    """
    dialog = RecoveryCodeDialog("Recover Access with Recovery Code", resource_path, parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_recovery_code(), dialog.get_new_password()
    return None, None


def show_recovery_codes(codes: list, resource_path=None, parent=None):
    """
    Show generated recovery codes to user.
    Blocks until user confirms they have saved the codes.
    """
    dialog = RecoveryCodesDisplayDialog(codes, resource_path, parent)
    dialog.exec()
