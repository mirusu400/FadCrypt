"""
Application Manager Module for FadCrypt

This module handles all application management functionality including:
- Adding, editing, and removing applications
- Multi-selection operations
- Statistics tracking (unlock counts, last accessed)
- Metadata (timestamps for added/modified)
- UI components for application list display
"""

import os
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Callable, Optional, Dict, List, Any
from PIL import Image, ImageTk


def format_timestamp(timestamp: float) -> str:
    """
    Format timestamp to readable format: '24th Aug 2025 2:24 PM'
    """
    dt = datetime.fromtimestamp(timestamp)
    
    # Get day with ordinal suffix
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    # Format: 24th Aug 2025 2:24 PM
    return dt.strftime(f"{day}{suffix} %b %Y %I:%M %p")


class ApplicationManager:
    """
    Manages application data, operations, and UI components for FadCrypt.
    Handles the applications tab, edit dialogs, statistics, and metadata.
    """
    
    def __init__(self, app_locker, master, notebook, resource_path_func, 
                 show_message_func, update_config_display_func, is_linux=True):
        """
        Initialize ApplicationManager
        
        Args:
            app_locker: The AppLocker instance with config
            master: Main Tk window
            notebook: ttk.Notebook to add the Applications tab to
            resource_path_func: Function to get resource paths
            show_message_func: Function to show messages
            update_config_display_func: Function to update config display
            is_linux: Whether running on Linux (affects executable detection)
        """
        self.app_locker = app_locker
        self.master = master
        self.notebook = notebook
        self.resource_path = resource_path_func
        self.show_message = show_message_func
        self.update_config_display = update_config_display_func
        self.is_linux = is_linux
        
        # UI components
        self.app_count_label = None
        self.apps_frame = None
        self.apps_container = None  # Scrollable container for grid
        self.apps_canvas = None  # Canvas for scrolling
        self.selected_apps = []  # Track selected application cards
        self.app_cards = []  # Store card widgets for selection
        self.selected_cards = set()  # Track selected cards
        self.app_count_label = None
        self.apps_frame = None
        
        # Icon cache
        self.icon_cache = {}
        
        # Callback for adding applications (set by parent GUI)
        self.add_application_callback = None
        
        # Initialize metadata storage
        self.metadata_file = os.path.join(
            os.path.dirname(self.app_locker.config_file),
            'app_metadata.json'
        )
        self.metadata = self.load_metadata()
        
        # Create the Applications tab
        self.create_applications_tab()
    
    def load_metadata(self) -> Dict:
        """Load application metadata (timestamps, stats) from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return {}
        return {}
    
    def save_metadata(self):
        """Save application metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=4)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def get_app_metadata(self, app_name: str) -> Dict:
        """Get metadata for a specific app, create if doesn't exist"""
        if app_name not in self.metadata:
            self.metadata[app_name] = {
                'added_timestamp': time.time(),
                'modified_timestamp': time.time(),
                'unlock_count': 0,
                'last_unlocked': None
            }
            self.save_metadata()
        return self.metadata[app_name]
    
    def increment_unlock_count(self, app_name: str):
        """Increment unlock count for an app"""
        meta = self.get_app_metadata(app_name)
        meta['unlock_count'] += 1
        meta['last_unlocked'] = time.time()
        self.save_metadata()
    
    def update_modified_timestamp(self, app_name: str):
        """Update the modified timestamp for an app"""
        meta = self.get_app_metadata(app_name)
        meta['modified_timestamp'] = time.time()
        self.save_metadata()
    
    def get_app_icon(self, app_path: str, size=(32, 32)) -> Optional[ImageTk.PhotoImage]:
        """
        Get icon for an application.
        Returns cached icon if available, otherwise tries to extract/load icon.
        """
        print(f"\n🔍 [ICON LOADING] Attempting to load icon for: {app_path}")
        
        if app_path in self.icon_cache:
            print(f"✅ [ICON CACHE] Found cached icon for: {app_path}")
            return self.icon_cache[app_path]
        
        try:
            icon_path = None
            
            # Try to get icon from .desktop file on Linux
            if self.is_linux:
                print(f"🐧 [LINUX] Searching for .desktop file...")
                icon_path = self.find_desktop_icon(app_path)
                if icon_path:
                    print(f"✅ [DESKTOP] Found icon from .desktop file: {icon_path}")
                else:
                    print(f"❌ [DESKTOP] No icon found in .desktop files")
            
            # If no icon found, try to find by app name
            if not icon_path or not os.path.exists(icon_path):
                app_name = os.path.basename(app_path).lower()
                print(f"🔎 [NAME SEARCH] Searching by app name: {app_name}")
                # Try common icon locations
                icon_path = self.find_icon_by_name(app_name)
                if icon_path:
                    print(f"✅ [NAME SEARCH] Found icon: {icon_path}")
                else:
                    print(f"❌ [NAME SEARCH] No icon found by name")
            
            # Load the icon if found
            if icon_path and os.path.exists(icon_path):
                print(f"📁 [FILE CHECK] Icon file exists: {icon_path}")
                # Handle SVG files
                if icon_path.endswith('.svg'):
                    print(f"🎨 [SVG] Found SVG file, looking for PNG alternative...")
                    # For SVG, we'll use a default icon or convert
                    # For now, try to find PNG version
                    png_path = icon_path.replace('.svg', '.png')
                    if os.path.exists(png_path):
                        icon_path = png_path
                        print(f"✅ [SVG->PNG] Using PNG version: {png_path}")
                    else:
                        # Try without extension
                        icon_path = self.find_icon_by_name(os.path.splitext(os.path.basename(icon_path))[0])
                        if icon_path:
                            print(f"✅ [SVG->PNG] Found alternative: {icon_path}")
                
                if icon_path and icon_path.endswith(('.png', '.jpg', '.jpeg', '.xpm')):
                    print(f"🖼️ [IMAGE LOAD] Loading image file: {icon_path}")
                    image = Image.open(icon_path)
                    image = image.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.icon_cache[app_path] = photo
                    print(f"✅ [SUCCESS] Icon loaded and cached successfully!")
                    return photo
                else:
                    print(f"⚠️ [FORMAT] Unsupported format or no valid path: {icon_path}")
            else:
                print(f"❌ [NOT FOUND] Icon path not found or doesn't exist")
        except Exception as e:
            print(f"❌ [ERROR] Error loading icon for {app_path}: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"❌ [FINAL] Returning None - no icon loaded for {app_path}")
        return None
    
    def find_icon_by_name(self, app_name: str) -> Optional[str]:
        """Find icon by application name in standard icon directories"""
        # Remove common suffixes
        app_name = app_name.replace('-browser', '').replace('.bin', '').replace('.exe', '')
        
        # Common icon directories and sizes
        icon_locations = [
            f'/usr/share/pixmaps/{app_name}.png',
            f'/usr/share/pixmaps/{app_name}.xpm',
            f'/usr/share/icons/hicolor/48x48/apps/{app_name}.png',
            f'/usr/share/icons/hicolor/32x32/apps/{app_name}.png',
            f'/usr/share/icons/hicolor/256x256/apps/{app_name}.png',
            f'/usr/share/icons/hicolor/scalable/apps/{app_name}.svg',
            f'/usr/share/app-install/icons/{app_name}.png',
        ]
        
        for path in icon_locations:
            if os.path.exists(path):
                return path
        
        # Try with capital first letter
        app_name_cap = app_name.capitalize()
        for path in icon_locations:
            cap_path = path.replace(app_name, app_name_cap)
            if os.path.exists(cap_path):
                return cap_path
        
        return None
    
    def find_desktop_icon(self, app_path: str) -> Optional[str]:
        """Find icon path from .desktop file on Linux"""
        try:
            # Common desktop file locations
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/local/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            app_name = os.path.basename(app_path)
            
            for desktop_dir in desktop_dirs:
                if not os.path.exists(desktop_dir):
                    continue
                
                for desktop_file in os.listdir(desktop_dir):
                    if not desktop_file.endswith('.desktop'):
                        continue
                    
                    desktop_path = os.path.join(desktop_dir, desktop_file)
                    try:
                        with open(desktop_path, 'r') as f:
                            content = f.read()
                            if app_name in content or app_path in content:
                                # Extract Icon= line
                                for line in content.split('\n'):
                                    if line.startswith('Icon='):
                                        icon_name = line.split('=', 1)[1].strip()
                                        # Try to find the actual icon file
                                        icon_path = self.find_icon_path(icon_name)
                                        if icon_path:
                                            return icon_path
                    except:
                        continue
        except Exception as e:
            print(f"Error finding desktop icon: {e}")
        return None
    
    def find_icon_path(self, icon_name: str) -> Optional[str]:
        """Find full path for an icon name"""
        # Common icon directories
        icon_dirs = [
            '/usr/share/icons/hicolor/48x48/apps',
            '/usr/share/icons/hicolor/32x32/apps',
            '/usr/share/pixmaps',
            '/usr/share/icons'
        ]
        
        # If already a full path
        if os.path.exists(icon_name):
            return icon_name
        
        # Search in icon directories
        for icon_dir in icon_dirs:
            if not os.path.exists(icon_dir):
                continue
            
            # Try various extensions
            for ext in ['.png', '.svg', '.xpm', '']:
                icon_path = os.path.join(icon_dir, icon_name + ext)
                if os.path.exists(icon_path):
                    return icon_path
        
        return None
    
    def create_applications_tab(self):
        """Create the Applications tab with grid-based UI components"""
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="Applications")

        # Header frame with app count
        header_frame = ttk.Frame(self.apps_frame)
        header_frame.pack(pady=(5, 0), padx=10, fill=tk.X)

        self.app_count_label = ttk.Label(
            header_frame, 
            text="Applications: 0", 
            font=("TkDefaultFont", 11, "bold")
        )
        self.app_count_label.pack(side=tk.LEFT, padx=5)

        # Create scrollable canvas for grid
        canvas_frame = ttk.Frame(self.apps_frame)
        canvas_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Canvas with scrollbar
        self.apps_canvas = tk.Canvas(
            canvas_frame,
            bg='#1e1e1e',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=self.apps_canvas.yview
        )
        
        self.apps_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.apps_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Container frame inside canvas for grid
        self.apps_container = ttk.Frame(self.apps_canvas)
        self.canvas_window = self.apps_canvas.create_window(
            (0, 0),
            window=self.apps_container,
            anchor='nw'
        )

        # Bind canvas resize
        self.apps_container.bind('<Configure>', self._on_frame_configure)
        self.apps_canvas.bind('<Configure>', self._on_canvas_configure)

        # Mouse wheel scrolling - only on canvas, not bind_all
        self.apps_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.apps_canvas.bind("<Button-4>", self._on_mousewheel)
        self.apps_canvas.bind("<Button-5>", self._on_mousewheel)

        self.update_apps_listbox()

        # Buttons frame
        button_frame = ttk.Frame(self.apps_frame)
        button_frame.pack(pady=10, padx=5, fill=tk.X)

        # Left side buttons (main actions)
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        ttk.Button(
            left_buttons, 
            text="➕ Add", 
            command=self.on_add_button_click, 
            style="green.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            left_buttons, 
            text="🗑️ Remove", 
            command=self.remove_applications, 
            style="red.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            left_buttons, 
            text="✏️ Edit", 
            command=self.edit_application
        ).pack(side=tk.LEFT, padx=5)

        # Right side buttons (selection actions)
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        # Create custom style for Select All button with white text
        style = ttk.Style()
        style.configure("SelectAll.TButton", foreground="white")

        ttk.Button(
            right_buttons, 
            text="Select All", 
            command=self.select_all_apps,
            style="SelectAll.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            right_buttons, 
            text="Deselect All", 
            command=self.deselect_all_apps
        ).pack(side=tk.LEFT, padx=5)
    
    def on_add_button_click(self):
        """Handle Add button click - calls callback if set"""
        if self.add_application_callback:
            self.add_application_callback()
        else:
            print("Add application callback not set")
    
    def scan_installed_applications(self):
        """Scan system for installed applications (cross-platform)"""
        apps = []
        
        if self.is_linux:
            # Scan .desktop files
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/local/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            for desktop_dir in desktop_dirs:
                if not os.path.exists(desktop_dir):
                    continue
                
                for filename in os.listdir(desktop_dir):
                    if not filename.endswith('.desktop'):
                        continue
                    
                    filepath = os.path.join(desktop_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            name = None
                            exec_path = None
                            icon = None
                            no_display = False
                            
                            for line in f:
                                line = line.strip()
                                if line.startswith('Name='):
                                    name = line.split('=', 1)[1]
                                elif line.startswith('Exec='):
                                    exec_line = line.split('=', 1)[1]
                                    # Extract executable path (remove %u, %f etc.)
                                    exec_parts = exec_line.split()
                                    if exec_parts:
                                        exec_path = exec_parts[0]
                                elif line.startswith('Icon='):
                                    icon = line.split('=', 1)[1]
                                elif line.startswith('NoDisplay=true'):
                                    no_display = True
                            
                            # Only add if has name, exec, not hidden, and not already in config
                            if name and exec_path and not no_display:
                                # Check if already added
                                already_added = any(
                                    app['name'] == name or app['path'] == exec_path
                                    for app in self.app_locker.config["applications"]
                                )
                                
                                if not already_added:
                                    apps.append({
                                        'name': name,
                                        'path': exec_path,
                                        'icon': icon,
                                        'desktop_file': filepath
                                    })
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
        else:
            # Windows: Scan common program directories
            program_dirs = [
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                os.path.expanduser(r"~\AppData\Local\Programs")
            ]
            
            for prog_dir in program_dirs:
                if not os.path.exists(prog_dir):
                    continue
                
                for root, dirs, files in os.walk(prog_dir):
                    for file in files:
                        if file.endswith('.exe'):
                            filepath = os.path.join(root, file)
                            name = os.path.splitext(file)[0]
                            
                            # Check if already added
                            already_added = any(
                                app['path'] == filepath
                                for app in self.app_locker.config["applications"]
                            )
                            
                            if not already_added:
                                apps.append({
                                    'name': name,
                                    'path': filepath,
                                    'icon': filepath  # Windows can extract icon from exe
                                })
        
        # Sort by name
        apps.sort(key=lambda x: x['name'].lower())
        return apps
    
    def show_app_scanner_dialog(self):
        """Show dialog with scanned applications for batch adding"""
        # Create loading dialog
        loading_dialog = tk.Toplevel(self.master)
        loading_dialog.title("Scanning Applications")
        loading_dialog.geometry("400x150")
        loading_dialog.transient(self.master)
        loading_dialog.grab_set()
        loading_dialog.resizable(False, False)
        
        # Center the loading dialog
        loading_dialog.update_idletasks()
        x = (loading_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (loading_dialog.winfo_screenheight() // 2) - (150 // 2)
        loading_dialog.geometry(f"400x150+{x}+{y}")
        
        # Loading content
        loading_frame = ttk.Frame(loading_dialog, padding=20)
        loading_frame.pack(fill=tk.BOTH, expand=True)
        
        loading_label = ttk.Label(loading_frame, text="🔍 Scanning system for applications...", 
                                 font=("Arial", 12, "bold"))
        loading_label.pack(pady=10)
        
        progress = ttk.Progressbar(loading_frame, mode='indeterminate', length=300)
        progress.pack(pady=10)
        progress.start(10)
        
        status_label = ttk.Label(loading_frame, text="This may take a few seconds...", 
                                font=("Arial", 9), foreground="gray")
        status_label.pack(pady=5)
        
        # Force update to show the loading dialog
        loading_dialog.update()
        
        # Scan for applications (this may take a few seconds)
        try:
            scanned_apps = self.scan_installed_applications()
            loading_dialog.destroy()
        except Exception as e:
            loading_dialog.destroy()
            self.show_message("Scan Error", f"Failed to scan applications: {str(e)}", "error")
            return
        
        if not scanned_apps:
            self.show_message("No Apps Found", "No new applications found to add.", "info")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.master)
        dialog.title(f"Scan Applications - Found {len(scanned_apps)} apps")
        dialog.attributes('-topmost', True)
        
        # Set size and position
        dialog_width = 800
        dialog_height = 600
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.resizable(True, True)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"📦 Found {len(scanned_apps)} Applications",
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Instructions
        inst_label = ttk.Label(
            main_frame,
            text="Select applications to add (Ctrl+Click for multiple, Shift+Click for range):",
            font=("TkDefaultFont", 10)
        )
        inst_label.pack(pady=(0, 5))
        
        # Create scrollable canvas for grid
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scan_canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', highlightthickness=0)
        scan_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=scan_canvas.yview)
        scan_canvas.configure(yscrollcommand=scan_scrollbar.set)
        
        scan_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scan_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scan_container = ttk.Frame(scan_canvas)
        canvas_window = scan_canvas.create_window((0, 0), window=scan_container, anchor='nw')
        
        # Track selected apps
        selected_scan_apps = []
        
        # Create grid of scanned app cards
        columns = 4
        for index, app in enumerate(scanned_apps):
            row = index // columns
            col = index % columns
            
            # Create mini card
            card = tk.Frame(
                scan_container,
                bg='#2a2a2a',
                relief=tk.RAISED,
                borderwidth=1,
                highlightthickness=2,
                highlightbackground='#444444'
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            card.app_data = app
            card.is_selected = False
            
            inner = tk.Frame(card, bg='#2a2a2a')
            inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
            
            # Icon (smaller)
            icon_photo = self.get_app_icon(app['path'])
            if icon_photo:
                try:
                    icon_path = self.find_desktop_icon(app['path'])
                    if icon_path and os.path.exists(icon_path):
                        img = Image.open(icon_path)
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        icon_label = tk.Label(inner, image=photo, bg='#2a2a2a')
                        icon_label.image = photo
                        icon_label.pack()
                except:
                    tk.Label(inner, text="📦", font=("TkDefaultFont", 16), bg='#2a2a2a').pack()
            else:
                tk.Label(inner, text="📦", font=("TkDefaultFont", 16), bg='#2a2a2a').pack()
            
            # Name
            name_label = tk.Label(
                inner,
                text=app['name'],
                font=("TkDefaultFont", 9),
                bg='#2a2a2a',
                fg='#ffffff',
                wraplength=120
            )
            name_label.pack(pady=(5, 0))
            
            # Click to select/deselect
            def make_click_handler(card_widget):
                def on_click(e):
                    if card_widget.is_selected:
                        card_widget.configure(highlightbackground='#444444')
                        card_widget.is_selected = False
                        if card_widget.app_data in selected_scan_apps:
                            selected_scan_apps.remove(card_widget.app_data)
                    else:
                        card_widget.configure(highlightbackground='#009E60', highlightthickness=3)
                        card_widget.is_selected = True
                        if card_widget.app_data not in selected_scan_apps:
                            selected_scan_apps.append(card_widget.app_data)
                    status_label.config(text=f"Selected: {len(selected_scan_apps)} apps")
                return on_click
            
            for widget in [card, inner, name_label]:
                widget.bind('<Button-1>', make_click_handler(card))
        
        # Configure grid
        for col in range(columns):
            scan_container.grid_columnconfigure(col, weight=1, minsize=150)
        
        # Bind canvas configure
        def on_scan_configure(e):
            scan_canvas.configure(scrollregion=scan_canvas.bbox("all"))
        scan_container.bind('<Configure>', on_scan_configure)
        
        def on_canvas_configure(e):
            scan_canvas.itemconfig(canvas_window, width=e.width)
        scan_canvas.bind('<Configure>', on_canvas_configure)
        
        # Status label
        status_label = ttk.Label(
            main_frame,
            text="Selected: 0 apps",
            font=("TkDefaultFont", 10, "bold")
        )
        status_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        def select_all():
            for widget in scan_container.winfo_children():
                if hasattr(widget, 'app_data') and not widget.is_selected:
                    widget.configure(highlightbackground='#009E60', highlightthickness=3)
                    widget.is_selected = True
                    if widget.app_data not in selected_scan_apps:
                        selected_scan_apps.append(widget.app_data)
            status_label.config(text=f"Selected: {len(selected_scan_apps)} apps")
        
        def deselect_all():
            for widget in scan_container.winfo_children():
                if hasattr(widget, 'app_data') and widget.is_selected:
                    widget.configure(highlightbackground='#444444', highlightthickness=2)
                    widget.is_selected = False
            selected_scan_apps.clear()
            status_label.config(text="Selected: 0 apps")
        
        def add_selected():
            if not selected_scan_apps:
                self.show_message("No Selection", "Please select at least one application to add.")
                return
            
            # Add all selected apps
            for app in selected_scan_apps:
                self.app_locker.add_application(app['name'], app['path'])
            
            dialog.destroy()
            self.update_apps_listbox()
            self.show_message("Success", f"Added {len(selected_scan_apps)} application(s) successfully!")
        
        ttk.Button(button_frame, text="Select All", command=select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=f"➕ Add Selected", command=add_selected, style="green.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        # Update scroll region
        self.apps_canvas.configure(scrollregion=self.apps_canvas.bbox("all"))
        
        # Check if scrolling is needed
        canvas_height = self.apps_canvas.winfo_height()
        content_height = self.apps_container.winfo_reqheight()
        
        # If content fits, reset scroll to top
        if content_height <= canvas_height:
            self.apps_canvas.yview_moveto(0)
    
    def _on_canvas_configure(self, event):
        """When canvas is resized, adjust the container width to match canvas"""
        canvas_width = event.width
        # Only set width, let height be determined by content
        self.apps_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling - only if content exceeds canvas"""
        canvas_height = self.apps_canvas.winfo_height()
        content_height = self.apps_container.winfo_reqheight()
        
        # Only scroll if content is larger than canvas
        if content_height > canvas_height:
            if event.num == 4 or event.delta > 0:
                self.apps_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.apps_canvas.yview_scroll(1, "units")
    
    def on_double_click(self, event):
        """Handle double-click on application card"""
        # Add small delay to ensure window is properly created
        self.master.after(100, self.edit_application)
    
    def show_context_menu(self, event):
        """Show context menu on right-click for grid cards"""
        if not self.selected_apps:
            return
        
        # Create context menu
        context_menu = tk.Menu(self.master, tearoff=0)
        context_menu.add_command(label="✏️ Edit", command=self.edit_application)
        context_menu.add_command(label="🗑️ Remove", command=self.remove_applications)
        context_menu.add_separator()
        context_menu.add_command(label="📊 View Statistics", command=self.show_statistics)
        context_menu.add_command(label="📋 Copy Path", command=self.copy_path)
        context_menu.add_separator()
        context_menu.add_command(label="📂 Open File Location", command=self.open_file_location)
        
        # Display menu at cursor position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def update_apps_listbox(self):
        """Update the applications grid with current apps"""
        print("\n=== UPDATE_APPS_GRID START ===")
        
        # Clear existing cards
        for widget in self.apps_container.winfo_children():
            widget.destroy()
        
        self.selected_apps = []
        app_count = len(self.app_locker.config["applications"])
        print(f"Total applications: {app_count}")
        
        if app_count == 0:
            # Show empty state
            empty_label = ttk.Label(
                self.apps_container,
                text="No applications added yet.\nClick '➕ Add' to get started!",
                font=("TkDefaultFont", 12),
                foreground='#888888',
                justify='center'
            )
            empty_label.pack(expand=True, pady=50)
        else:
            # Create grid of application cards
            columns = 3  # Number of cards per row
            
            for index, app in enumerate(self.app_locker.config["applications"]):
                print(f"\n  App {index + 1}: {app['name']}")
                print(f"    Path: {app['path']}")
                
                # Get metadata
                meta = self.get_app_metadata(app['name'])
                unlock_count = meta.get('unlock_count', 0)
                print(f"    Unlock count: {unlock_count}")
                
                # Calculate grid position
                row = index // columns
                col = index % columns
                
                # Create application card
                card = self.create_app_card(app, meta, index)
                card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Configure grid weights for responsiveness
            for col in range(columns):
                self.apps_container.grid_columnconfigure(col, weight=1, minsize=200)
        
        # Update app count label
        self.app_count_label.config(text=f"Applications: {app_count}")
        print(f"\n=== UPDATE_APPS_GRID END (Total: {app_count}) ===\n")
        self.update_config_display()
    
    def create_app_card(self, app, meta, index):
        """Create a single application card with icon, name, and stats"""
        # Main card frame with border
        card_frame = tk.Frame(
            self.apps_container,
            bg='#2a2a2a',
            relief=tk.RAISED,
            borderwidth=1,
            highlightthickness=2,
            highlightbackground='#444444'
        )
        
        # Store app data
        card_frame.app_name = app['name']
        card_frame.app_path = app['path']
        card_frame.app_index = index
        card_frame.is_selected = False
        
        # Inner padding frame
        inner_frame = tk.Frame(card_frame, bg='#2a2a2a')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Icon section
        icon_frame = tk.Frame(inner_frame, bg='#2a2a2a')
        icon_frame.pack(pady=(0, 10))
        
        # Try to get actual icon (returns PhotoImage or None)
        photo = self.get_app_icon(app['path'])
        if photo:
            print(f"    ✓ Icon found and loaded")
            try:
                # Resize the cached PhotoImage
                # Note: get_app_icon returns 48x48, we want 64x64
                # So we need to get the path and reload
                icon_path = self.find_desktop_icon(app['path'])
                if icon_path and os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    icon_label = tk.Label(icon_frame, image=photo, bg='#2a2a2a')
                    icon_label.image = photo  # Keep reference
                    icon_label.pack()
                else:
                    raise Exception("Could not find icon file")
            except Exception as e:
                print(f"    ✗ Error resizing icon: {e}")
                # Fallback to emoji
                icon_label = tk.Label(
                    icon_frame,
                    text="📦",
                    font=("TkDefaultFont", 32),
                    bg='#2a2a2a'
                )
                icon_label.pack()
        else:
            print(f"    ✗ No icon found, using emoji fallback")
            icon_label = tk.Label(
                icon_frame,
                text="📦",
                font=("TkDefaultFont", 32),
                bg='#2a2a2a'
            )
            icon_label.pack()
        
        # App name
        name_label = tk.Label(
            inner_frame,
            text=app['name'],
            font=("TkDefaultFont", 11, "bold"),
            bg='#2a2a2a',
            fg='#ffffff',
            wraplength=180
        )
        name_label.pack(pady=(0, 5))
        
        # Stats
        unlock_count = meta.get('unlock_count', 0)
        stats_label = tk.Label(
            inner_frame,
            text=f"🔓 {unlock_count}× unlocked",
            font=("TkDefaultFont", 9),
            bg='#2a2a2a',
            fg='#888888'
        )
        stats_label.pack()
        
        # Bind events for interaction
        def on_click(event):
            self.toggle_card_selection(card_frame)
        
        def on_double_click(event):
            self.edit_application_from_card(card_frame)
        
        def on_right_click(event):
            self.show_card_context_menu(event, card_frame)
        
        # Bind to all widgets in card
        for widget in [card_frame, inner_frame, icon_frame, icon_label, name_label, stats_label]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Double-Button-1>', on_double_click)
            widget.bind('<Button-3>', on_right_click)
        
        return card_frame
    
    def toggle_card_selection(self, card):
        """Toggle selection state of a card"""
        if card.is_selected:
            # Deselect
            card.configure(highlightbackground='#444444', highlightthickness=2)
            card.is_selected = False
            if card.app_name in self.selected_apps:
                self.selected_apps.remove(card.app_name)
        else:
            # Select
            card.configure(highlightbackground='#009E60', highlightthickness=3)
            card.is_selected = True
            if card.app_name not in self.selected_apps:
                self.selected_apps.append(card.app_name)
        
        print(f"Selected apps: {self.selected_apps}")
    
    def edit_application_from_card(self, card):
        """Edit application from card"""
        # Ensure only this card is selected
        self.selected_apps = [card.app_name]
        self.edit_application()
    
    def show_card_context_menu(self, event, card):
        """Show context menu for a card"""
        # Select this card if not already selected
        if not card.is_selected:
            self.toggle_card_selection(card)
        
        # Show context menu at cursor position
        self.show_context_menu(event)
    
    def remove_applications(self):
        """Remove selected applications with confirmation"""
        if not self.selected_apps:
            self.show_message("Error", "Please select at least one application to remove.")
            return
        
        app_names = self.selected_apps.copy()
        count = len(app_names)
        
        # Show confirmation dialog
        if count == 1:
            message = f"Are you sure you want to remove '{app_names[0]}'?"
        else:
            message = f"Are you sure you want to remove {count} applications?\n\n" + "\n".join(f"• {name}" for name in app_names[:5])
            if count > 5:
                message += f"\n... and {count - 5} more"
        
        response = messagebox.askyesno("Confirm Removal", message, icon='warning')
        if not response:
            return
        
        # Remove all selected applications
        for app_name in app_names:
            self.app_locker.remove_application(app_name)
            # Remove metadata
            if app_name in self.metadata:
                del self.metadata[app_name]
        
        self.save_metadata()
        self.update_apps_listbox()
        
        if count == 1:
            self.show_message("Success", f"Application '{app_names[0]}' removed successfully.")
        else:
            self.show_message("Success", f"{count} applications removed successfully.")
    
    def edit_application(self):
        """Edit both name and path of selected application"""
        if not self.selected_apps:
            self.show_message("Error", "Please select an application to edit.")
            return
        
        if len(self.selected_apps) > 1:
            self.show_message("Error", "Please select only one application to edit.")
            return
        
        # Get the selected app name
        old_name = self.selected_apps[0]
        
        # Find the app in config
        app_index = None
        old_path = None
        for idx, app in enumerate(self.app_locker.config["applications"]):
            if app["name"] == old_name:
                app_index = idx
                old_path = app["path"]
                break
        
        if app_index is None:
            self.show_message("Error", "Application not found in configuration.")
            return
        
        # Create edit dialog
        self.edit_application_dialog(old_name, old_path, app_index)
    
    def edit_application_dialog(self, old_name, old_path, app_index):
        """Show dialog to edit application name and path"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Application")
        dialog.attributes('-topmost', True)
        
        # Wait for dialog to be created and visible
        dialog.update_idletasks()
        
        # Center the dialog
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - 250
        y = (screen_height // 2) - 125
        dialog.geometry(f"550x300+{x}+{y}")
        
        # Now grab after dialog is visible
        dialog.after(50, dialog.grab_set)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Edit Application", 
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Name field
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Name:", width=10).pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, width=50)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        name_entry.insert(0, old_name)
        
        # Path field
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Path:", width=10).pack(side=tk.LEFT)
        
        # Entry and browse button container
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        path_entry = ttk.Entry(path_input_frame)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        path_entry.insert(0, old_path)
        
        # Browse button
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Application",
                initialdir="/usr/bin" if old_path.startswith("/usr/bin") else os.path.dirname(old_path)
            )
            if file_path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, file_path)
        
        ttk.Button(path_input_frame, text="Browse", command=browse_file).pack(side=tk.LEFT, padx=(5, 0))
        
        # Metadata info
        meta = self.get_app_metadata(old_name)
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        added_time = format_timestamp(meta['added_timestamp'])
        modified_time = format_timestamp(meta['modified_timestamp'])
        unlock_count = meta.get('unlock_count', 0)
        
        info_text = f"Added: {added_time}  |  Modified: {modified_time}  |  Unlocked: {unlock_count} times"
        ttk.Label(info_frame, text=info_text, foreground='#888888', font=("TkDefaultFont", 9)).pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def save_changes():
            new_name = name_entry.get().strip()
            new_path = path_entry.get().strip()
            
            if not new_name or not new_path:
                self.show_message("Error", "Both name and path are required.")
                return
            
            if not os.path.exists(new_path):
                self.show_message("Error", f"Path does not exist: {new_path}")
                return
            
            # Check if name already exists (excluding current app)
            for idx, app in enumerate(self.app_locker.config["applications"]):
                if idx != app_index and app["name"] == new_name:
                    self.show_message("Error", f"An application with name '{new_name}' already exists.")
                    return
            
            # Update the application
            self.app_locker.config["applications"][app_index]["name"] = new_name
            self.app_locker.config["applications"][app_index]["path"] = new_path
            
            # Update metadata
            if old_name != new_name and old_name in self.metadata:
                # Rename metadata entry
                self.metadata[new_name] = self.metadata.pop(old_name)
            
            self.update_modified_timestamp(new_name)
            
            self.update_apps_listbox()
            self.show_message("Success", f"Application updated successfully!")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(
            button_frame, 
            text="💾 Save", 
            command=save_changes, 
            style="green.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="❌ Cancel", 
            command=cancel, 
            style="red.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
        name_entry.select_range(0, tk.END)
    
    def show_statistics(self):
        """Show detailed statistics for selected application"""
        if not self.selected_apps:
            self.show_message("Error", "Please select an application to view statistics.")
            return
        
        app_name = self.selected_apps[0]
        meta = self.get_app_metadata(app_name)
        
        # Format statistics
        added_time = format_timestamp(meta['added_timestamp'])
        modified_time = format_timestamp(meta['modified_timestamp'])
        unlock_count = meta.get('unlock_count', 0)
        last_unlocked = meta.get('last_unlocked')
        last_unlocked_str = format_timestamp(last_unlocked) if last_unlocked else "Never"
        
        stats_message = f"""Statistics for: {app_name}

📅 Added: {added_time}
✏️ Last Modified: {modified_time}
🔓 Total Unlocks: {unlock_count}
⏰ Last Unlocked: {last_unlocked_str}"""
        
        self.show_message("Application Statistics", stats_message)
    
    def copy_path(self):
        """Copy selected application path to clipboard"""
        if not self.selected_apps:
            return
        
        app_name = self.selected_apps[0]
        
        # Find path in config
        path = None
        for app in self.app_locker.config["applications"]:
            if app["name"] == app_name:
                path = app["path"]
                break
        
        if path:
            self.master.clipboard_clear()
            self.master.clipboard_append(path)
            self.show_message("Copied", f"Path copied to clipboard:\n{path}")
    
    def open_file_location(self):
        """Open file manager at the application's location"""
        if not self.selected_apps:
            return
        
        app_name = self.selected_apps[0]
        
        # Find path in config
        path = None
        for app in self.app_locker.config["applications"]:
            if app["name"] == app_name:
                path = app["path"]
                break
        
        if path:
            directory = os.path.dirname(path)
            if os.path.exists(directory):
                if self.is_linux:
                    os.system(f'xdg-open "{directory}" &')
                else:
                    os.system(f'explorer "{directory}"')
            else:
                self.show_message("Error", f"Directory does not exist:\n{directory}")
    
    def select_all_apps(self):
        """Select all application cards"""
        for widget in self.apps_container.winfo_children():
            if hasattr(widget, 'app_name') and not widget.is_selected:
                self.toggle_card_selection(widget)
        return 'break'  # Prevent default Ctrl+A behavior
    
    def deselect_all_apps(self):
        """Deselect all application cards"""
        for widget in self.apps_container.winfo_children():
            if hasattr(widget, 'app_name') and widget.is_selected:
                self.toggle_card_selection(widget)

