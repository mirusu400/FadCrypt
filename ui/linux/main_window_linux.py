"""Linux-specific Main Window for FadCrypt PyQt6 UI"""

import os
import subprocess
from PyQt6.QtWidgets import QMessageBox
from ui.base.main_window_base import MainWindowBase


class MainWindowLinux(MainWindowBase):
    """
    Linux-specific main window extending MainWindowBase.
    
    Handles Linux-specific functionality:
    - .desktop file autostart
    - Linux-specific paths (~/.config/autostart/)
    - ELF binary detection
    - fcntl locking for single-instance
    """
    
    def __init__(self, version=None):
        super().__init__(version)
        self.setup_linux_specifics()
    
    def setup_linux_specifics(self):
        """Initialize Linux-specific features"""
        # TODO: Set up Linux-specific initialization
        pass
    
    def setup_autostart_linux(self, enable=True):
        """
        Set up autostart for Linux using .desktop file.
        
        Args:
            enable: If True, create autostart entry. If False, remove it.
        """
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "fadcrypt.desktop")
        
        if enable:
            # Create autostart directory if it doesn't exist
            os.makedirs(autostart_dir, exist_ok=True)
            
            # Get the path to the executable
            import sys
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                exec_path = sys.executable
            else:
                # Running as script
                exec_path = os.path.abspath(sys.argv[0])
            
            # Create .desktop file content
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=FadCrypt
Comment=Application Locker and Monitor
Exec={exec_path} --auto-monitor
Icon=fadcrypt
Terminal=false
Categories=Utility;Security;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
            
            # Write .desktop file
            try:
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                
                # Make it executable
                os.chmod(desktop_file, 0o755)
                
                print(f"Autostart enabled: {desktop_file}")
                return True
            except Exception as e:
                print(f"Failed to create autostart entry: {e}")
                QMessageBox.warning(
                    self,
                    "Autostart Error",
                    f"Failed to enable autostart:\n{str(e)}"
                )
                return False
        else:
            # Remove autostart entry
            try:
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                    print(f"Autostart disabled: {desktop_file}")
                return True
            except Exception as e:
                print(f"Failed to remove autostart entry: {e}")
                QMessageBox.warning(
                    self,
                    "Autostart Error",
                    f"Failed to disable autostart:\n{str(e)}"
                )
                return False
    
    def is_autostart_enabled_linux(self):
        """
        Check if autostart is enabled on Linux.
        
        Returns:
            bool: True if autostart is enabled, False otherwise
        """
        desktop_file = os.path.expanduser("~/.config/autostart/fadcrypt.desktop")
        return os.path.exists(desktop_file)
    
    def open_terminal_linux(self):
        """Open a terminal on Linux (distribution-aware)"""
        terminals = [
            'gnome-terminal',
            'konsole',
            'xfce4-terminal',
            'xterm',
            'terminator',
            'tilix'
        ]
        
        for terminal in terminals:
            try:
                subprocess.Popen([terminal])
                print(f"Opened terminal: {terminal}")
                return True
            except FileNotFoundError:
                continue
        
        QMessageBox.warning(
            self,
            "Terminal Not Found",
            "Could not find a terminal emulator.\n"
            "Please install gnome-terminal, konsole, or xterm."
        )
        return False
    
    def open_system_monitor_linux(self):
        """Open system monitor on Linux (distribution-aware)"""
        monitors = [
            'gnome-system-monitor',
            'ksysguard',
            'xfce4-taskmanager',
            'mate-system-monitor',
            'htop',
            'top'
        ]
        
        for monitor in monitors:
            try:
                if monitor in ['htop', 'top']:
                    # These need a terminal
                    subprocess.Popen(['gnome-terminal', '--', monitor])
                else:
                    subprocess.Popen([monitor])
                print(f"Opened system monitor: {monitor}")
                return True
            except FileNotFoundError:
                continue
        
        QMessageBox.warning(
            self,
            "System Monitor Not Found",
            "Could not find a system monitor application.\n"
            "Please install gnome-system-monitor or ksysguard."
        )
        return False
    
    def get_fadcrypt_folder(self):
        """
        Get the FadCrypt configuration folder for Linux.
        
        Returns:
            str: Path to ~/.config/FadCrypt/
        """
        config_dir = os.path.expanduser("~/.config/FadCrypt")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_backup_folder(self):
        """
        Get the backup folder for Linux.
        
        Returns:
            str: Path to ~/.local/share/FadCrypt/Backup/
        """
        backup_dir = os.path.expanduser("~/.local/share/FadCrypt/Backup")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
