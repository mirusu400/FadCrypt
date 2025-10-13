"""
About Panel - Application information and credits
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import webbrowser


class AboutPanel(QWidget):
    """
    About panel displaying app information, version, and credits.
    """
    
    def __init__(self, app_version: str = "0.4.0", version_code: int = 4, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # App Title
        title_label = QLabel("🔐 FadCrypt")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Version Info
        version_label = QLabel(f"Version {app_version} (Build {version_code})")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "Application Locker with Password Protection\n"
            "Cross-platform security tool for Windows & Linux"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # UI Framework Info
        ui_label = QLabel("🎨 Modern PyQt6 User Interface")
        ui_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ui_label)
        
        # Performance Info
        perf_label = QLabel("⚡ Optimized Monitoring (~3-5% CPU)")
        perf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(perf_label)
        
        layout.addSpacing(20)
        
        # GitHub Button
        github_button = QPushButton("📦 View on GitHub")
        github_button.setMinimumHeight(35)
        github_button.clicked.connect(lambda: webbrowser.open("https://github.com/anonfaded/FadCrypt"))
        layout.addWidget(github_button)
        
        # Credits
        credits_label = QLabel(
            "Created by anonfaded\n"
            "Licensed under MIT License\n\n"
            "© 2024-2025 FadCrypt Project"
        )
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits_label)
        
        # Stretch at bottom
        layout.addStretch()
