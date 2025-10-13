"""Windows-specific Main Window for FadCrypt PyQt6 UI"""

import os
import sys
import subprocess
import ctypes
from PyQt6.QtWidgets import QMessageBox

try:
    import winreg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from ui.base.main_window_base import MainWindowBase


class MainWindowWindows(MainWindowBase):
    """
    Windows-specific main window extending MainWindowBase.
    
    Handles Windows-specific functionality:
    - Registry autostart
    - Windows-specific paths (AppData, ProgramData)
    - .exe detection
    - Windows mutex for single-instance
    """
    
    def __init__(self, version=None):
        super().__init__(version)
        self.setup_windows_specifics()
    
    def setup_windows_specifics(self):
        """Initialize Windows-specific features"""
        if not WINDOWS_AVAILABLE:
            print("Warning: Running on non-Windows system, Windows features disabled")
        # Check if autostart is currently enabled and update settings UI
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.update_autostart_ui)
    
    def update_autostart_ui(self):
        """Update autostart checkbox based on current state"""
        is_enabled = self.is_autostart_enabled_windows()
        if hasattr(self, 'settings_panel'):
            self.settings_panel.autostart_checkbox.setChecked(is_enabled)
    
    def handle_autostart_setting(self, enable):
        """
        Handle autostart setting change for Windows.
        
        Args:
            enable: True to enable autostart, False to disable
        """
        self.setup_autostart_windows(enable)
    
    def setup_autostart_windows(self, enable=True):
        """
        Set up autostart for Windows using Registry.
        
        Args:
            enable: If True, create autostart entry. If False, remove it.
        """
        if not WINDOWS_AVAILABLE:
            QMessageBox.warning(
                self,
                "Platform Error",
                "Windows autostart is not available on this platform."
            )
            return False
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "FadCrypt"
        
        try:
            # Get the path to the executable
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                exec_path = sys.executable
            else:
                # Running as script - use pythonw to avoid console
                exec_path = f'pythonw "{os.path.abspath(sys.argv[0])}"'
            
            # Add --auto-monitor flag
            exec_command = f'"{exec_path}" --auto-monitor'
            
            if enable:
                # Open registry key
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )
                
                # Set the value
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, exec_command)
                winreg.CloseKey(key)
                
                print(f"Autostart enabled: {exec_command}")
                return True
            else:
                # Remove the value
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        key_path,
                        0,
                        winreg.KEY_WRITE
                    )
                    winreg.DeleteValue(key, value_name)
                    winreg.CloseKey(key)
                    print("Autostart disabled")
                    return True
                except FileNotFoundError:
                    # Value doesn't exist, already disabled
                    return True
        
        except Exception as e:
            print(f"Failed to modify autostart: {e}")
            QMessageBox.warning(
                self,
                "Autostart Error",
                f"Failed to {'enable' if enable else 'disable'} autostart:\n{str(e)}"
            )
            return False
    
    def is_autostart_enabled_windows(self):
        """
        Check if autostart is enabled on Windows.
        
        Returns:
            bool: True if autostart is enabled, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            return False
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "FadCrypt"
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking autostart: {e}")
            return False
    
    def open_terminal_windows(self):
        """Open a terminal on Windows"""
        try:
            # Try PowerShell first (modern Windows)
            subprocess.Popen(['powershell.exe'])
            print("Opened PowerShell")
            return True
        except Exception:
            try:
                # Fall back to cmd.exe
                subprocess.Popen(['cmd.exe'])
                print("Opened CMD")
                return True
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Terminal Error",
                    f"Failed to open terminal:\n{str(e)}"
                )
                return False
    
    def open_system_monitor_windows(self):
        """Open Task Manager on Windows"""
        try:
            subprocess.Popen(['taskmgr.exe'])
            print("Opened Task Manager")
            return True
        except Exception as e:
            QMessageBox.warning(
                self,
                "Task Manager Error",
                f"Failed to open Task Manager:\n{str(e)}"
            )
            return False
    
    def get_fadcrypt_folder(self):
        """
        Get the FadCrypt configuration folder for Windows.
        
        Returns:
            str: Path to %APPDATA%\\FadCrypt\\
        """
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(appdata, 'FadCrypt')
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_backup_folder(self):
        """
        Get the backup folder for Windows.
        
        Returns:
            str: Path to C:\\ProgramData\\FadCrypt\\Backup\\
        """
        programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
        backup_dir = os.path.join(programdata, 'FadCrypt', 'Backup')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def disable_system_tools(self):
        """
        Disable Command Prompt, Task Manager, Control Panel, and Registry Editor.
        This is called when "Disable Main loopholes" is enabled before monitoring starts.
        Note: Does NOT disable PowerShell as it's harder to detect and manage.
        """
        if not WINDOWS_AVAILABLE:
            print("Warning: Windows registry tools not available on this platform")
            return False
        
        try:
            # Check for admin privileges
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Warning: Administrative privileges required to disable system tools.")
                QMessageBox.warning(
                    self,
                    "Admin Required",
                    "Administrator privileges are required to disable system tools.\n"
                    "Please run FadCrypt as Administrator."
                )
                return False

            # Registry keys to modify
            keys_to_modify = [
                (r'Software\Policies\Microsoft\Windows\System', 'DisableCMD'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools')
            ]

            for reg_path, value_name in keys_to_modify:
                try:
                    # Create/open the registry key
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    # Set the value to disable
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                    print(f"✓ {value_name} disabled successfully")
                except Exception as e:
                    print(f"✗ Error disabling {value_name}: {e}")

            print("System tools disabled successfully")
            return True

        except Exception as e:
            print(f"Failed to disable system tools: {e}")
            return False
    
    def enable_system_tools(self):
        """
        Re-enable Command Prompt, Task Manager, Control Panel, and Registry Editor.
        This is called when monitoring stops or during cleanup.
        """
        if not WINDOWS_AVAILABLE:
            print("Warning: Windows registry tools not available on this platform")
            return False
        
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Warning: Administrative privileges required to enable system tools.")
                QMessageBox.warning(
                    self,
                    "Admin Required",
                    "Administrator privileges are required to enable system tools.\n"
                    "Please run FadCrypt as Administrator."
                )
                return False

            keys_to_modify = [
                (r'Software\Policies\Microsoft\Windows\System', 'DisableCMD'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableTaskMgr'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', 'NoControlPanel'),
                (r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 'DisableRegistryTools')
            ]

            for reg_path, value_name in keys_to_modify:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
                    try:
                        winreg.DeleteValue(key, value_name)
                        print(f"✓ {value_name} enabled successfully")
                    except FileNotFoundError:
                        print(f"ℹ {value_name} was not disabled (already enabled)")
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    print(f"ℹ Registry key for {value_name} doesn't exist (already enabled)")
                except Exception as e:
                    print(f"✗ Error enabling {value_name}: {e}")

            print("System tools enabled successfully")
            return True

        except Exception as e:
            print(f"Failed to enable system tools: {e}")
            return False

