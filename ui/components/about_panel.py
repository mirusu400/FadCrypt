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
        """Initialize the about panel UI"""
        # Make scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # App icon
        icon_path = self.resource_path('img/icon.png')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path)
            scaled_icon = icon_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)
        
        # App name
        app_name = QLabel("FadCrypt")
        app_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name)
        
        # Version
        version_label = QLabel(f"Version {self.version}")
        version_label.setStyleSheet("font-size: 10px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Check for updates button
        update_button = QPushButton("Check for Updates")
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        update_button.clicked.connect(self.check_for_updates)
        update_button.setMaximumWidth(200)
        layout.addWidget(update_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        # Description
        description = QLabel(
            "FadCrypt is an open-source app lock/encryption software that prioritizes privacy by not tracking or collecting any data. "
            "It is available exclusively on GitHub and through the official links mentioned in the README."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setMaximumWidth(400)
        layout.addWidget(description, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        # FadSec Lab Suite Information
        suite_frame = QFrame()
        suite_frame.setStyleSheet("background-color: black; border-radius: 5px; padding: 10px;")
        suite_layout = QVBoxLayout(suite_frame)
        
        suite_info = QLabel("FadCrypt is part of the FadSec Lab suite. For more information, click on 'View Source Code' below.")
        suite_info.setStyleSheet("color: green; font-weight: bold;")
        suite_info.setWordWrap(True)
        suite_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        suite_layout.addWidget(suite_info)
        
        layout.addWidget(suite_frame)
        layout.addSpacing(10)
        
        # Button row
        button_layout = QHBoxLayout()
        
        source_button = QPushButton("View Source Code")
        source_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)
        source_button.clicked.connect(lambda: webbrowser.open("https://github.com/anonfaded/FadCrypt"))
        button_layout.addWidget(source_button)
        
        coffee_button = QPushButton("Buy Me A Coffee")
        coffee_button.setStyleSheet("""
            QPushButton {
                background-color: #ffeb3b;
                color: black;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #fdd835;
            }
        """)
        coffee_button.clicked.connect(lambda: webbrowser.open("https://ko-fi.com/fadedx"))
        button_layout.addWidget(coffee_button)
        
        discord_button = QPushButton("Join Discord")
        discord_button.setStyleSheet("""
            QPushButton {
                background-color: #5865f2;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        discord_button.clicked.connect(lambda: webbrowser.open("https://discord.gg/kvAZvdkuuN"))
        button_layout.addWidget(discord_button)
        
        review_button = QPushButton("Write a Review")
        review_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        review_button.clicked.connect(lambda: webbrowser.open("https://forms.gle/wnthyevjkRD41eTFA"))
        button_layout.addWidget(review_button)
        
        layout.addLayout(button_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        layout.addSpacing(10)
        
        # FadCam Promotion Section
        promo_title = QLabel("Check out FadCam, our Android app from the FadSec Lab suite.")
        promo_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        promo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(promo_title)
        
        layout.addSpacing(10)
        
        # FadCam frame with icon and button
        fadcam_frame = QHBoxLayout()
        fadcam_frame.setSpacing(10)
        
        # FadCam icon and text
        fadcam_icon_path = self.resource_path('img/fadcam.png')
        if os.path.exists(fadcam_icon_path):
            fadcam_icon_label = QLabel()
            fadcam_pixmap = QPixmap(fadcam_icon_path)
            # Scale to reasonable size (subsample 12x12 in Tkinter)
            scaled_fadcam = fadcam_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            fadcam_icon_label.setPixmap(scaled_fadcam)
            fadcam_icon_label.setCursor(Qt.CursorShape.PointingHandCursor)
            fadcam_icon_label.mousePressEvent = lambda event: webbrowser.open("https://github.com/anonfaded/FadCam")
            fadcam_frame.addWidget(fadcam_icon_label)
        
        fadcam_text = QLabel("FadCam - Open Source Ad-Free Offscreen Video Recorder.")
        fadcam_text.setStyleSheet("font-weight: bold;")
        fadcam_text.setCursor(Qt.CursorShape.PointingHandCursor)
        fadcam_text.mousePressEvent = lambda event: webbrowser.open("https://github.com/anonfaded/FadCam")
        fadcam_frame.addWidget(fadcam_text)
        
        fadcam_button = QPushButton("Get FadCam")
        fadcam_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        fadcam_button.clicked.connect(lambda: webbrowser.open("https://github.com/anonfaded/FadCam"))
        fadcam_frame.addWidget(fadcam_button)
        
        fadcam_frame.addStretch()
        
        layout.addLayout(fadcam_frame)
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
