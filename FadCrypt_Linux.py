import os
import json
import threading
import subprocess
import time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import psutil
import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage
import signal
from PIL import Image
from pystray import Icon, Menu, MenuItem
import sys
import base64
from cryptography.fernet import Fernet
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinterdnd2 import TkinterDnD, DND_FILES
from ttkbootstrap import Style
from PIL import Image, ImageTk
import webbrowser
import random
import requests
import pygame
import shlex          
import fcntl
import atexit
# App Version Information
__version__ = "0.1.0"
__version_code__ = 1  # Increment this for each release





class AppLockerGUI:
    def __init__(self, master):
        self.master = master
        
        self.master.title("FadCrypt")

        # Center the dialog on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        dialog_width = 700  # Increased width
        dialog_height = 650  # Increased height to prevent truncation
        position_x = (screen_width // 2) - (dialog_width // 2)
        position_y = (screen_height // 2) - (dialog_height // 2)
        self.master.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")


        # self.master.geometry("700x450") # Adjusted size to accommodate new tabs
        # Prevent resizing
        self.master.resizable(False, False)
        self.app_locker = AppLocker(self)

        
        # Ensure the settings file is correctly initialized
        self.settings_file = os.path.join(self.app_locker.get_fadcrypt_folder(), 'settings.json')
        self.lock_tools_var = tk.BooleanVar(value=True)  # Default value is True
        self.password_dialog_style = tk.StringVar(value="simple")
        self.wallpaper_choice = tk.StringVar(value="default")
        

        self.set_app_icon()  # Set the custom app icon
        self.create_widgets()
        self.load_settings()
        # Automatically start monitoring if launched with the --auto-monitor flag
        if '--auto-monitor' in sys.argv:
            self.start_monitoring(auto_start=True)
        

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
    def open_add_application_dialog(self):
        self.add_dialog = tk.Toplevel(self.master)  # Store reference to the dialog
        self.add_dialog.title("Add Application to Encrypt")

        # Set the same icon for the dialog
        # if hasattr(self, 'icon_img'):
        #     self.add_dialog.iconphoto(False, self.icon_img)
        #     self.add_dialog.update_idletasks()  # Force update the dialog to ensure the icon is set

        # Center the dialog on the screen
        screen_width = self.add_dialog.winfo_screenwidth()
        screen_height = self.add_dialog.winfo_screenheight()
        dialog_width = 400  # Adjust width as needed
        dialog_height = 500  # Adjust height as needed
        # position_x = (screen_width // 2) - (dialog_width // 2)
        position_x = 50  # Position the dialog on the left edge of the screen
        position_y = (screen_height // 2) - (dialog_height // 2)
        self.add_dialog.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")
        
        # Prevent resizing
        self.add_dialog.resizable(False, False)

        # Ensure the dialog is focused
        self.add_dialog.attributes('-topmost', True)
        self.add_dialog.focus_set()

        
        # Drag and Drop Area
        drop_frame = tk.LabelFrame(self.add_dialog, text="Drag and Drop .exe Here")
        drop_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Use TkinterDnD for drag-and-drop functionality
        drop_area = tk.Canvas(drop_frame, height=100, bg="lightgray")
        drop_area.pack(padx=10, pady=10, fill="both", expand=True)
        
        def update_text_position():
            drop_area.delete("all")  # Clear previous text
            drop_area.create_text(
                drop_area.winfo_width() // 2,
                drop_area.winfo_height() // 2,
                text="Just drop it in—I'll sort out the name and path,\nno worries",
                fill="lightgreen",
                font=("Arial", 9),
                anchor="center"
            )
    
        # Update text position after the canvas is rendered
        drop_area.after(100, update_text_position)  # Adjust delay if needed


        # Enable the canvas for drag-and-drop
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Manual Input Area
        manual_frame = tk.LabelFrame(self.add_dialog, text="Or Manually Add Application")
        manual_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(manual_frame, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(manual_frame)
        self.name_entry.pack(padx=10, pady=5, fill="x")

        tk.Label(manual_frame, text="Path:").pack(pady=5)
        self.path_entry = tk.Entry(manual_frame)
        self.path_entry.pack(padx=10, pady=5, fill="x")

        browse_button = ttk.Button(manual_frame, text="Browse", command=self.browse_for_file, style="navy.TButton")
        browse_button.pack(pady=5)

        # Save Button
        save_button = ttk.Button(self.add_dialog, text="Save", command=self.save_application, width=11, style="green.TButton")
        save_button.pack(pady=10)

        # Bind the Enter key to the Save button
        self.add_dialog.bind('<Return>', lambda event: save_button.invoke())


    def on_drop(self, event):
        file_path = event.data.strip('{}')

        # Check if the file exists first
        if not os.path.exists(file_path):
            self.show_message("Invalid File", "File does not exist.")
            return

        # Linux executable extensions and patterns
        linux_executables = ('.desktop', '.sh', '.AppImage', '.run', '.bin', '.py', '.pl', '.rb')

        # Check if it's a valid executable
        is_executable = (
            file_path.endswith(linux_executables) or
            os.access(file_path, os.X_OK) or  # Check if file has execute permissions
            self.is_elf_binary(file_path)  # Check if it's an ELF binary
        )

        if is_executable:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

            app_name = os.path.basename(file_path)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, app_name)
        else:
            self.show_message("Invalid File", "Please drop a valid executable file.")

    def is_elf_binary(self, file_path):
        """Check if the file is an ELF binary (Linux executable format)"""
        try:
            with open(file_path, 'rb') as f:
                # ELF files start with the magic bytes: 0x7f, 'E', 'L', 'F'
                magic = f.read(4)
                return magic == b'\x7fELF'
        except (IOError, OSError):
            return False

    def browse_for_file(self):
        # Update filetypes for Linux (allow selection of any executable file)
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.*")])
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

            app_name = os.path.basename(file_path)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, app_name)


    def save_application(self):
        app_name = self.name_entry.get().strip()
        app_path = self.path_entry.get().strip()
        
        if not app_name or not app_path:
            self.show_message("Error", "Both name and path are required.")
            return

        # Call the add_application method from AppLocker instance
        self.app_locker.add_application(app_name, app_path)
        self.update_apps_listbox()
        self.update_config_display()  # Update config tab

        # Close the dialog
        self.add_dialog.destroy()

        self.show_message("Success", f"Application '{app_name}'\nadded successfully!")

        






    def set_app_icon(self):
        try:
            # Only use .png icon for Linux
            png_path = self.resource_path('img/icon.png')
            if os.path.exists(png_path):
                icon_img = PhotoImage(file=png_path)
                self.master.iconphoto(False, icon_img)
            else:
                print(f"Icon file {png_path} not found, skipping icon setting.")
        except Exception as e:
            print(f"Failed to set application icon: {e}")







    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # Main Tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")

        try:
            # Load and display image
            self.load_image()
            self.image_label = tk.Label(self.main_frame, image=self.img)
            self.image_label.pack(pady=20)
        except:
            print("create_widget: Failed to load logo image...")

        # Frame for centered buttons
        center_buttons_frame = ttk.Frame(self.main_frame)
        center_buttons_frame.pack(pady=10)

        # Add Start Monitoring and Read Me buttons (centered)
        self.start_button = ttk.Button(center_buttons_frame, text="Start Monitoring", command=self.start_monitoring, style='red.TButton')
        self.start_button.pack(side=tk.LEFT, padx=10)

        readme_button = ttk.Button(center_buttons_frame, text="Read Me", command=self.show_readme, style='navy.TButton')
        readme_button.pack(side=tk.LEFT, padx=10)

        # Create a frame for the left side buttons and separator
        left_frame = ttk.Frame(self.main_frame)
        left_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)

        # Create a frame for the buttons
        left_button_frame = ttk.Frame(left_frame)
        left_button_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Add buttons to the left button frame
        ttk.Button(left_button_frame, text="Stop Monitoring", command=self.stop_monitoring).pack(pady=5, fill=tk.X)
        ttk.Button(left_button_frame, text="Create Password", command=self.create_password).pack(pady=5, fill=tk.X)
        ttk.Button(left_button_frame, text="Change Password", command=self.change_password).pack(pady=5, fill=tk.X)
        ttk.Button(left_button_frame, text="Snake 🪱", command=self.start_snake_game, style='navy.TButton').pack(pady=5, fill=tk.X)
        

        # Add vertical separator, fill x for shorter separator in middle or y for full height
        ttk.Separator(left_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.X, padx=10)
        
        # Add a separator before the footer
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10, padx=20)

        




        # Create a frame for the footer
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, padx=10, pady=5)

        # Load and scale the main tab's footer logo image
        logo_image = Image.open(self.resource_path('img/fadsec-main-footer.png'))  # Ensure 'fadsec.png' is in the 'img' directory
        scale_factor = 0.4  # Scale to 40% of the original size
        logo_image = logo_image.resize((int(logo_image.width * scale_factor), 
                                        int(logo_image.height * scale_factor)), 
                                        Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Add branding logo (left side)
        logo_label = tk.Label(footer_frame, image=logo_photo)
        logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
        logo_label.pack(side=tk.LEFT, padx=(0, 0))  # Add padding to the right of the logo

        # Add remaining branding and license info (right side)
        branding_text = " \u00A9 2024 | fadedhood.com | Licensed under GPL 3.0"
        branding_label = ttk.Label(footer_frame, text=branding_text, foreground="gray", font=("Helvetica", 10))
        branding_label.pack(side=tk.LEFT)

    

        # Add GitHub link with star emoji (right side)
        github_link = ttk.Label(footer_frame, text="⭐ Sponsor on GitHub", foreground="#FFD700", cursor="hand2", font=("Helvetica", 10))
        github_link.pack(side=tk.RIGHT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/anonfaded/FadCrypt"))










        # Config Tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Config")

        # Title for the config section
        config_title = ttk.Label(self.config_frame, text="Config File", font=("TkDefaultFont", 16, "bold"))
        config_title.pack(anchor="w", padx=10, pady=(10, 0))
        # Separator before textbox section
        ttk.Separator(self.config_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)

        # Config text box to display the config file content
        self.config_text = tk.Text(self.config_frame, width=99, height=17)
        self.config_text.pack(pady=5, padx=10)
        self.update_config_display()

        # Description below the config text box
        config_description = ttk.Label(self.config_frame, text=(
            "This is the list of applications currently locked by FadCrypt.\n"
            "It is displayed in plain text here for your convenience, "
            "but rest assured, the data is encrypted when saved on your computer,\n"
            "keeping your locked apps confidential."
        ))
        config_description.pack(anchor="w", padx=10, pady=(10, 10))

        # Separator before export section
        ttk.Separator(self.config_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Export config data section
        export_frame = ttk.Frame(self.config_frame)
        export_frame.pack(fill=tk.X, pady=10, padx=15)

        export_title = ttk.Label(export_frame, text="Export Configurations", font=("TkDefaultFont", 10, "bold"))
        export_title.pack(anchor="w", padx=10)

        export_description = ttk.Label(export_frame, text="Export the list of applications added to the lock list.")
        export_description.pack(anchor="w", pady=(0, 5), padx=10)

        export_button = ttk.Button(export_frame, text="Export Config", command=self.export_config, style="green.TButton")
        export_button.pack(anchor="w", padx=12)

        # Applications Tab
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="Applications")

        # Create a frame to hold the listbox and scrollbar
        list_frame = ttk.Frame(self.apps_frame)
        list_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Create the listbox with a scrollbar
        self.apps_listbox = tk.Listbox(list_frame, width=50, font=("Helvetica", 10), selectmode=tk.SINGLE)
        self.apps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.apps_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.apps_listbox.config(yscrollcommand=scrollbar.set)

        

        self.update_apps_listbox()

        # Buttons frame
        button_frame = ttk.Frame(self.apps_frame)
        button_frame.pack(pady=10, padx=5, fill=tk.X)

        # Modify the Add button to open the new dialog
        ttk.Button(button_frame, text="Add", command=self.open_add_application_dialog, style="green.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_application, style="red.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rename", command=self.rename_application).pack(side=tk.LEFT, padx=5)









































        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.settings_frame)
        self.scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas to expand with window
        self.canvas.bind('<Configure>', self.configure_canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Title
        title_label = ttk.Label(self.scrollable_frame, text="Preferences", font=("TkDefaultFont", 16, "bold"))
        title_label.pack(anchor="w", padx=10, pady=(10, 20))
        # Separator after top frame
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        

        # Top frame for radio buttons and preview
        top_frame = ttk.Frame(self.scrollable_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # Left frame for radio buttons
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(3, 10))

        # Right frame for preview
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Separator after preview section in settings tab
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Bottom frame for checkboxes and export section
        bottom_frame = ttk.Frame(self.scrollable_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)







        # Radio buttons
        ttk.Label(left_frame, text="Password Dialog Style:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=10)
        ttk.Radiobutton(left_frame, text="Simple Dialog", variable=self.password_dialog_style, value="simple", command=self.save_and_update_preview).pack(anchor="w", padx=20, pady=0)
        ttk.Radiobutton(left_frame, text="Full Screen", variable=self.password_dialog_style, value="fullscreen", command=self.save_and_update_preview).pack(anchor="w", padx=20, pady=20)
        ttk.Label(left_frame, text="Full Screen Wallpaper:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=5)
        ttk.Radiobutton(left_frame, text="Lab (Default)", variable=self.wallpaper_choice, value="default", command=self.save_and_update_wallpaper).pack(anchor="w", padx=20, pady=0)
        ttk.Radiobutton(left_frame, text="H4ck3r", variable=self.wallpaper_choice, value="H4ck3r", command=self.save_and_update_wallpaper).pack(anchor="w", padx=20, pady=20)
        ttk.Radiobutton(left_frame, text="Binary", variable=self.wallpaper_choice, value="Binary", command=self.save_and_update_wallpaper).pack(anchor="w", padx=20, pady=0)
        ttk.Radiobutton(left_frame, text="Encryptedddddd", variable=self.wallpaper_choice, value="encrypted", command=self.save_and_update_wallpaper).pack(anchor="w", padx=20, pady=20)
        # ttk.Radiobutton(left_frame, text="Lab", variable=self.wallpaper_choice, value="Lab", command=self.save_and_update_wallpaper).pack(anchor="w", padx=20, pady=0)








        # Preview area
        ttk.Label(right_frame, text="Dialog Preview:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=10, padx=50)
        self.preview_frame = ttk.Frame(right_frame, width=400, height=250)  # Set a fixed size
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)  # Prevent the frame from shrinking
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill=tk.BOTH)






        # Checkbox (full width)
        self.lock_tools_var = tk.BooleanVar(value=True)
        
        lock_tools_checkbox_title = ttk.Label(bottom_frame, text="Disable Main loopholes", font=("TkDefaultFont", 10, "bold"))
        lock_tools_checkbox_title.pack(anchor="w", pady=5, padx=27)
        lock_tools_checkbox = ttk.Checkbutton(
            bottom_frame,
            text="Disable Command Prompt, Registry Editor, Control Panel, msconfig, and Task Manager during monitoring.\n"
            "(Default: All are disabled for best security. For added security, please disable PowerShell as well; search\n"
            "on internet for help. Otherwise, FadCrypt could be terminated via PowerShell.)",
            variable=self.lock_tools_var,
            command=self.save_settings
        )
        lock_tools_checkbox.pack(anchor="w", pady=10)
        


        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

















        # About Tab
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="About")

        # Load App Logo with Error Handling
        try:
            app_icon = tk.PhotoImage(file=self.resource_path('img/icon.png')).subsample(4, 4)  # Resize the logo to 50x50 px
        except tk.TclError:
            print("Error: App icon 'img/icon.png' not found.")
            app_icon = None

        if app_icon:
            icon_label = ttk.Label(self.about_frame, image=app_icon)
            icon_label.image = app_icon  # Keep a reference to avoid garbage collection
            icon_label.pack(pady=20)
        else:
            icon_label = ttk.Label(self.about_frame, text="FadCrypt", font=("TkDefaultFont", 18, "bold"))
            icon_label.pack(pady=20)

        # App Name and Version
        app_name_label = ttk.Label(self.about_frame, text="FadCrypt", font=("TkDefaultFont", 18, "bold"))
        app_name_label.pack()

        app_version_label = ttk.Label(self.about_frame, text=f"Version {__version__}", font=("TkDefaultFont", 10))
        app_version_label.pack(pady=(0, 10))

        # Check for Updates Button
        update_button = ttk.Button(self.about_frame, text="Check for Updates", command=self.check_for_updates, style="green.TButton")
        update_button.pack(pady=10)

        # Description
        description_label = ttk.Label(
            self.about_frame, 
            text="FadCrypt is an open-source app lock/encryption software that prioritizes privacy by not tracking or collecting any data. It is available exclusively on GitHub and through the official links mentioned in the README.",
            wraplength=400,
            justify="center"
        )
        description_label.pack(pady=(0, 20))


        # FadSec Lab Suite Information with Darker Background
        suite_frame = ttk.Frame(self.about_frame, padding=10,  style="Dark.TFrame")
        suite_frame.pack(pady=10, padx=20)

        suite_info_label = ttk.Label(suite_frame, text="FadCrypt is part of the FadSec Lab suite. For more information, click on 'View Source Code' below.", background="black", foreground="green")
        suite_info_label.pack(anchor="center")



        # Button Frame for Alignment
        button_frame = ttk.Frame(self.about_frame)
        button_frame.pack(pady=10)

        # Source Code Button
        source_code_button = ttk.Button(button_frame, text="View Source Code", command=self.open_source_code, style="navy.TButton")
        source_code_button.grid(row=0, column=0, padx=(0, 10))

        # Buy Me A Coffee Button
        coffee_button = ttk.Button(button_frame, text="Buy Me A Coffee", command=lambda: webbrowser.open("https://ko-fi.com/fadedx"), style="yellow.TButton")
        coffee_button.grid(row=0, column=1, padx=(0, 10))

        # New Button: Join Discord
        discord_button = ttk.Button(button_frame, text="Join Discord", command=lambda: webbrowser.open("https://discord.gg/kvAZvdkuuN"), style="blue.TButton")
        discord_button.grid(row=0, column=2, padx=(0, 10))

        # New Button: Write a Review
        review_button = ttk.Button(button_frame, text="Write a Review", command=lambda: webbrowser.open("https://forms.gle/wnthyevjkRD41eTFA"), style="green.TButton")
        review_button.grid(row=0, column=3)




        # Promotion Section for Another App
        separator = ttk.Separator(self.about_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)




        # Title for Promotion Section
        promo_title_label = ttk.Label(self.about_frame, text="Check out FadCam, our Android app from the FadSec Lab suite.", font=("TkDefaultFont", 12, "bold"))
        promo_title_label.pack(pady=(0, 10))

        # Frame for FadCam Promo and Button
        fadcam_promo_frame = ttk.Frame(self.about_frame)
        fadcam_promo_frame.pack(pady=10)

        #  fad cam App Icon and Title
        try:
            fadcam_icon = tk.PhotoImage(file=self.resource_path('img/fadcam.png')).subsample(12, 12)  # Resize the logo to 50x50 px
        except tk.TclError:
            print("Error: FadCam icon 'fadcam_icon.png' not found.")
            fadcam_icon = None

        if fadcam_icon:
            fadcam_label = ttk.Label(fadcam_promo_frame, image=fadcam_icon, text="FadCam - Open Source Ad-Free Offscreen Video Recorder.",
                                    compound="left", font=("TkDefaultFont", 10, "bold"))
            fadcam_label.image = fadcam_icon
            fadcam_label.grid(row=0, column=0, padx=(0, 10))
            fadcam_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/anonfaded/FadCam"))
        else:
            fadcam_label = ttk.Label(fadcam_promo_frame, text="FadCam - Open Source Ad-Free Offscreen Video Recorder.",
                                    font=("TkDefaultFont", 10, "bold"))
            fadcam_label.grid(row=0, column=0, padx=(0, 10))
            fadcam_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/anonfaded/FadCam"))

        # Button to Open FadCam Repo
        fadcam_button = ttk.Button(fadcam_promo_frame, text="Get FadCam", command=lambda: webbrowser.open("https://github.com/anonfaded/FadCam"), style="red.TButton")
        fadcam_button.grid(row=0, column=1)














        self.update_preview()


    # Method to open the GitHub page
    def open_source_code(self):
        webbrowser.open("https://github.com/anonfaded/FadCrypt")
        
    

    # Method to check for updates

    def check_for_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/anonfaded/FadCrypt/releases/latest")
            response.raise_for_status()  # Ensure we got a valid response

            latest_version = response.json().get("tag_name", None)
            current_version = __version__

            if latest_version and latest_version != current_version:
                self.show_message("Update Available", f"New version {latest_version} is available! Visit GitHub for more details.")
            else:
                self.show_message("Up to Date", "Your application is up to date.")
        except requests.ConnectionError:
            self.show_message("Connection Error", "Unable to check for updates. Please check your internet connection.")
        except requests.HTTPError as http_err:
            self.show_message("HTTP Error", f"HTTP error occurred:\n{http_err}")
        except Exception as e:
            self.show_message("Error", f"An error occurred while checking for updates: {str(e)}")




    def show_readme(self):
        # Show the Read Me dialog first
        self.fullscreen_readme_dialog()


    def fullscreen_readme_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.attributes('-alpha', 0.0)  # Start fully transparent
        dialog.update_idletasks()  # Update geometry-related information

        # Set dialog to fullscreen
        dialog.attributes('-fullscreen', True)
        dialog.geometry(f"{dialog.winfo_screenwidth()}x{dialog.winfo_screenheight()}")

        # Center the dialog on the screen
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog_width = screen_width
        dialog_height = screen_height
        position_x = 0
        position_y = 0
        dialog.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")

        dialog.grab_set()


        # Add a frame for the text
        text_frame = tk.Frame(dialog, bg='white')
        text_frame.pack(expand=True, pady=50)

        welcome_text = (
            "Welcome to FadCrypt!\n\n"
            "Experience top-notch security and sleek design with FadCrypt.\n\n"
            "Features:\n"
            "- Application Locking: Secure apps with an encrypted password. Save your password safely;\nit can't be recovered if lost!\n"
            "- Real-time Monitoring: Detects and auto-recovers critical files if they are deleted.\n"
            "- Auto-Startup: After starting monitoring, the app will be automatically enabled for every session.\n"
            "- Aesthetic UI: Choose custom wallpapers or a minimal style with smooth animations.\n\n"
            "Security:\n"
            "- System Tools Disabled: Disables Command Prompt, Task Manager, msconfig, Control Panel, and Registry Editor;\n  a real nightmare for attackers trying to bypass it.\n  Manual PowerShell disabling is recommended as it's a significant loophole!\n"
            "- Encrypted Storage: Passwords and config file data (list of locked apps) are encrypted and backed up.\n\n"
            "Testing:\n"
            "- Test blocked tools (Command Prompt, Task Manager) via Windows search to confirm effectiveness.\nSearch for Control Panel or Task Manager in Windows+S search and see the disabled message box.\n\n"
            "Upcoming Features:\n"
            "- Password Recovery: In case of a forgotten password, users will be able to recover their passwords.\n"
            "- Logging and Alerts: Includes screenshots, email alerts on wrong password attempts, and detailed logs.\n"
            "- Community Input: Integrating feedback for improved security and usability.\n\n"
            "Extras:\n"
            "- Snake Game: Enjoy the classic Snake game on the main tab or from the tray icon for a bit of fun!\n\n"
            "# Join our Discord community via the 'Settings' tab\nfor help, questions, or to share your ideas and feedback."
        )




        # Create a label to hold the animated text
        self.animated_label = tk.Label(text_frame, text="", font=("Arial", 16), bg='white', justify="left", anchor="nw")
        self.animated_label.pack(padx=50, pady=50, anchor="n")

        # Start the typewriter animation
        self.animate_text(welcome_text, dialog)

        # Add a button to close the dialog
        ok_button = ttk.Button(dialog, text="OK", command=lambda: self.fade_out(dialog), style='red.TButton', width="11")
        ok_button.pack(pady=20)

        # Bind the Enter key to the OK button
        dialog.bind('<Return>', lambda event: dialog.destroy())

        # Load and place the image in the bottom left corner
        self.load_readme_image(dialog)


        # Fade in effect
        self.fade_in(dialog)

        # Ensure the dialog stays on top
        dialog.wait_window()

    def animate_text(self, text, dialog, index=0):
        if index < len(text):
            self.animated_label.config(text=text[:index+1])
            dialog.after(2, self.animate_text, text, dialog, index+1)  # Adjust the speed here

    def load_readme_image(self, dialog):
        # Load the image using PIL
        img = Image.open(self.resource_path("img/readme.png"))
        img = img.resize((400, 400), Image.LANCZOS)  # Adjust the size as needed
        photo = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(dialog, image=photo, bg='white')
        image_label.image = photo  # Keep a reference to avoid garbage collection

        # Place the image in the bottom left corner
        image_label.place(x=10, y=dialog.winfo_screenheight() - 400)


    def fade_in(self, window):
        alpha = 0.0
        while alpha < 1.0:
            alpha += 0.05
            window.attributes('-alpha', alpha)
            window.update_idletasks()
            window.after(50)  # Adjust the delay to control the fade-in speed

    def fade_out(self, window):
        alpha = window.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.05
            window.attributes('-alpha', alpha)
            window.after(50, self.fade_out, window)
        else:
            window.destroy()



















    def configure_canvas(self, event):
        # Update the width of the canvas window to fit the frame
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        # Update the initial canvas window height to fit the frame
        if self.scrollable_frame.winfo_reqheight() < event.height:
            self.canvas.itemconfig(self.canvas_frame, height=event.height)
        else:
            self.canvas.itemconfig(self.canvas_frame, height=self.scrollable_frame.winfo_reqheight())

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        
        




    def save_and_update_preview(self):
        self.save_password_dialog_style()
        self.update_preview()


    def save_and_update_wallpaper(self):
        self.save_wallpaper_choice()
        self.update_preview()



    def save_password_dialog_style(self):
        self.save_settings()   

    def save_wallpaper_choice(self):
        self.save_settings()


    def update_preview(self):
        dialog_style = self.password_dialog_style.get()
        wallpaper_choice = self.wallpaper_choice.get()

        if dialog_style == "simple":
            preview_path = self.resource_path("img/preview1.png")
        elif dialog_style == "fullscreen":
            if wallpaper_choice == "default":
                preview_path = self.resource_path("img/wall1.png")
            elif wallpaper_choice == "H4ck3r":
                preview_path = self.resource_path("img/wall2.png")
            elif wallpaper_choice == "Binary":
                preview_path = self.resource_path("img/wall3.png")
            elif wallpaper_choice == "encrypted":
                preview_path = self.resource_path("img/wall4.png")
            else:
                preview_path = self.resource_path("img/preview2.png")  # Fallback to fullscreen preview if no wallpaper selected
        else:
            preview_path = self.resource_path("img/preview2.png")  # Fallback to fullscreen preview if no style selected

        try:
            preview_image = Image.open(preview_path)
            preview_image = preview_image.resize((400, 250), Image.Resampling.LANCZOS)
            preview_photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.config(image=preview_photo)
            self.preview_label.image = preview_photo
        except FileNotFoundError:
            print(f"Preview image not found: {preview_path}")








    # image for the main page above the buttons
    def load_image(self):
        # Open and prepare the image
        try:
            image = Image.open(self.resource_path('img/banner.png'))  # Update this path
            image = image.resize((700, 200), Image.LANCZOS)  # Resize using LANCZOS filter
            self.img = ImageTk.PhotoImage(image)
        except:
            print("load_image: unable to load 1.ico")













    def update_config_textbox(self):
        # Update the content of the config text box with the latest config data
        config_json = json.dumps(self.app_locker.config, indent=4)
        self.config_textbox.config(state=tk.NORMAL)
        self.config_textbox.delete(1.0, tk.END)
        self.config_textbox.insert(tk.END, config_json)
        self.config_textbox.config(state=tk.DISABLED)



    def update_apps_listbox(self):
        self.apps_listbox.delete(0, tk.END)
        for index, app in enumerate(self.app_locker.config["applications"]):
            item = f"  {app['name']} - {app['path']}"  # Added two spaces for left padding
            self.apps_listbox.insert(tk.END, item)
            # Apply alternating row colors
            if index % 2 == 0:
                self.apps_listbox.itemconfig(index, {'bg': '#f0f0f0'})
            else:
                self.apps_listbox.itemconfig(index, {'bg': '#ffffff'})
        self.update_config_display()

    def update_config_display(self):
        self.config_text.config(state=tk.NORMAL)
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, json.dumps(self.app_locker.config, indent=4))
        self.config_text.config(state=tk.DISABLED)






    def update_state_display(self):
        self.state_text.delete(1.0, tk.END)
        self.state_text.insert(tk.END, json.dumps(self.app_locker.state, indent=4))

    def export_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="FadCrypt_config.json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.app_locker.config, f, indent=4)
                self.show_message("Success", f"Config exported successfully to {file_path}")
            except Exception as e:
                self.show_message("Error", f"Failed to export config: {e}")

    def export_state(self):
        self.app_locker.export_state()
        self.show_message("Info", "State exported to state.json")
  

    def create_password(self):
        if os.path.exists(self.app_locker.password_file):
            self.show_message("Info", "Password already exists. Use 'Change Password' to modify.")
        else:
            password = self.ask_password("Create Password", "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:")
            if password:
                self.app_locker.create_password(password)
                self.show_message("Success", "Password created successfully.")

    def change_password(self):
        if os.path.exists(self.app_locker.password_file):
            old_password = self.ask_password("Change Password", "Enter your old password:")
            if old_password and self.app_locker.verify_password(old_password):
                new_password = self.ask_password("New Password", "Make sure to securely note down your password.\nIf forgotten, the tool cannot be stopped,\nand recovery will be difficult!\nEnter a new password:")
                if new_password:
                    self.app_locker.change_password(old_password, new_password)
                    self.show_message("Success", "Password changed successfully.")
            else:
                self.show_message("Error", "Incorrect old password.")
        else:
            self.show_message("Oops!", "How do I change a password that doesn’t exist? :(")

    def add_application(self):
        app_name = self.ask_password("Add Application", "Enter the name of the application:")
        if app_name:
            app_path = filedialog.askopenfilename(title="Select application executable")
            if app_path:
                self.app_locker.add_application(app_name, app_path)
                self.update_apps_listbox()
                self.update_config_display()  # Update config tab
                self.show_message("Success", f"Application {app_name}\nadded successfully.")


    def remove_application(self):
        selection = self.apps_listbox.curselection()
        if selection:
            app_name = self.apps_listbox.get(selection[0]).split(" - ")[0].strip()  # Remove leading spaces
            self.app_locker.remove_application(app_name)
            self.update_apps_listbox()
            self.update_config_display()
            self.show_message("Success", f"Application {app_name}\nremoved successfully.")
        else:
            self.show_message("Error", "Please select an application to remove.")

    def rename_application(self):
        selection = self.apps_listbox.curselection()
        if selection:
            old_name = self.apps_listbox.get(selection[0]).split(" - ")[0].strip()  # Remove leading spaces
            new_name = self.ask_password("Rename Application", f"Enter new name for {old_name}:")
            if new_name:
                for app in self.app_locker.config["applications"]:
                    if app["name"] == old_name:
                        app["name"] = new_name
                        break
                self.update_apps_listbox()
                self.update_config_display()
                self.show_message("Success", f"Application renamed from {old_name} to {new_name}.")
        else:
            self.show_message("Error", "Please select an application to rename.")

    def start_monitoring(self, auto_start=False):
        if os.path.exists(self.app_locker.password_file):
            # Lock tools if required
            if self.lock_tools_var.get():
                print("Disabling Terminal and System Monitor...")
                self.disable_tools()

            # Start monitoring in a separate thread
            threading.Thread(target=self.app_locker.start_monitoring, daemon=True).start()

            if not auto_start:
                self.show_message("Info", "Monitoring started. Use the system tray icon to stop.")
                # Add to startup on manual start
                print("Adding to startup manually...")
                self.add_to_startup()

            self.master.withdraw()  # Hide the main window
        else:
            self.show_message("Hey!", "Please set your password, and I'll enjoy some biryani 🍚.\nBy the way, do you like biryani as well?")
            return False


    def add_to_startup(self):
        try:
           # Determine the correct Exec command for startup
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Packaged with PyInstaller
                exec_command = f'"{sys.executable}" --auto-monitor'
            else:
                # Running as a script
                exec_command = f'{sys.executable} "{os.path.abspath(sys.argv[0])}" --auto-monitor'
            desktop_entry = f"""[Desktop Entry]
                                Type=Application
                                Exec={exec_command}
                                Hidden=false
                                NoDisplay=false
                                X-GNOME-Autostart-enabled=true
                                Name=FadCrypt
                                Comment=Start FadCrypt automatically
                                Version=1.0
                                """
            autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            autostart_path = os.path.join(autostart_dir, "FadCrypt.desktop")

            with open(autostart_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(autostart_path, 0o755)
            print(f"FadCrypt added to startup: {autostart_path}")
        except Exception as e:
            print(f"Error adding to startup: {e}")

    def remove_from_startup(self):
        try:
            autostart_path = os.path.join(os.path.expanduser("~"), ".config", "autostart", "FadCrypt.desktop")
            if os.path.exists(autostart_path):
                os.remove(autostart_path)
                print("FadCrypt removed from startup.")
            else:
                print("FadCrypt was not in startup.")
        except Exception as e:
            print(f"Error removing from startup: {e}")

    def stop_monitoring(self):
        # Enable the tools if they were disabled
        if self.lock_tools_var.get():
            print("Enabling Terminal and System Monitor...")
            self.enable_tools()

        if self.app_locker.monitoring:
            password = self.ask_password("Stop Monitoring", "Enter your password to stop monitoring:")
            if password and self.app_locker.verify_password(password):
                self.app_locker.stop_monitoring()
                # Remove from startup when monitoring is stopped
                self.remove_from_startup()
                self.show_message("Success", "Monitoring stopped.")
                self.master.deiconify()  # Show the main window
            else:
                self.show_message("Error", "Incorrect password. Monitoring will continue.")
        else:
            self.show_message("Info", "Monitoring is not running.")




    
    # def block_registry_editor():
    #     try:
    #         # Disable Registry Editor
    #         reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System')
    #         winreg.SetValueEx(reg_key, 'DisableRegistryTools', 0, winreg.REG_DWORD, 1)
    #         winreg.CloseKey(reg_key)
    #         print("Registry Editor blocked.")
    #     except Exception as e:
    #         print(f"Error blocking Registry Editor: {e}")

    # def unblock_registry_editor():
    #     try:
    #         # Open the registry key
    #         reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_SET_VALUE)
    #         try:
    #             # Attempt to delete the DisableRegistryTools value
    #             winreg.DeleteValue(reg_key, 'DisableRegistryTools')
    #             print("Registry Editor unblocked.")
    #         except FileNotFoundError:
    #             print("Registry Editor was not blocked.")
    #         finally:
    #             winreg.CloseKey(reg_key)
    #     except Exception as e:
    #         print(f"Error unblocking Registry Editor: {e}")


    def disable_tools(self):
        """Disable system tools on Linux (use with extreme caution)"""
        try:
            #list of common terminal and system monitor executables.
            tools_to_disable = [
                '/usr/bin/gnome-terminal',
                '/usr/bin/konsole',
                '/usr/bin/xterm',
                '/usr/bin/gnome-system-monitor',
                '/usr/bin/htop',
                '/usr/bin/top'
            ]
            
            disabled_tools = []
            chmod_commands = []
            for tool in tools_to_disable:
                if os.path.exists(tool) and os.access(tool, os.X_OK):
                    chmod_commands.append(f'chmod 644 "{tool}"')
                    disabled_tools.append(tool)
            
            if chmod_commands:
                # Run all chmod commands in one pkexec call
                command = '; '.join(chmod_commands)
                try:
                    subprocess.run(['pkexec', 'bash', '-c', command], check=True)
                    print(f"Disabled tools: {disabled_tools}")
                    
                    # Save the list of modified tools for re-enabling later.
                    disabled_tools_file = os.path.join(self.app_locker.get_fadcrypt_folder(), 'disabled_tools.txt')
                    with open(disabled_tools_file, 'w') as f:
                        f.write('\n'.join(disabled_tools))
                except subprocess.CalledProcessError as e:
                    print(f"Failed to disable tools: {e}")
            else:
                print("No tools were disabled (tools not found or already disabled).")
                
        except Exception as e:
            print(f"An error occurred in disable_tools: {e}")

    def enable_tools(self):
        """Re-enable previously disabled tools"""
        try:
            disabled_tools_file = os.path.join(self.app_locker.get_fadcrypt_folder(), 'disabled_tools.txt')
            if os.path.exists(disabled_tools_file):
                with open(disabled_tools_file, 'r') as f:
                    tools = f.read().strip().split('\n')

                chmod_commands = []
                valid_tools = []
                for tool in tools:
                    if tool and os.path.exists(tool):
                        chmod_commands.append(f'chmod 755 "{tool}"')
                        valid_tools.append(tool)

                if chmod_commands:
                    # Run all chmod commands in one pkexec call
                    command = '; '.join(chmod_commands)
                    try:
                        subprocess.run(['pkexec', 'bash', '-c', command], check=True)
                        for tool in valid_tools:
                            print(f"Re-enabled: {tool}")
                        
                        # Clean up the record file after restoring permissions.
                        os.remove(disabled_tools_file)
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to restore permissions: {e}")
                else:
                    print("No valid tools found to re-enable.")
            else:
                print("No disabled tools file found to re-enable.")
        except Exception as e:
            print(f"An error occurred in enable_tools: {e}")

    def save_settings(self, *args):
        settings = {
            "lock_tools": self.lock_tools_var.get(),
            "password_dialog_style": self.password_dialog_style.get(),
            "wallpaper_choice": self.wallpaper_choice.get()
            # Other settings can be added here
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Settings saved to {self.settings_file}")  # Debug print



    def load_settings(self):
        if os.path.exists(self.settings_file):
            print(f"load_settings: Loading settings from {self.settings_file}")
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.lock_tools_var.set(settings.get("lock_tools", True))
                self.password_dialog_style.set(settings.get("password_dialog_style", "simple"))
                self.wallpaper_choice.set(settings.get("wallpaper_choice", "default"))
        else:
            print("load_settings: Probably file does not exist.")
            # If settings file does not exist, use defaults
            self.lock_tools_var.set(True)  # Default to locking tools
            self.password_dialog_style.set("simple")
            self.wallpaper_choice.set("default")
        self.update_preview()





    def ask_password(self, title, prompt):
        if self.password_dialog_style.get() == "simple":
            return self.custom_dialog(title, prompt, fullscreen=False)
        else:
            return self.custom_dialog(title, prompt, fullscreen=True)







    def custom_dialog(self, title, prompt, fullscreen=False, input_required=True):
        dialog = tk.Toplevel(self.master)
        dialog.attributes('-alpha', 0.0)  # Start fully transparent
        dialog.update_idletasks()  # Update geometry-related information

        if fullscreen:
            dialog.attributes('-fullscreen', True)
        else:
            dialog.geometry("300x200")
        # Center the dialog on the screen
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog_width = 400
        dialog_height = 250
        position_x = (screen_width // 2) - (dialog_width // 2)
        position_y = (screen_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")

        dialog.grab_set()

        if fullscreen:
            # Load and display wallpaper
            wallpaper_path = self.get_wallpaper_path()
            wallpaper = Image.open(wallpaper_path)
            wallpaper = wallpaper.resize((dialog.winfo_screenwidth(), dialog.winfo_screenheight()), Image.LANCZOS)
            wallpaper = ImageTk.PhotoImage(wallpaper)
            background_label = tk.Label(dialog, image=wallpaper)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            background_label.image = wallpaper

        frame = tk.Frame(dialog, bg='white', bd=5)
        if fullscreen:
            frame.place(relx=0.5, rely=0.5, anchor='center')
        else:
            frame.pack(expand=True, fill='both', padx=10, pady=10)

        tk.Label(frame, text=title, font=("Arial", 14, "bold"), bg='white').pack(pady=10)
        tk.Label(frame, text=prompt, font=("Arial", 10), bg='white').pack(pady=5)
        
        result = [None]  # Use a list to store the result

        if input_required:
            password_entry = tk.Entry(frame, show='*', font=("Arial", 12), width=30)
            password_entry.pack(pady=10)
            
            # Set focus after the dialog is fully rendered
            dialog.after(100, password_entry.focus_set)

            def on_ok(event=None):  # Accept an optional event argument
                result[0] = password_entry.get()
                self.fade_out(dialog)

            ok_button = ttk.Button(frame, text="OK", command=on_ok, style="red.TButton", width="11")
            ok_button.pack(side=tk.BOTTOM, pady=10, anchor='center')

            # Bind the Enter key to the OK button
            dialog.bind('<Return>', on_ok)
        else:
            def on_ok(event=None):  # Accept an optional event argument
                result[0] = True
                self.fade_out(dialog)

            ok_button = ttk.Button(frame, text="OK", command=on_ok, style="red.TButton", width="11")
            ok_button.pack(side=tk.BOTTOM, pady=10, anchor='center')

            # Bind the Enter key to the OK button
            dialog.bind('<Return>', on_ok)

        self.fade_in(dialog)
        dialog.wait_window()
        return result[0]


    def fade_in(self, window):
        alpha = 0.0
        window.attributes('-alpha', alpha)
        window.deiconify()
        while alpha < 1.0:
            alpha += 0.2  # Increased step for faster animation
            window.attributes('-alpha', min(alpha, 1.0))
            window.update()
            time.sleep(0.02)  # Reduced sleep time for faster animation

    def fade_out(self, window):
        alpha = 1.0
        while alpha > 0.0:
            alpha -= 0.2  # Increased step for faster animation
            window.attributes('-alpha', max(alpha, 0.0))
            window.update()
            time.sleep(0.02)  # Reduced sleep time for faster animation
        window.destroy()

    def show_message(self, title, message, message_type="info"):
        return self.custom_dialog(title, message, fullscreen=False, input_required=False)
















    def full_screen_password_dialog(self, title, prompt):
        dialog = tk.Toplevel(self.master)
        dialog.attributes('-fullscreen', True)
        dialog.grab_set()

        # Load and display wallpaper
        wallpaper_path = self.get_wallpaper_path()
        wallpaper = Image.open(wallpaper_path)
        wallpaper = wallpaper.resize((dialog.winfo_screenwidth(), dialog.winfo_screenheight()), Image.LANCZOS)
        wallpaper = ImageTk.PhotoImage(wallpaper)
        background_label = tk.Label(dialog, image=wallpaper)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = wallpaper

        frame = tk.Frame(dialog, bg='white', bd=5)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(frame, text=title, font=("Arial", 16, "bold"), bg='white').pack(pady=10)
        tk.Label(frame, text=prompt, font=("Arial", 12), bg='white').pack(pady=5)
        password_entry = tk.Entry(frame, show='*', font=("Arial", 12), width=30)
        password_entry.pack(pady=10)

        password = [None]  # Use a list to store the password

        def on_ok():
            password[0] = password_entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        tk.Button(frame, text="OK", command=on_ok, font=("Arial", 12)).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(frame, text="Cancel", command=on_cancel, font=("Arial", 12)).pack(side=tk.RIGHT, padx=10, pady=10)

        dialog.wait_window()
        return password[0]

    def get_wallpaper_path(self):
        wallpapers = {
            "default": self.resource_path("img/wall1.jpg"),
            "H4ck3r": self.resource_path("img/wall2.jpg"),
            "Binary": self.resource_path("img/wall3.jpg"),
            "encrypted": self.resource_path("img/wall4.jpg")
        }
        return wallpapers.get(self.wallpaper_choice.get(), wallpapers["default"])
    
    









    def start_snake_game(self):
        def run_snake_game(gui_instance):
            # Initialize Pygame
            pygame.init()

            # Colors
            BLACK = (0, 0, 0)
            WHITE = (255, 255, 255)
            RED = (255, 0, 0)
            GREEN = (0, 255, 0)
            YELLOW = (255, 255, 0)
            TRANSPARENT = (0, 0, 0)

            # New dark mode colors
            DARK_GRAY = (30, 30, 30)
            DARKER_GRAY = (20, 20, 20)
            OBSTACLE_COLOR = (100, 100, 100)  # Single color for obstacles



            # Game settings
            FPS = 14

            # Pygame setup
            info = pygame.display.Info()
            WINDOW_WIDTH = info.current_w
            WINDOW_HEIGHT = info.current_h
            window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
            pygame.display.set_caption('Minimal Snake Game - FadSec-Lab')
            clock = pygame.time.Clock()

            # Fonts
            font_small = pygame.font.SysFont('arial', 25)
            font_medium = pygame.font.SysFont('arial', 50)
            font_large = pygame.font.SysFont('arial', 80)

            # Calculate game area to maintain aspect ratio
            game_area_height = int(WINDOW_HEIGHT * 0.9)
            game_area_width = int(game_area_height * 4 / 3)
            if game_area_width > int(WINDOW_WIDTH * 0.9):
                game_area_width = int(WINDOW_WIDTH * 0.9)
                game_area_height = int(game_area_width * 3 / 4)


            game_area_top = (WINDOW_HEIGHT - game_area_height) // 2
            game_area_left = (WINDOW_WIDTH - game_area_width) // 2


            BLOCK_SIZE = min(game_area_width // 60, game_area_height // 45)
            BORDER_WIDTH = 8  # Increase border width for visibility

            class Snake:
                def __init__(self):
                    self.length = 1
                    self.positions = [((game_area_width // 2), (game_area_height // 2))]
                    self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    self.color1 = (0, 200, 0)
                    self.color2 = (0, 255, 0)
                    self.score = 0

                def get_head_position(self):
                    return self.positions[0]

                def move(self):
                    cur = self.get_head_position()
                    x, y = self.direction
                    new = (((cur[0] + (x * BLOCK_SIZE)) % (game_area_width - 2*BORDER_WIDTH)), 
                        ((cur[1] + (y * BLOCK_SIZE)) % (game_area_height - 2*BORDER_WIDTH)))
                    
                    if len(self.positions) > 2 and new in self.positions[2:]:
                        return False
                    
                    self.positions.insert(0, new)
                    if len(self.positions) > self.length:
                        self.positions.pop()
                    return True

                def reset(self):
                    self.length = 1
                    self.positions = [((game_area_width // 2), (game_area_height // 2))]
                    self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    self.score = 0

                def draw(self, surface):
                    for i, p in enumerate(self.positions):
                        color = self.color1 if i % 2 == 0 else self.color2
                        pygame.draw.rect(surface, color, 
                                        (p[0] + game_area_left + BORDER_WIDTH, 
                                        p[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))

                def handle_keys(self):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("handle_keys: Quitting game...")
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP:
                                self.turn(UP)
                            elif event.key == pygame.K_DOWN:
                                self.turn(DOWN)
                            elif event.key == pygame.K_LEFT:
                                self.turn(LEFT)
                            elif event.key == pygame.K_RIGHT:
                                self.turn(RIGHT)
                            elif event.key == pygame.K_ESCAPE:
                                return "PAUSE"
                    
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        return "FAST"
                    return "NORMAL"

                def turn(self, direction):
                    if (direction[0] * -1, direction[1] * -1) == self.direction:
                        return
                    else:
                        self.direction = direction

            class Food:
                def __init__(self):
                    self.position = (0, 0)
                    self.color = RED
                    self.randomize_position()

                def randomize_position(self):
                    self.position = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                                    random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)

                def draw(self, surface):
                    pygame.draw.rect(surface, self.color, 
                                    (self.position[0] + game_area_left + BORDER_WIDTH, 
                                    self.position[1] + game_area_top + BORDER_WIDTH, 
                                    BLOCK_SIZE, BLOCK_SIZE))

            class Obstacle:
                def __init__(self):
                    self.positions = []

                def add_obstacle(self):
                    new_pos = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                            random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)
                    if new_pos not in self.positions:
                        self.positions.append(new_pos)

                def draw(self, surface):
                    for pos in self.positions:
                        pygame.draw.rect(surface, OBSTACLE_COLOR, 
                                        (pos[0] + game_area_left + BORDER_WIDTH, 
                                        pos[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))
            class PowerUp:
                def __init__(self):
                    self.position = (0, 0)
                    self.color = YELLOW
                    self.active = False
                    self.type = None

                def spawn(self):
                    self.position = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                                    random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)
                    self.type = random.choice(['speed', 'slow', 'shrink'])
                    self.active = True

                def draw(self, surface):
                    if self.active:
                        pygame.draw.rect(surface, self.color, 
                                        (self.position[0] + game_area_left + BORDER_WIDTH, 
                                        self.position[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))

            def draw_patterned_background(surface, rect, color1, color2, block_size):
                for y in range(rect.top, rect.bottom, block_size):
                    for x in range(rect.left, rect.right, block_size):
                        color = color1 if (x // block_size + y // block_size) % 2 == 0 else color2
                        pygame.draw.rect(surface, color, (x, y, block_size, block_size))

            def draw_text(surface, text, size, x, y, color=WHITE):
                font = pygame.font.SysFont('arial', size)
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect()
                text_rect.midtop = (x, y)
                surface.blit(text_surface, text_rect)

            def show_menu(surface):
                surface.fill(BLACK)
                draw_text(surface, "SNAKE GAME", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)
                draw_text(surface, "Press SPACE to start", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                draw_text(surface, "Press Q to quit", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
                pygame.display.flip()
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("show_menu: Quitting game...")
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                waiting = False
                            elif event.key == pygame.K_q:
                                print("show_menu2: Quitting game...")
                                pygame.quit()
                                sys.exit()

            def pause_menu(surface):
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                surface.blit(overlay, (0, 0))
                draw_text(surface, "PAUSED", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)
                draw_text(surface, "Press SPACE to continue", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                draw_text(surface, "Press Q to quit", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
                pygame.display.flip()
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("pause_menu: Quitting game...")
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                return "CONTINUE"
                            elif event.key == pygame.K_q:
                                print("pause_menu returning quit: Quitting game...")
                                return "QUIT"

            def game_over(surface, score, high_score):
                surface.fill(BLACK)
                draw_text(surface, "GAME OVER", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)
                draw_text(surface, f"Score: {score}", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
                draw_text(surface, f"High Score: {high_score}", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
                draw_text(surface, "Press SPACE to play again", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
                draw_text(surface, "Press Q to quit", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 7 // 8)
                pygame.display.flip()
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("game_over: Quitting game...")
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                return "PLAY_AGAIN"
                            elif event.key == pygame.K_q:
                                print("game_over returning quit: Quitting game...")
                                return "QUIT"

            def load_high_score():
                try:
                    # Get the FadCrypt folder path using the gui_instance
                    folder_path = gui_instance.app_locker.get_fadcrypt_folder()
                    # Define the full path to the snake_high_score.json file
                    file_path = os.path.join(folder_path, "snake_high_score.json")
                    # Load the high score from the file
                    with open(file_path, "r") as f:
                        return json.load(f)["high_score"]
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    return 0

            def save_high_score(high_score):
                try:
                    # Get the FadCrypt folder path using the gui_instance
                    folder_path = gui_instance.app_locker.get_fadcrypt_folder()
                    # Define the full path to the snake_high_score.json file
                    file_path = os.path.join(folder_path, "snake_high_score.json")
                    # Save the high score to the file
                    with open(file_path, "w") as f:
                        json.dump({"high_score": high_score}, f)
                except Exception as e:
                    print(f"Error saving high score: {e}")
                    

            def main():
                snake = Snake()
                food = Food()
                obstacles = Obstacle()
                power_up = PowerUp()
                high_score = load_high_score()
                
                level = 1
                obstacles_per_level = 5
                
                for _ in range(obstacles_per_level):
                    obstacles.add_obstacle()

                while True:
                    show_menu(window)
                    
                    game_over_flag = False
                    power_up_timer = 0
                    speed_modifier = 0
                    
                    while not game_over_flag:
                        move_speed = FPS + speed_modifier
                        action = snake.handle_keys()
                        if action == "PAUSE":
                            pause_action = pause_menu(window)
                            if pause_action == "QUIT":
                                print("main: Quitting game...")
                                pygame.quit()
                                sys.exit()
                            continue
                        elif action == "FAST":
                            move_speed = FPS + 10
                        
                        clock.tick(move_speed)
                        
                        if not snake.move():
                            game_over_flag = True
                            break
                        
                        head_pos = snake.get_head_position()
                        if (abs(head_pos[0] - food.position[0]) < BLOCK_SIZE and 
                            abs(head_pos[1] - food.position[1]) < BLOCK_SIZE):
                            snake.length += 1
                            snake.score += 10
                            food.randomize_position()
                            while any(abs(food.position[0] - obs[0]) < BLOCK_SIZE and 
                                    abs(food.position[1] - obs[1]) < BLOCK_SIZE 
                                    for obs in obstacles.positions + snake.positions):
                                food.randomize_position()
                            if snake.score % 50 == 0:
                                level += 1
                                for _ in range(obstacles_per_level):
                                    obstacles.add_obstacle()
                        
                        if not power_up.active and random.randint(1, 100) == 1:
                            power_up.spawn()
                            while any(abs(power_up.position[0] - obs[0]) < BLOCK_SIZE and 
                                    abs(power_up.position[1] - obs[1]) < BLOCK_SIZE 
                                    for obs in obstacles.positions + snake.positions + [food.position]):
                                power_up.spawn()
                        
                        if power_up.active and (abs(head_pos[0] - power_up.position[0]) < BLOCK_SIZE and 
                                                abs(head_pos[1] - power_up.position[1]) < BLOCK_SIZE):
                            if power_up.type == 'speed':
                                speed_modifier = 5
                            elif power_up.type == 'slow':
                                speed_modifier = -5
                            elif power_up.type == 'shrink':
                                snake.length = max(1, snake.length - 2)
                            power_up.active = False
                            power_up_timer = pygame.time.get_ticks()
                        
                        if pygame.time.get_ticks() - power_up_timer > 5000:
                            speed_modifier = 0
                        
                        if any(abs(head_pos[0] - obs[0]) < BLOCK_SIZE and 
                            abs(head_pos[1] - obs[1]) < BLOCK_SIZE 
                            for obs in obstacles.positions):
                            game_over_flag = True
                            break

                        # Clear the entire window
                        window.fill(BLACK)
                        
                        # Draw patterned background with new dark mode colors
                        draw_patterned_background(window, 
                                                pygame.Rect(game_area_left + BORDER_WIDTH, 
                                                            game_area_top + BORDER_WIDTH, 
                                                            game_area_width - 1.5*BORDER_WIDTH, 
                                                            game_area_height - 2*BORDER_WIDTH),
                                                DARK_GRAY, DARKER_GRAY, BLOCK_SIZE)
                        
                        # Draw game area border
                        # pygame.draw.rect(window, BLACK, 
                        #                 (game_area_left, game_area_top, game_area_width, game_area_height), 
                        #                 BORDER_WIDTH)
                        
                        snake.draw(window)
                        food.draw(window)
                        obstacles.draw(window)
                        if power_up.active:
                            power_up.draw(window)
                        
                        # Load the logo
                        logo = pygame.image.load(self.resource_path("img/fadsec.png"))  # Ensure 'fadsec.png' is in the same directory
                        # Determine the new size for the logo
                        scale_factor = 0.5  # Scale to 50% of the original size
                        logo_width, logo_height = logo.get_size()
                        new_logo_width = int(logo_width * scale_factor)
                        new_logo_height = int(logo_height * scale_factor)

                        # Scale the logo
                        scaled_logo = pygame.transform.scale(logo, (new_logo_width, new_logo_height))

                        # Position for the bottom center
                        logo_x = (WINDOW_WIDTH - new_logo_width) // 2  # Center horizontally
                        logo_y = WINDOW_HEIGHT - new_logo_height - -50  # 10 pixels from the bottom
                        

                        draw_text(window, f"Score: {snake.score}", 25, WINDOW_WIDTH - 70, 10)
                        draw_text(window, f"High Score: {high_score}", 25, WINDOW_WIDTH - 100, 40)
                        draw_text(window, f"Level: {level}", 25, 70, 10)
                        draw_text(window, "Press ESC to pause, and hold SHIFT to move faster.", 25, WINDOW_WIDTH // 2, 10)

                        # Draw the scaled logo
                        window.blit(scaled_logo, (logo_x, logo_y))
                        
                        # # logo in gray at the bottom left
                        # logo_text = "FadSec-Lab © 2024"
                        # logo_color = (169, 169, 169)  # Gray color (RGB)
                        # # the value after logo text is for font
                        # draw_text(window, logo_text, 15, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40, color=logo_color)
                        
                        pygame.display.update()
                    
                    if snake.score > high_score:
                        high_score = snake.score
                        save_high_score(high_score)
                    
                    action = game_over(window, snake.score, high_score)
                    if action == "QUIT":
                        print("main, game: Quitting game...")
                        pygame.quit()
                        sys.exit()
                    snake.reset()
                    level = 1
                    obstacles = Obstacle()
                    for _ in range(obstacles_per_level):
                        obstacles.add_obstacle()

            if __name__ == "__main__":
                UP = (0, -1)
                DOWN = (0, 1)
                LEFT = (-1, 0)
                RIGHT = (1, 0)
                main()

        # Run the game in a new thread, passing the GUI instance
        snake_game_thread = threading.Thread(target=run_snake_game, args=(self,))
        snake_game_thread.start()








    






























class AppLocker:
    # def __init__(self, gui, config_file="config.json", state_file="state.json"):
    def __init__(self, gui):
        self.gui = gui # Store reference to the AppLockerGUI instance
        self.config_file = self.get_config_file_path()
        # self.key = self.generate_key()
        # self.fernet = Fernet(self.key)

        # self.config_file = {"applications": []}  # In-memory config
        self.password_file = os.path.join(self.get_fadcrypt_folder(), 'encrypted_password.bin')
        self.config = {"applications": []}  # In-memory configuration
        self.state = {"unlocked_apps": []}  # In-memory state

        self.load_config()  # Load config from disk
        self.load_state()
        self.monitoring = False
        self.monitoring_thread = None
        # self.state_file = {"unlocked_apps": []}  # In-memory state
        self.load_state()
        self.icon = None
        self.apps_showing_dialog = set()
        self.observers = []
        self.pending_launch = None
        


    def get_fadcrypt_folder(self):
        path = os.path.join(os.getenv('HOME'), '.FadCrypt')  # Changed APPDATA to HOME and updated folder name
        os.makedirs(path, exist_ok=True)
        return path
    
        

    def load_config(self):
        print("=== LOAD_CONFIG START ===")
        print(f"Loading config from {self.config_file}")  # Debug print
        
        # Check if the config file exists
        if os.path.exists(self.config_file):
            if os.path.exists(self.password_file):
                password = self.load_password()
                print(f"Password file exists, password loaded (length: {len(password)})")
                decrypted_data = self.decrypt_data(password, self.config_file)
                if decrypted_data is not None:
                    self.config = decrypted_data
                    print(f"Config loaded: {self.config}")  # Debug print
                else:
                    print("Decryption failed. Creating new config.")  # Debug print
                    self.config = {"applications": []}
                    self.save_config()  # Save a new encrypted config if decryption fails
            else:
                print("Password file does not exist.")
                self.config = {"applications": []}
                # Optionally, save default config if password file is missing
                self.save_config()
        else:
            print("load_config: Config file does not exist. Initialized with default config.")  # Debug print
            self.config = {"applications": []}
            # Create the config file with default content and encrypt it
            self.save_config()
        print("=== LOAD_CONFIG END ===")

    def save_config(self):
        if os.path.exists(self.password_file):
            password = self.load_password()
            self.encrypt_data(password, self.config, self.config_file)
            print(f"Config saved to {self.config_file}")  # Debug print
        else:
            print("Password file does not exist. Cannot save config.")
            self.gui.show_message("Important!", "Please create a password before proceeding and ensure\n it's securely noted down. If forgotten, recovery can be\nchallenging, and the tool cannot be stopped.\n\nDon't forget to review the ReadMe for\nessential information about the tool and its options.")




    def load_password(self):
        with open(self.password_file, 'rb') as f:
            return f.read()
        
    def get_key(self):
        # Generate a key for encryption/decryption
        # You can generate a key using: Fernet.generate_key()
        # Save this key securely; for demo, we're using a hardcoded key.
        return base64.urlsafe_b64encode(b"your-secret-key-32-bytes-long")

    def get_config_file_path(self):
        return os.path.join(self.get_fadcrypt_folder(), 'config.json')
    
        
    def generate_key(self):
        key_path = os.path.join(os.getenv('HOME'), '.FadCrypt', 'config.key')  # Changed APPDATA to HOME and updated folder name
        print(f"Key file path: {key_path}")  # Debug print
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key
    
    def encrypt_data(self, password, data, file_path):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password)
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        json_data = json.dumps(data).encode()
        encrypted_data = encryptor.update(json_data) + encryptor.finalize()
        with open(file_path, 'wb') as f:
            f.write(salt + encryptor.tag + encrypted_data)

    def decrypt_data(self, password, file_path):
        try:
            with open(file_path, 'rb') as f:
                salt = f.read(16)
                tag = f.read(16)
                encrypted_data = f.read()
            print(f"Salt: {salt.hex()}")
            print(f"Tag: {tag.hex()}")
            print(f"Encrypted Data: {encrypted_data.hex()}")
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password)
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"Error decrypting data: {e}")
            self.gui.show_message("Decryption failed", "Config file tampered.\nPlease delete the config.json file and start fresh.")
            return None
    
    def load_state(self):
        print("Loading state from disk...")
        state_file = os.path.join(self.get_fadcrypt_folder(), 'state.json')
        if os.path.exists(state_file) and os.path.exists(self.password_file):
            password = self.load_password()
            if password:
                decrypted_data = self.decrypt_data(password, state_file)
                if decrypted_data is not None:
                    self.state = decrypted_data
                    print(f"State loaded: {self.state}")
                else:
                    print("Failed to decrypt state file, using default state")
                    self.state = {"unlocked_apps": []}
            else:
                print("Password file not found, using default state")
                self.state = {"unlocked_apps": []}
        else:
            print("State file not found, using default state")
            self.state = {"unlocked_apps": []}

    def save_state(self):
        if os.path.exists(self.password_file):
            password = self.load_password()
            state_file = os.path.join(self.get_fadcrypt_folder(), 'state.json')
            self.encrypt_data(password, self.state, state_file)
            print(f"State saved to {state_file}: {self.state}")
        else:
            print("Password file not found, cannot save state")
    
    def export_config(self):
        export_path = "FadCrypt_config.json"
        print(f"Exporting config to {export_path}")  # Debug print
        with open(export_path, "w") as f:
            json.dump(self.config, f, indent=4)
        print("Config exported.")  # Debug print

    def export_state(self):
        export_path = "state.json"
        print(f"Exporting state to {export_path}")  # Debug print
        with open(export_path, "w") as f:
            json.dump(self.state, f, indent=4)
        print("State exported.")  # Debug print


    

    def create_password(self, password):
        try:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_hash = encryptor.update(password.encode()) + encryptor.finalize()
            
            # FIXED: Re-added the missing lines to write the password file.
            with open(self.password_file, "wb") as f:
                f.write(salt + encryptor.tag + encrypted_hash)
            
        except Exception as e:
            # Note: Changed to self.gui.show_message for correctness
            self.gui.show_message("Error", f"Error creating password: {e}")
            
    def change_password(self, old_password, new_password):
        if self.verify_password(old_password):
            self.create_password(new_password)

            # Re-encrypt the configuration file with the new password
            self.save_config()  # This will use the new password
            print("change_password: Re-encrypt the configuration file with the new password")
        else:
            self.show_message("Error", "Incorrect old password.")

    def verify_password(self, password):
        try:
            if not os.path.exists(self.password_file):
                return False

            with open(self.password_file, "rb") as f:
                salt = f.read(16)
                tag = f.read(16)
                encrypted_hash = f.read()

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_hash = decryptor.update(encrypted_hash) + decryptor.finalize()

            return password.encode() == decrypted_hash
        # except InvalidTag as ee:
        #     messagebox.showerror("Error", f"Encryptepd file corrupted: {ee}")
        #     return False
        except Exception as e:
            print("Error", f"Error verifying password: {e}")
        return False

    def add_application(self, app_name, app_path):
        self.config["applications"].append({"name": app_name, "path": app_path})
        self.save_config()

    def remove_application(self, app_name):
        self.config["applications"] = [app for app in self.config["applications"] if app["name"] != app_name]
        self.save_config()

    def block_application(self, app_name, app_path):
        while self.monitoring:
            try:
                # Get process name from path for better matching
                process_name = os.path.basename(app_path) if app_path else app_name
                
                # Handle .desktop files
                if app_path.endswith('.desktop'):
                    process_name = self._get_exec_from_desktop(app_path)
                
                app_processes = []
                for proc in psutil.process_iter(['name', 'pid', 'cmdline', 'status', 'ppid']):
                    try:
                        # Skip zombie processes - they are already dead but not reaped
                        if proc.info['status'] == psutil.STATUS_ZOMBIE:
                            continue  # Skip zombie processes silently
                        
                        # Match by process name or command line
                        proc_name = proc.info['name'].lower()
                        proc_cmdline = proc.info['cmdline'] if proc.info['cmdline'] else []
                        
                        # Direct name match
                        if proc_name == process_name.lower():
                            app_processes.append(proc)
                        # Command line match
                        elif proc_cmdline and any(process_name.lower() in cmd.lower() for cmd in proc_cmdline if cmd):
                            app_processes.append(proc)
                        # Special handling for Chrome/Chromium-based apps - catch all child processes
                        elif 'chrome' in process_name.lower() and ('chrome' in proc_name or 
                                                                   any('chrome' in str(cmd).lower() for cmd in proc_cmdline if cmd)):
                            app_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if app_processes:
                    print(f"Found {len(app_processes)} processes for {app_name}, unlocked_apps: {self.state['unlocked_apps']}, showing_dialog: {app_name in self.apps_showing_dialog}")
                    if app_name not in self.state["unlocked_apps"]:
                        if app_name not in self.apps_showing_dialog:
                            print(f"Blocking {app_name}: terminating {len(app_processes)} processes")
                            for proc in app_processes:
                                print(f"Killing process {proc.info['pid']}: {proc.info['name']} - cmdline: {proc.info['cmdline']}")
                                # Kill child processes first
                                for child in proc.children(recursive=True):
                                    try:
                                        child.kill()
                                        print(f"Killed child process {child.pid}")
                                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                        print(f"Failed to kill child {child.pid}: {e}")
                                try:
                                    proc.kill()  # Use kill instead of terminate for immediate blocking
                                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                    print(f"Failed to kill process {proc.info['pid']}: {e}")
                            
                            print(f"Showing password dialog for {app_name}")
                            self.apps_showing_dialog.add(app_name)
                            self.gui.master.after(0, self._show_password_dialog, app_name, app_path)
                            time.sleep(1)
                        else:
                            # App is showing dialog, but new processes appeared - kill them too
                            print(f"Blocking additional {app_name} processes while dialog is showing: terminating {len(app_processes)} processes")
                            for proc in app_processes:
                                print(f"Killing additional process {proc.info['pid']}: {proc.info['name']} - cmdline: {proc.info['cmdline']}")
                                # Kill child processes first
                                for child in proc.children(recursive=True):
                                    try:
                                        child.kill()
                                        print(f"Killed child process {child.pid}")
                                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                        print(f"Failed to kill child {child.pid}: {e}")
                                try:
                                    proc.kill()  # Use kill instead of terminate for immediate blocking
                                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                    print(f"Failed to kill process {proc.info['pid']}: {e}")
                    else:
                        print(f"{app_name} is unlocked, sleeping for 7 seconds")
                        time.sleep(7)
                
                # Only remove from unlocked_apps if no processes found for an extended period
                # This prevents premature removal right after launching
                if app_name in self.state["unlocked_apps"] and not app_processes:
                    # Check if we've seen no processes for this app recently
                    if not hasattr(self, f"{app_name}_no_process_count"):
                        setattr(self, f"{app_name}_no_process_count", 0)
                    
                    count = getattr(self, f"{app_name}_no_process_count")
                    count += 1
                    setattr(self, f"{app_name}_no_process_count", count)
                    
                    # Only remove after 10 consecutive checks with no processes (about 0.5 seconds)
                    if count >= 10:
                        print(f"Auto-locking {app_name} (no active processes found)")
                        self.state["unlocked_apps"].remove(app_name)
                        self.save_state()
                        delattr(self, f"{app_name}_no_process_count")
                    # Don't print the counting to avoid terminal clutter
                elif app_name in self.state["unlocked_apps"] and app_processes:
                    # Reset counter if processes are found
                    if hasattr(self, f"{app_name}_no_process_count"):
                        delattr(self, f"{app_name}_no_process_count")
                
                time.sleep(0.05)  # Very fast monitoring for near-instant blocking
            except Exception as e:
                print(f"Error in block_application: {e}")

    def _get_exec_from_desktop(self, desktop_path):
        """Extract executable name from .desktop file"""
        try:
            with open(desktop_path, 'r') as f:
                for line in f:
                    if line.startswith('Exec='):
                        exec_line = line.split('=', 1)[1].strip()
                        parts = shlex.split(exec_line)
                        executable = ""
                        for part in parts:
                            if '=' not in part:
                                executable = part
                                break
                        return executable.split('/')[-1] if executable else ""
        except Exception as e:
            print(f"Error parsing desktop file: {e}")
        return os.path.basename(desktop_path)

    def _show_password_dialog(self, app_name, app_path):
        try:
            try:
                password = self.gui.ask_password("Password", f"Enter your password to unlock {app_name}:")
            except Exception as e:
                print(f"Error in asking for password in _show_password_dialog: {e}")
                return

            if password is None:
                print(f"Password dialog cancelled for {app_name}")
                return

            try:
                if self.verify_password(password):
                    print(f"Password verified successfully for {app_name}, adding to unlocked_apps")
                    self.state["unlocked_apps"].append(app_name)
                    self.save_state()
                    print(f"State saved, unlocked_apps now: {self.state['unlocked_apps']}")

                    # Launch the app
                    try:
                        # Determine if it's a known GUI app (browser, etc)
                        gui_apps = ['chrome', 'chromium', 'firefox', 'brave', 'opera', 'edge', 
                                   'vivaldi', 'code', 'slack', 'discord', 'telegram',
                                   'vlc', 'gimp', 'libreoffice', 'thunderbird', 'zoom', 'teams', 'obs', 'steam', 'nautilus', 'dolphin', 'kate', 'gedit', 'kdenlive', 'krita', 'inkscape', 'blender', 'audacity', 'shotcut', 'code', 'pycharm', 'eclipse', 'intellij', 'sublime', 'virtualbox', 'postman', 'docker', 'filezilla', 'wireshark', 'gparted', 'transmission', 'remmina']
                        
                        is_gui_app = any(gui_app in app_path.lower() or gui_app in app_name.lower() 
                                        for gui_app in gui_apps)
                        
                        if app_path.lower().endswith('.desktop'):
                            # Launch .desktop files with xdg-open in detached mode
                            subprocess.Popen(['xdg-open', app_path], 
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL,
                                           start_new_session=True)
                        elif app_path.lower().endswith('.py'):
                            # Launch Python scripts in a new terminal
                            subprocess.Popen(['gnome-terminal', '--', 'python3', app_path],
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL,
                                           start_new_session=True)
                        elif is_gui_app:
                            # Launch known GUI apps directly without terminal
                            subprocess.Popen([app_path],
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL,
                                           start_new_session=True)
                        elif any(bin_dir in app_path for bin_dir in ['/usr/bin', '/bin', '/usr/local/bin']):
                            # Launch CLI tools in a new terminal
                            subprocess.Popen(['gnome-terminal', '--', app_path],
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL,
                                           start_new_session=True)
                        else:
                            # Launch other apps directly (assume GUI)
                            subprocess.Popen([app_path],
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL,
                                           start_new_session=True)
                        print(f"Successfully launched {app_name}")
                    except Exception as e:
                        print(f"Error launching {app_name}: {e}")
                        self.gui.show_message("Error", f"Failed to start {app_name}: {e}")

                else:
                    print(f"Incorrect password entered for {app_name}")
                    self.gui.show_message("Error", f"Incorrect password. {app_name} remains locked.")
            except Exception as e:
                print(f"Error in verifying password or saving state in _show_password_dialog: {e}")
        except Exception as e:
            print(f"General error in _show_password_dialog: {e}")
        finally:
            print(f"Removing {app_name} from apps_showing_dialog")
            self.apps_showing_dialog.discard(app_name)


    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            for app in self.config["applications"]:
                app_name = app["name"]
                app_path = app.get("path", "")
                threading.Thread(target=self.block_application, args=(app_name, app_path), daemon=True).start()
            self._create_system_tray_icon()
        else:
            self.gui.show_message("Info", "Monitoring is already running.")
            return False

    def stop_monitoring(self):
        # if window opened from tray icon, and monitoring is stopped, then show the start button again.
        self.gui.start_button.pack(side=tk.LEFT, padx=10)
        if self.monitoring:
            self.monitoring = False
            if self.icon:
                self.icon.stop()
            
            print("Re-enabling disabled tools...")
            # Re-enable execution for disabled tools
            disabled_tools_file = os.path.join(self.get_fadcrypt_folder(), 'disabled_tools.txt')
            if os.path.exists(disabled_tools_file):
                with open(disabled_tools_file, 'r') as f:
                    tools = f.read().strip().split('\n')

                # Filter out empty lines and non-existent tools
                valid_tools = [tool for tool in tools if tool and os.path.exists(tool)]
                
                if valid_tools:
                    print(f"Re-enabling {len(valid_tools)} tools...")
                    # Create a single command to chmod all tools at once
                    chmod_commands = " && ".join([f"chmod 755 '{tool}'" for tool in valid_tools])
                    try:
                        subprocess.run(['pkexec', 'bash', '-c', chmod_commands], check=True)
                        print(f"Successfully re-enabled all {len(valid_tools)} tools")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to re-enable tools: {e}")
                
                # Clean up the record file
                os.remove(disabled_tools_file)
                print("Disabled tools re-enabled and file removed.")
            else:
                print("No disabled tools file found.")
            
            self.gui.master.deiconify()  # Show the main window
        else:
            self.gui.show_message("Info", "Monitoring is not running.")

    def _create_system_tray_icon(self):
        def on_show_window(icon, item):
            password = self.gui.ask_password("Password", "Enter your password to open window:")
            if password is not None and self.verify_password(password):
                print("on_show_window: correct password, opening window.")
                self.gui.master.deiconify()
                self.gui.master.focus()
                self.gui.start_button.pack_forget()  # Disable the button
                self.gui.master.protocol("WM_DELETE_WINDOW", self._on_close)
            else:
                print("on_show_window: incorrect password, not opening window.")
                self.gui.show_message("Error", "I won't open without a pass!")

        def on_stop(icon, item):
            self.gui.master.after(0, self._password_prompt_and_stop)

        def on_quit(icon, item):
            self.gui.master.after(0, self._password_prompt_and_quit, icon)

        def on_snake(item):
            self.gui.master.after(0, self.gui.start_snake_game)

        try:
            image = Image.open(self.gui.resource_path('img/icon.png'))  # Path to icon.png
            image = image.resize((64, 64), Image.LANCZOS)  # Resize image
        except Exception as e:
            print(f"Failed to load tray icon: {e}")
            image = Image.new('RGB', (64, 64), color=(73, 109, 137))  # Fallback to a rectangle

        menu = Menu(
            MenuItem('Open window', on_show_window),
            MenuItem('Stop Monitoring', on_stop),
            MenuItem('Quit', on_quit),
            MenuItem('Snake 🪱', on_snake)
        )

        self.icon = Icon("AppLocker", image, "FadCrypt", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def _on_close(self):
        if self.monitoring:
            print("Window minimized to system tray.")
            self.gui.master.withdraw()
        else:
            print("_on_close: not monitoring, can't withdraw window. Quitting...")
            sys.exit()  # Quit the app instead of sending to system tray

    def _password_prompt_and_stop(self):
        password = self.gui.ask_password("Password", "Enter your password to stop monitoring:")
        if password is not None and self.verify_password(password):
            self.stop_monitoring()
            # tools disabling feature is disabled
            # if self.gui.lock_tools_var.get():
            #     print("Enabling the cmd, powershell and task managaer...")
            #     self.gui.enable_tools()
            self.gui.show_message("Info", "Monitoring has been stopped.")
        else:
            self.gui.show_message("Error", "Incorrect password or action cancelled. Monitoring will continue.")

    def _password_prompt_and_quit(self, icon):
        password = self.gui.ask_password("Password", "Enter your password to quit:")
        if password is not None and self.verify_password(password):
            self.stop_monitoring()
            icon.stop()
            self.gui.show_message("Info", "Application has been stopped.")
            self.gui.master.quit()
        else:
            self.gui.show_message("Error", "Incorrect password. Application will continue.")




class FileMonitor:
    def __init__(self):
        # self.pid_file = "fadcrypt.pid"
        # self.lock_file = "fadcrypt.lock"

        self.observer = Observer()
        self.backup_folder = None
        self.files_to_monitor = []

    def get_fadcrypt_folder(self):
        path = os.path.join(os.getenv('HOME'), '.FadCrypt')  # Changed APPDATA to HOME and updated folder name
        os.makedirs(path, exist_ok=True)
        return path

    def get_backup_folder(self):
        # Using a folder in the user's home directory for backup
        path = os.path.join(os.getenv('HOME'), '.FadCrypt', 'Backup')  # Changed ProgramData to HOME and updated folder name
        os.makedirs(path, exist_ok=True)
        return path
    
    def set_files_to_monitor(self):
        # Set the files to monitor in the correct directory
        fadcrypt_folder = self.get_fadcrypt_folder()
        self.files_to_monitor = [
            os.path.join(fadcrypt_folder, 'config.json'),
            os.path.join(fadcrypt_folder, 'encrypted_password.bin')
        ]
        self.backup_folder = self.get_backup_folder()






        
    def start_monitoring(self):
        """Start monitoring and handle multiple instances."""
        # Proceed with monitoring setup
        self.set_files_to_monitor()
        event_handler = self.FileChangeHandler(self.files_to_monitor, self.backup_folder)
        self.observer.schedule(event_handler, os.path.dirname(self.files_to_monitor[0]), recursive=False)
        self.observer.start()
                
        print("Started monitoring files...")
    

    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, files_to_monitor, backup_folder):
            super().__init__()
            self.files_to_monitor = files_to_monitor
            self.backup_folder = backup_folder
            # self.initial_restore()  # Restore any missing files from the backup folder
            print("Initial file recovery disabled.")

        def on_modified(self, event):
            if event.src_path in self.files_to_monitor:
                print(f"File modified: {event.src_path}")
                self.backup_files()

        def on_deleted(self, event):
            if event.src_path in self.files_to_monitor:
                print(f"File deleted: {event.src_path}")
                self.restore_files()

        def backup_files(self):
            # Ensure backup directory exists
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)
                print(f"Backup folder created: {self.backup_folder}")

            for file_path in self.files_to_monitor:
                if os.path.exists(file_path):
                    backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                    try:
                        shutil.copy(file_path, backup_path)
                        print(f"Backed up {file_path} to {backup_path}")
                    except Exception as e:
                        print(f"Error backing up {file_path}: {e}")
                else:
                    print(f"File {file_path} does not exist, cannot back up.")


        def restore_files(self):
            for file_path in self.files_to_monitor:
                backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                if not os.path.exists(file_path) and os.path.exists(backup_path):
                    # Ensure the target directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    try:
                        shutil.copy(backup_path, file_path)
                        print(f"Restored {file_path} from {backup_path}")
                    except Exception as e:
                        print(f"Error restoring {file_path}: {e}")
                else:
                    print(f"Could not restore {file_path}; either it already exists or no backup found.")


        def initial_restore(self):
            for file_path in self.files_to_monitor:
                if not os.path.exists(file_path):
                    backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                    if os.path.exists(backup_path):
                        # Ensure the target directory exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        try:
                            shutil.copy(backup_path, file_path)
                            print(f"Initial restore: {file_path} restored from {backup_path}")
                        except Exception as e:
                            print(f"Error during initial restore of {file_path}: {e}")
                    else:
                        print(f"Backup for {file_path} not found for initial restore.")




def start_monitoring_thread(monitor):
    monitor.start_monitoring()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.observer.stop()
    monitor.observer.join()









# check for more than one instances, and terminate them so no new window will be opened to access the app
# A mutex (short for "mutual exclusion") is a synchronization primitive that ensures only one instance of a program can run at a time.

class SingleInstance:
    def __init__(self):
        self.lock_file = "/tmp/fadcrypt.lock"
        self.lock_fd = None

    def create_mutex(self):
        """Create a file-based lock to ensure only one instance is running."""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.lockf(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
        except (IOError, OSError):
            print("Another instance is already running. Exiting...")
            sys.exit(1)

    def release_mutex(self):
        """Release the lock by closing and removing the lock file."""
        try:
            if self.lock_fd:
                self.lock_fd.close()
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except OSError as e:
            print(f"Error removing lock file: {e}")



def main():
    # Step 1: Create a SingleInstance object and check for existing instance
    single_instance = SingleInstance()
    single_instance.create_mutex()

    # Setup cleanup on exit
    def cleanup_on_exit():
        single_instance.release_mutex()

    atexit.register(cleanup_on_exit)

    # Setup signal handlers for proper cleanup
    def signal_handler(signum, frame):
        print("Received signal, cleaning up...")
        cleanup_on_exit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    root = TkinterDnD.Tk()
    style = Style(theme='darkly')  # Apply dark theme, pulse, cyborg, darkly, simplex(red)

    # Customize window borders (not directly supported in ttkbootstrap, but can be done with custom themes)
    style.configure('TNotebook.Tab',
                    background='#333333',  # Dark gray for tabs
                    foreground='#FFFFFF')  # White text for tabs
    
    style.configure('TButton', bordercolor="black", background="black")
    style.configure('red.TButton', bordercolor="#ED2939", background="#ED2939")
    style.configure('white.TButton', bordercolor="#ffffff", background="#ffffff")
    style.configure('green.TButton', bordercolor="#009E60", background="#009E60")
    style.configure('yellow.TButton', bordercolor="#DAA520", background="#DAA520")
    style.configure('blue.TButton', bordercolor="#004F98", background="#004F98")
    style.configure('navy.TButton', bordercolor="#4C516D", background="#4C516D")

    # Customize button color
    style.configure('TButton',
                    background='#333333',  # Dark gray color
                    foreground='#FFFFFF',  # White text
                    borderwidth=3,  # Border width
                    relief='solid',  # Solid border
                    highlightbackground='#222222',  # Darker border color
                    highlightthickness=0)  # Thickness of the border

    style.map('TButton',
            foreground=[('hover', '#D3D3D3')],  # gray text color on hover
            background=[('active', '#000000')])  # Black color on hover
    
    # Style the Checkbutton
    style.configure('TCheckbutton', foreground='#ffffff', padding=10)

    app = AppLockerGUI(root)
    # root.protocol("WM_DELETE_WINDOW", root.iconify)  # Minimize instead of close
    root.mainloop()

if __name__ == "__main__":
    monitor = FileMonitor()
    monitoring_thread = threading.Thread(target=start_monitoring_thread, args=(monitor,))
    monitoring_thread.daemon = True
    monitoring_thread.start()
    main()
