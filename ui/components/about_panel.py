"""About Panel Component for FadCrypt"""

import os
import webbrowser
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class AboutPanel(QWidget):
    """About panel showing app information, FadSec suite, and FadCam promotion"""
    
    def __init__(self, version, version_code, resource_path_func):
        super().__init__()
        self.version = version
        self.version_code = version_code
        self.resource_path = resource_path_func
        self.init_ui()
        
    def init_ui(self):
        """Initialize the about panel UI with modern design"""
        # Make scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        scroll_content = QWidget()
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # === Header Section (Everything in ONE compact box) ===
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(8)
        
        # App icon - smaller for compactness
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path)
            scaled_icon = icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(icon_label)
        
        # App name - smaller
        app_name = QLabel("FadCrypt")
        app_name.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 1px;
            }
        """)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_name)
        
        # Version - more compact
        version_label = QLabel(f"v{self.version}")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #888888;
                background-color: #3a3a3a;
                padding: 3px 10px;
                border-radius: 8px;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add minimal spacing before bio
        header_layout.addSpacing(5)
        
        # Bio/description - compact
        bio = QLabel("🔒 Open-source app lock\n🛡️ Privacy-focused\n📦 GitHub exclusive")
        bio.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-size: 11px;
                font-weight: bold;
                line-height: 1.4;
            }
        """)
        bio.setWordWrap(True)
        bio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(bio)
        
        layout.addWidget(header_frame)
        
        # === Action Buttons Grid ===
        buttons_frame = QWidget()
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(10)
        
        # Row 1: Check Updates (keep green for success-related action)
        update_button = QPushButton("🔄 Check for Updates")
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 25px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """)
        update_button.clicked.connect(self.check_for_updates)
        update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(update_button)
        
        # Row 2: Source & Support
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        source_button = QPushButton("📂 Source Code")
        source_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        source_button.clicked.connect(lambda: webbrowser.open("https://github.com/anonfaded/FadCrypt"))
        source_button.setCursor(Qt.CursorShape.PointingHandCursor)
        row2.addWidget(source_button)
        
        coffee_button = QPushButton("☕ Buy Me Coffee")
        coffee_button.setStyleSheet("""
            QPushButton {
                background-color: #ffeb3b;
                color: #000000;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #fdd835;
            }
        """)
        coffee_button.clicked.connect(lambda: webbrowser.open("https://ko-fi.com/fadedx"))
        coffee_button.setCursor(Qt.CursorShape.PointingHandCursor)
        row2.addWidget(coffee_button)
        
        buttons_layout.addLayout(row2)
        
        # Row 3: Community
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        
        discord_button = QPushButton("💬 Join Discord")
        discord_button.setStyleSheet("""
            QPushButton {
                background-color: #5865f2;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        discord_button.clicked.connect(lambda: webbrowser.open("https://discord.gg/kvAZvdkuuN"))
        discord_button.setCursor(Qt.CursorShape.PointingHandCursor)
        row3.addWidget(discord_button)
        
        review_button = QPushButton("⭐ Write Review")
        review_button.setStyleSheet("""
            QPushButton {
                background-color: #f57c00;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e65100;
            }
        """)
        review_button.clicked.connect(lambda: webbrowser.open("https://forms.gle/wnthyevjkRD41eTFA"))
        review_button.setCursor(Qt.CursorShape.PointingHandCursor)
        row3.addWidget(review_button)
        
        buttons_layout.addLayout(row3)
        
        layout.addWidget(buttons_frame)
        
        # === FadSec Lab Suite Info ===
        suite_frame = QFrame()
        suite_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a1a1a, stop:1 #1a1a1a);
                border-radius: 12px;
                border-left: 4px solid #d32f2f;
                padding: 15px;
            }
        """)
        suite_layout = QVBoxLayout(suite_frame)
        
        suite_title = QLabel("🛡️ Part of FadSec Lab Suite")
        suite_title.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        suite_layout.addWidget(suite_title)
        
        suite_info = QLabel("Comprehensive security tools for privacy-conscious users")
        suite_info.setStyleSheet("color: #888888; font-size: 11px;")
        suite_info.setWordWrap(True)
        suite_layout.addWidget(suite_info)
        
        layout.addWidget(suite_frame)
        
        # === FadCam Promotion Card ===
        fadcam_frame = QFrame()
        fadcam_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        fadcam_layout = QHBoxLayout(fadcam_frame)
        fadcam_layout.setSpacing(15)
        
        # FadCam icon
        fadcam_icon_path = self.resource_path('img/fadcam.png')
        if os.path.exists(fadcam_icon_path):
            fadcam_icon_label = QLabel()
            fadcam_pixmap = QPixmap(fadcam_icon_path)
            scaled_fadcam = fadcam_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            fadcam_icon_label.setPixmap(scaled_fadcam)
            fadcam_icon_label.setCursor(Qt.CursorShape.PointingHandCursor)
            fadcam_icon_label.mousePressEvent = lambda event: webbrowser.open("https://github.com/anonfaded/FadCam")
            fadcam_layout.addWidget(fadcam_icon_label)
        
        # FadCam info
        fadcam_info_layout = QVBoxLayout()
        fadcam_info_layout.setSpacing(5)
        
        fadcam_title = QLabel("FadCam")
        fadcam_title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 15px;
                color: #ffffff;
            }
        """)
        fadcam_info_layout.addWidget(fadcam_title)
        
        fadcam_desc = QLabel("Open Source Ad-Free Offscreen Video Recorder")
        fadcam_desc.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        fadcam_desc.setWordWrap(True)
        fadcam_info_layout.addWidget(fadcam_desc)
        
        fadcam_layout.addLayout(fadcam_info_layout, 1)
        
        # Get FadCam button
        fadcam_button = QPushButton("Get FadCam →")
        fadcam_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        fadcam_button.clicked.connect(lambda: webbrowser.open("https://github.com/anonfaded/FadCam"))
        fadcam_button.setCursor(Qt.CursorShape.PointingHandCursor)
        fadcam_layout.addWidget(fadcam_button)
        
        layout.addWidget(fadcam_frame)
        
        # === Footer ===
        footer = QLabel("© 2024 FadSec Lab • Open Source • Privacy First")
        footer.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 10px;
                padding-top: 20px;
            }
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
        layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
    def check_for_updates(self):
        """Check for latest version on GitHub"""
        try:
            response = requests.get("https://api.github.com/repos/anonfaded/FadCrypt/releases/latest", timeout=5)
            response.raise_for_status()
            
            latest_version = response.json().get("tag_name", None)
            current_version = self.version
            
            if latest_version:
                # Compare versions (strip 'v' prefix)
                latest_ver = latest_version.lstrip('v')
                current_ver = current_version.lstrip('v')
                
                # Split and compare
                try:
                    latest_parts = [int(x) for x in latest_ver.split('.')]
                    current_parts = [int(x) for x in current_ver.split('.')]
                    
                    if latest_parts > current_parts:
                        QMessageBox.information(
                            self,
                            "Update Available",
                            f"New version {latest_version} is available! Visit GitHub for more details."
                        )
                    else:
                        QMessageBox.information(
                            self,
                            "Up to Date",
                            "Your application is up to date."
                        )
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Could not parse version information."
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Could not retrieve version information."
                )
        except requests.ConnectionError:
            QMessageBox.warning(
                self,
                "Connection Error",
                "Unable to check for updates. Please check your internet connection."
            )
        except requests.HTTPError as http_err:
            QMessageBox.warning(
                self,
                "HTTP Error",
                f"HTTP error occurred:\n{http_err}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"An error occurred while checking for updates:\n{e}"
            )
