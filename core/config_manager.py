"""
Config Manager - Handles import/export of configuration files
This is shared between Windows and Linux versions
"""

import json
import os
import time
from tkinter import filedialog, messagebox


class ConfigManager:
    """
    Manages configuration import/export operations.
    This class provides unified functionality for both Windows and Linux versions.
    """
    
    def __init__(self, app_locker, get_fadcrypt_folder_func):
        """
        Initialize the ConfigManager
        
        Args:
            app_locker: The AppLocker instance that contains the config
            get_fadcrypt_folder_func: Function that returns the FadCrypt folder path
        """
        self.app_locker = app_locker
        self.get_fadcrypt_folder = get_fadcrypt_folder_func
    
    def export_config(self, show_message_func):
        """
        Export configuration to a JSON file
        
        Args:
            show_message_func: Function to show messages to user (title, message)
        
        Returns:
            bool: True if export successful, False otherwise
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="FadCrypt_config.json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.app_locker.config, f, indent=4)
                show_message_func("Success", f"Config exported successfully to {file_path}")
                return True
            except Exception as e:
                show_message_func("Error", f"Failed to export config: {e}")
                return False
        return False
    
    def import_config(self, show_message_func, update_display_func):
        """
        Import configuration from a JSON file
        
        Args:
            show_message_func: Function to show messages to user (title, message)
            update_display_func: Function to update the UI display after import
        
        Returns:
            bool: True if import successful, False otherwise
        """
        file_path = filedialog.askopenfilename(
            title="Select Config File to Import",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return False
        
        try:
            # Read the imported config
            with open(file_path, "r") as f:
                imported_config = json.load(f)
            
            # Validate the config structure
            if not isinstance(imported_config, dict) or "applications" not in imported_config:
                show_message_func("Error", "Invalid config file format. Missing 'applications' key.")
                return False
            
            # Ask for confirmation
            num_apps = len(imported_config.get("applications", []))
            response = messagebox.askyesno(
                "Confirm Import",
                f"This will import {num_apps} application(s).\n\n"
                "Current applications will be replaced.\n\n"
                "Do you want to continue?"
            )
            
            if not response:
                return False
            
            # Backup current config before importing
            backup_path = os.path.join(
                self.get_fadcrypt_folder(),
                'Backup',
                f'config_backup_{time.strftime("%Y%m%d_%H%M%S")}.json'
            )
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            try:
                with open(backup_path, 'w') as f:
                    json.dump(self.app_locker.config, f, indent=4)
                print(f"Backup created at: {backup_path}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
            
            # Import the config
            self.app_locker.config = imported_config
            self.app_locker.save_config()
            
            # Refresh the applications list display
            update_display_func()
            
            show_message_func(
                "Success",
                f"Config imported successfully!\n\n"
                f"Imported {num_apps} application(s).\n"
                f"Previous config backed up to:\n{os.path.basename(backup_path)}"
            )
            
            return True
            
        except json.JSONDecodeError:
            show_message_func("Error", "Invalid JSON file. Please select a valid config file.")
            return False
        except Exception as e:
            show_message_func("Error", f"Failed to import config: {e}")
            return False
