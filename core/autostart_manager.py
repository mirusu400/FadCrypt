"""
Autostart Manager - System Startup Configuration
Handles autostart configuration for Windows and Linux
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Optional


class AutostartManagerBase(ABC):
    """
    Abstract base class for autostart management.
    
    Platform-specific implementations should inherit from this class
    and implement the abstract methods.
    """
    
    def __init__(self, app_name: str = "FadCrypt", app_path: Optional[str] = None):
        """
        Initialize the autostart manager.
        
        Args:
            app_name: Name of the application
            app_path: Path to application executable (auto-detected if None)
        """
        self.app_name = app_name
        self.app_path = app_path or self._get_app_path()
    
    def _get_app_path(self) -> str:
        """
        Get the path to the current application executable.
        
        Returns:
            Absolute path to the application
        """
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(sys.argv[0])
    
    @abstractmethod
    def enable_autostart(self, with_monitoring: bool = True) -> bool:
        """
        Enable autostart on system boot.
        
        Args:
            with_monitoring: If True, start with --auto-monitor flag
            
        Returns:
            True if autostart enabled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def disable_autostart(self) -> bool:
        """
        Disable autostart on system boot.
        
        Returns:
            True if autostart disabled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def is_autostart_enabled(self) -> bool:
        """
        Check if autostart is currently enabled.
        
        Returns:
            True if autostart is enabled, False otherwise
        """
        pass


class AutostartManagerLinux(AutostartManagerBase):
    """
    Linux autostart implementation using .desktop files.
    
    Creates/removes .desktop file in ~/.config/autostart/
    """
    
    def __init__(self, app_name: str = "FadCrypt", app_path: Optional[str] = None):
        super().__init__(app_name, app_path)
        
        # Autostart directory
        config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        self.autostart_dir = os.path.join(config_home, 'autostart')
        self.desktop_file = os.path.join(self.autostart_dir, f'{app_name}.desktop')
    
    def enable_autostart(self, with_monitoring: bool = True) -> bool:
        """
        Enable autostart by creating .desktop file in ~/.config/autostart/
        
        Args:
            with_monitoring: If True, start with --auto-monitor flag
            
        Returns:
            True if autostart enabled successfully, False otherwise
        """
        try:
            # Create autostart directory if it doesn't exist
            os.makedirs(self.autostart_dir, exist_ok=True)
            
            # Build exec command
            exec_command = self.app_path
            if with_monitoring:
                exec_command += " --auto-monitor"
            
            # Create .desktop file content
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Comment=Application Locker with Password Protection
Exec={exec_command}
Icon=fadcrypt
Terminal=false
Categories=Security;Utility;
X-GNOME-Autostart-enabled=true
"""
            
            # Write .desktop file
            with open(self.desktop_file, 'w') as f:
                f.write(desktop_content)
            
            # Make executable
            os.chmod(self.desktop_file, 0o755)
            
            print(f"[AutostartManager] Autostart enabled: {self.desktop_file}")
            return True
            
        except Exception as e:
            print(f"[AutostartManager] Error enabling autostart: {e}")
            return False
    
    def disable_autostart(self) -> bool:
        """
        Disable autostart by removing .desktop file.
        
        Returns:
            True if autostart disabled successfully, False otherwise
        """
        try:
            if os.path.exists(self.desktop_file):
                os.remove(self.desktop_file)
                print(f"[AutostartManager] Autostart disabled: {self.desktop_file}")
            else:
                print("[AutostartManager] Autostart was not enabled")
            return True
            
        except Exception as e:
            print(f"[AutostartManager] Error disabling autostart: {e}")
            return False
    
    def is_autostart_enabled(self) -> bool:
        """
        Check if autostart is enabled by checking .desktop file existence.
        
        Returns:
            True if .desktop file exists, False otherwise
        """
        return os.path.exists(self.desktop_file)


class AutostartManagerWindows(AutostartManagerBase):
    """
    Windows autostart implementation using registry.
    
    Creates/removes registry key in HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    """
    
    def __init__(self, app_name: str = "FadCrypt", app_path: Optional[str] = None):
        super().__init__(app_name, app_path)
        
        try:
            import winreg
            self.winreg = winreg
            self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        except ImportError:
            print("[AutostartManager] Warning: winreg not available (not on Windows?)")
            self.winreg = None
    
    def enable_autostart(self, with_monitoring: bool = True) -> bool:
        """
        Enable autostart by creating registry key.
        
        Args:
            with_monitoring: If True, start with --auto-monitor flag
            
        Returns:
            True if autostart enabled successfully, False otherwise
        """
        if not self.winreg:
            print("[AutostartManager] winreg not available")
            return False
        
        try:
            # Build exec command
            exec_command = f'"{self.app_path}"'
            if with_monitoring:
                exec_command += " --auto-monitor"
            
            # Open registry key
            key = self.winreg.OpenKey(
                self.winreg.HKEY_CURRENT_USER,
                self.reg_path,
                0,
                self.winreg.KEY_SET_VALUE
            )
            
            # Set value
            self.winreg.SetValueEx(
                key,
                self.app_name,
                0,
                self.winreg.REG_SZ,
                exec_command
            )
            
            self.winreg.CloseKey(key)
            print(f"[AutostartManager] Autostart enabled in registry")
            return True
            
        except Exception as e:
            print(f"[AutostartManager] Error enabling autostart: {e}")
            return False
    
    def disable_autostart(self) -> bool:
        """
        Disable autostart by removing registry key.
        
        Returns:
            True if autostart disabled successfully, False otherwise
        """
        if not self.winreg:
            print("[AutostartManager] winreg not available")
            return False
        
        try:
            # Open registry key
            key = self.winreg.OpenKey(
                self.winreg.HKEY_CURRENT_USER,
                self.reg_path,
                0,
                self.winreg.KEY_SET_VALUE
            )
            
            # Delete value
            try:
                self.winreg.DeleteValue(key, self.app_name)
                print(f"[AutostartManager] Autostart disabled in registry")
            except FileNotFoundError:
                print("[AutostartManager] Autostart was not enabled")
            
            self.winreg.CloseKey(key)
            return True
            
        except Exception as e:
            print(f"[AutostartManager] Error disabling autostart: {e}")
            return False
    
    def is_autostart_enabled(self) -> bool:
        """
        Check if autostart is enabled by checking registry key.
        
        Returns:
            True if registry key exists, False otherwise
        """
        if not self.winreg:
            return False
        
        try:
            key = self.winreg.OpenKey(
                self.winreg.HKEY_CURRENT_USER,
                self.reg_path,
                0,
                self.winreg.KEY_READ
            )
            
            try:
                self.winreg.QueryValueEx(key, self.app_name)
                self.winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                self.winreg.CloseKey(key)
                return False
                
        except Exception as e:
            print(f"[AutostartManager] Error checking autostart: {e}")
            return False


# Factory function to get platform-specific manager
def get_autostart_manager(app_name: str = "FadCrypt", app_path: Optional[str] = None) -> AutostartManagerBase:
    """
    Get the appropriate autostart manager for the current platform.
    
    Args:
        app_name: Name of the application
        app_path: Path to application executable (auto-detected if None)
        
    Returns:
        Platform-specific AutostartManager instance
    """
    if sys.platform.startswith('linux'):
        return AutostartManagerLinux(app_name, app_path)
    elif sys.platform.startswith('win'):
        return AutostartManagerWindows(app_name, app_path)
    else:
        # Fallback to Linux implementation for other Unix-like systems
        print(f"[AutostartManager] Warning: Unsupported platform {sys.platform}, using Linux implementation")
        return AutostartManagerLinux(app_name, app_path)
