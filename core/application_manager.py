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
        self.apps_listbox = None
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
        if app_path in self.icon_cache:
            return self.icon_cache[app_path]
        
        try:
            icon_path = None
            
            # Try to get icon from .desktop file on Linux
            if self.is_linux:
                icon_path = self.find_desktop_icon(app_path)
            
            # If no icon found, try to find by app name
            if not icon_path or not os.path.exists(icon_path):
                app_name = os.path.basename(app_path).lower()
                # Try common icon locations
                icon_path = self.find_icon_by_name(app_name)
            
            # Load the icon if found
            if icon_path and os.path.exists(icon_path):
                # Handle SVG files
                if icon_path.endswith('.svg'):
                    # For SVG, we'll use a default icon or convert
                    # For now, try to find PNG version
                    png_path = icon_path.replace('.svg', '.png')
                    if os.path.exists(png_path):
                        icon_path = png_path
                    else:
                        # Try without extension
                        icon_path = self.find_icon_by_name(os.path.splitext(os.path.basename(icon_path))[0])
                
                if icon_path and icon_path.endswith(('.png', '.jpg', '.jpeg', '.xpm')):
                    image = Image.open(icon_path)
                    image = image.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.icon_cache[app_path] = photo
                    return photo
        except Exception as e:
            print(f"Error loading icon for {app_path}: {e}")
        
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
        """Create the Applications tab with all UI components"""
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="Applications")

        # Header frame with app count
        header_frame = ttk.Frame(self.apps_frame)
        header_frame.pack(pady=(5, 0), padx=5, fill=tk.X)

        self.app_count_label = ttk.Label(
            header_frame, 
            text="Applications: 0", 
            font=("TkDefaultFont", 10, "bold")
        )
        self.app_count_label.pack(side=tk.LEFT, padx=5)

        # Create a frame to hold the listbox and scrollbar
        list_frame = ttk.Frame(self.apps_frame)
        list_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Create the listbox with scrollbar (EXTENDED selectmode for multi-selection)
        self.apps_listbox = tk.Listbox(
            list_frame,
            width=50,
            font=("Helvetica", 10),
            selectmode=tk.EXTENDED,
            bg='#222222',
            fg='#ffffff',
            selectbackground='#555555',
            selectforeground='#009E60',
            activestyle='none',
            highlightcolor='#ED2939',
            highlightbackground='#444444',
            highlightthickness=1
        )
        self.apps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, 
            orient=tk.VERTICAL, 
            command=self.apps_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.apps_listbox.config(yscrollcommand=scrollbar.set)

        # Bind events
        self.apps_listbox.bind('<Double-Button-1>', self.on_double_click)
        self.apps_listbox.bind('<Delete>', lambda e: self.remove_applications())
        self.apps_listbox.bind('<Control-a>', lambda e: self.select_all_apps())
        self.apps_listbox.bind('<Button-3>', self.show_context_menu)  # Right-click

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
    
    def on_double_click(self, event):
        """Handle double-click on listbox item"""
        # Add small delay to ensure window is properly created
        self.master.after(100, self.edit_application)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under cursor
        index = self.apps_listbox.nearest(event.y)
        self.apps_listbox.selection_clear(0, tk.END)
        self.apps_listbox.selection_set(index)
        self.apps_listbox.activate(index)
        
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
        """Update the applications listbox with current apps"""
        self.apps_listbox.delete(0, tk.END)
        app_count = len(self.app_locker.config["applications"])
        
        for index, app in enumerate(self.app_locker.config["applications"]):
            # Get metadata
            meta = self.get_app_metadata(app['name'])
            unlock_count = meta.get('unlock_count', 0)
            
            # Format the display text with icon placeholder and stats
            item = f"  📦 {app['name']} → {app['path']}  [Unlocked: {unlock_count}×]"
            self.apps_listbox.insert(tk.END, item)
            
            # Apply alternating row colors for dark theme
            if index % 2 == 0:
                self.apps_listbox.itemconfig(index, {'bg': '#2a2a2a', 'fg': '#ffffff'})
            else:
                self.apps_listbox.itemconfig(index, {'bg': '#1f1f1f', 'fg': '#ffffff'})
        
        # Update app count label
        self.app_count_label.config(text=f"Applications: {app_count}")
        self.update_config_display()
    
    def remove_applications(self):
        """Remove selected applications with confirmation"""
        selections = self.apps_listbox.curselection()
        if not selections:
            self.show_message("Error", "Please select at least one application to remove.")
            return
        
        # Get all selected app names
        app_names = []
        for idx in selections:
            item_text = self.apps_listbox.get(idx)
            # Extract name from formatted text: "  📦 name → path  [Unlocked: X×]"
            name = item_text.split('📦')[1].split('→')[0].strip()
            app_names.append(name)
        
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
        selection = self.apps_listbox.curselection()
        if not selection:
            self.show_message("Error", "Please select an application to edit.")
            return
        
        if len(selection) > 1:
            self.show_message("Error", "Please select only one application to edit.")
            return
        
        # Get current app info
        item_text = self.apps_listbox.get(selection[0])
        old_name = item_text.split('📦')[1].split('→')[0].strip()
        old_path = item_text.split('→')[1].split('[')[0].strip()
        
        # Find the app in config
        app_index = None
        for idx, app in enumerate(self.app_locker.config["applications"]):
            if app["name"] == old_name:
                app_index = idx
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
        selection = self.apps_listbox.curselection()
        if not selection:
            self.show_message("Error", "Please select an application to view statistics.")
            return
        
        item_text = self.apps_listbox.get(selection[0])
        app_name = item_text.split('📦')[1].split('→')[0].strip()
        
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
        selection = self.apps_listbox.curselection()
        if not selection:
            return
        
        item_text = self.apps_listbox.get(selection[0])
        path = item_text.split('→')[1].split('[')[0].strip()
        
        self.master.clipboard_clear()
        self.master.clipboard_append(path)
        self.show_message("Copied", f"Path copied to clipboard:\n{path}")
    
    def open_file_location(self):
        """Open file manager at the application's location"""
        selection = self.apps_listbox.curselection()
        if not selection:
            return
        
        item_text = self.apps_listbox.get(selection[0])
        path = item_text.split('→')[1].split('[')[0].strip()
        
        directory = os.path.dirname(path)
        if os.path.exists(directory):
            if self.is_linux:
                os.system(f'xdg-open "{directory}" &')
            else:
                os.system(f'explorer "{directory}"')
        else:
            self.show_message("Error", f"Directory does not exist:\n{directory}")
    
    def select_all_apps(self):
        """Select all applications in the listbox"""
        self.apps_listbox.select_set(0, tk.END)
        return 'break'  # Prevent default Ctrl+A behavior
    
    def deselect_all_apps(self):
        """Deselect all applications in the listbox"""
        self.apps_listbox.selection_clear(0, tk.END)
