"""Add Application Dialog for FadCrypt"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os


class AddApplicationDialog(QDialog):
    """Dialog for adding applications with drag-and-drop support"""
    
    application_added = pyqtSignal(str, str)  # app_name, app_path
    
    def __init__(self, resource_path, parent=None):
        super().__init__(parent)
        self.resource_path = resource_path
        self.setWindowTitle("Add Application to Encrypt")
        self.setMinimumSize(420, 580)
        self.setModal(True)
        
        # Position on left edge
        screen_geometry = self.screen().geometry()
        x = 50
        y = (screen_geometry.height() - 580) // 2
        self.move(x, y)
        
        self.init_ui()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Drag and Drop Area
        drop_group = QGroupBox("Drag and Drop Executable Here")
        drop_layout = QVBoxLayout()
        
        self.drop_area = QTextEdit()
        self.drop_area.setReadOnly(True)
        self.drop_area.setMinimumHeight(100)
        self.drop_area.setMaximumHeight(150)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                color: #00ff00;
                font-size: 11px;
                border: 2px dashed #ccc;
            }
        """)
        self.drop_area.setText("Just drop it in—I'll sort out the name and path,\nno worries")
        self.drop_area.setAcceptDrops(True)
        
        # Install event filter to handle drops on the text edit
        self.drop_area.installEventFilter(self)
        
        drop_layout.addWidget(self.drop_area)
        drop_group.setLayout(drop_layout)
        layout.addWidget(drop_group)
        
        # Manual Input Area
        manual_group = QGroupBox("Or Manually Add Application")
        manual_layout = QVBoxLayout()
        
        # Helper text
        helper_label = QLabel(
            "To find an executable path, use the 'which' command in terminal:\n"
            "❯ which firefox\n"
            "/usr/bin/firefox\n\n"
            "Paste the exact path (with slashes) in the Path field below.\n"
            "For Name, use any readable name like 'Firefox'."
        )
        helper_label.setStyleSheet("color: blue; font-size: 9pt;")
        helper_label.setWordWrap(True)
        manual_layout.addWidget(helper_label)
        
        # Name input
        name_label = QLabel("Name:")
        manual_layout.addWidget(name_label)
        
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("e.g., Firefox")
        manual_layout.addWidget(self.name_entry)
        
        # Path input
        path_label = QLabel("Path:")
        manual_layout.addWidget(path_label)
        
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("e.g., /usr/bin/firefox")
        manual_layout.addWidget(self.path_entry)
        
        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #4C516D;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a3f5c;
            }
        """)
        browse_button.clicked.connect(self.browse_for_file)
        manual_layout.addWidget(browse_button)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Scan Apps Button
        scan_button = QPushButton("🔍 Scan for Apps")
        scan_button.setMinimumWidth(120)
        scan_button.setStyleSheet("""
            QPushButton {
                background-color: #4C516D;
                color: white;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3f5c;
            }
        """)
        scan_button.clicked.connect(self.scan_for_apps)
        button_layout.addWidget(scan_button)
        
        # Save Button
        save_button = QPushButton("💾 Save")
        save_button.setMinimumWidth(100)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #009E60;
                color: white;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """)
        save_button.clicked.connect(self.save_application)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Bind Enter key to save
        self.name_entry.returnPressed.connect(self.save_application)
        self.path_entry.returnPressed.connect(self.save_application)
    
    def eventFilter(self, obj, event):
        """Handle drag and drop events on the drop area"""
        if obj == self.drop_area:
            if event.type() == event.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                else:
                    event.ignore()
                return True
            elif event.type() == event.Type.Drop:
                if event.mimeData().hasUrls():
                    urls = event.mimeData().urls()
                    if urls:
                        file_path = urls[0].toLocalFile()
                        self.on_drop(file_path)
                return True
        return super().eventFilter(obj, event)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event on dialog"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event on dialog"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.on_drop(file_path)
    
    def on_drop(self, file_path):
        """Handle dropped file"""
        # Check if file exists
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file does not exist:\n{file_path}")
            return
        
        # Check if it's executable
        if not self.is_executable(file_path):
            reply = QMessageBox.question(
                self,
                "Not Executable",
                f"The selected file is not executable.\nDo you want to add it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Auto-fill name and path
        app_name = os.path.basename(file_path)
        self.name_entry.setText(app_name)
        self.path_entry.setText(file_path)
        
        self.drop_area.setStyleSheet("""
            QTextEdit {
                background-color: #d4edda;
                color: #155724;
                font-size: 11px;
                border: 2px solid #28a745;
            }
        """)
        self.drop_area.setText(f"✓ File added:\n{app_name}\n{file_path}")
    
    def is_executable(self, file_path):
        """Check if file is executable"""
        # Linux executable extensions
        linux_executables = ('.desktop', '.sh', '.AppImage', '.run', '.bin', '.py', '.pl', '.rb')
        
        return (
            file_path.endswith(linux_executables) or
            os.access(file_path, os.X_OK) or
            self.is_elf_binary(file_path)
        )
    
    def is_elf_binary(self, file_path):
        """Check if the file is an ELF binary (Linux executable format)"""
        try:
            with open(file_path, 'rb') as f:
                return f.read(4) == b'\x7fELF'
        except (IOError, OSError):
            return False
    
    def browse_for_file(self):
        """Open file browser to select executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application Executable",
            os.path.expanduser("~"),
            "All Files (*)"
        )
        
        if file_path:
            self.path_entry.setText(file_path)
            if not self.name_entry.text():
                self.name_entry.setText(os.path.basename(file_path))
    
    def scan_for_apps(self):
        """Open app scanner (to be implemented later)"""
        QMessageBox.information(
            self,
            "Scan for Apps",
            "App scanner feature will be implemented in the next update!"
        )
    
    def save_application(self):
        """Save the application"""
        app_name = self.name_entry.text().strip()
        app_path = self.path_entry.text().strip()
        
        if not app_name or not app_path:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide both name and path for the application."
            )
            return
        
        # Check if path exists
        if not os.path.exists(app_path):
            reply = QMessageBox.question(
                self,
                "File Not Found",
                f"The path does not exist:\n{app_path}\n\nDo you want to add it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Emit signal and close
        self.application_added.emit(app_name, app_path)
        self.accept()
