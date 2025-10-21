"""
File Protection Manager
Protects critical files (recovery codes, config) from deletion/modification when monitoring is active.

Platform-specific implementations:
- Windows: SetFileAttributesW (HIDDEN + SYSTEM + READONLY)
- Linux: chattr +i (immutable flag) or restrictive permissions
"""

import os
import sys
import stat
from typing import List, Tuple, Optional

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

if IS_WINDOWS:
    try:
        import ctypes
        from ctypes import windll, wintypes
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        print("[FileProtection] ⚠️  Windows ctypes not available")
else:
    WINDOWS_AVAILABLE = False


class FileProtectionManager:
    """
    Manages file protection to prevent tampering with critical files during monitoring.
    
    Protection Methods:
    - Windows: Hidden + System + ReadOnly attributes via SetFileAttributesW
    - Linux: Immutable flag via chattr +i (requires sudo) or restrictive permissions
    
    Files Protected:
    - recovery_codes.json
    - encrypted_password.bin
    - fadcrypt_config.json (optional)
    """
    
    # Windows file attribute constants
    FILE_ATTRIBUTE_READONLY = 0x00000001
    FILE_ATTRIBUTE_HIDDEN = 0x00000002
    FILE_ATTRIBUTE_SYSTEM = 0x00000004
    FILE_ATTRIBUTE_NORMAL = 0x00000080
    
    def __init__(self):
        """Initialize file protection manager"""
        self.protected_files: List[str] = []
        self.original_attributes: dict = {}  # Store original attributes for restoration
        self.file_locks: dict = {}  # Store open file descriptors for locking (Linux)
        
        print(f"[FileProtection] Initialized on {sys.platform}")
        print(f"[FileProtection] Windows mode: {IS_WINDOWS}")
        print(f"[FileProtection] Linux mode: {IS_LINUX}")
    
    def protect_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Protect a file from deletion/modification.
        
        Args:
            file_path: Full path to file to protect
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        try:
            # Store original attributes
            self._store_original_attributes(file_path)
            
            if IS_WINDOWS:
                return self._protect_file_windows(file_path)
            elif IS_LINUX:
                return self._protect_file_linux(file_path)
            else:
                return False, f"Unsupported platform: {sys.platform}"
                
        except Exception as e:
            return False, f"Exception protecting file: {e}"
    
    def unprotect_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove protection from a file.
        
        Args:
            file_path: Full path to file to unprotect
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        try:
            if IS_WINDOWS:
                return self._unprotect_file_windows(file_path)
            elif IS_LINUX:
                return self._unprotect_file_linux(file_path)
            else:
                return False, f"Unsupported platform: {sys.platform}"
                
        except Exception as e:
            return False, f"Exception unprotecting file: {e}"
    
    def protect_multiple_files(self, file_paths: List[str]) -> Tuple[int, List[str]]:
        """
        Protect multiple files at once.
        
        On Linux: Uses elevated daemon for batch chattr +i operations (seamless, no prompts).
        On Windows: Protects each file individually.
        
        Args:
            file_paths: List of file paths to protect
            
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        # Filter existing files
        existing_files = [f for f in file_paths if os.path.exists(f)]
        
        if not existing_files:
            return 0, ["No files found to protect"]
        
        # Store original attributes for all files
        for file_path in existing_files:
            self._store_original_attributes(file_path)
        
        # Linux: Use batch protection via elevated daemon
        if IS_LINUX:
            return self._protect_multiple_files_linux_batch(existing_files)
        
        # Windows: Protect all files quickly (no UAC needed for attributes)
        success_count = 0
        errors = []
        
        print(f"[FileProtection] Protecting {len(existing_files)} files...")
        
        for file_path in existing_files:
            success, error = self.protect_file(file_path)
            if success:
                success_count += 1
                self.protected_files.append(file_path)
                print(f"[FileProtection] ✅ Protected: {os.path.basename(file_path)}")
            else:
                errors.append(f"{os.path.basename(file_path)}: {error}")
                print(f"[FileProtection] ❌ Failed to protect: {os.path.basename(file_path)} - {error}")
        
        if success_count > 0:
            print(f"[FileProtection] 🔒 {success_count} files protected (HIDDEN + SYSTEM + READONLY)")
        
        return success_count, errors
    
    def unprotect_all_files(self) -> Tuple[int, List[str]]:
        """
        Remove protection from all previously protected files.
        
        On Linux: Uses elevated daemon for batch chattr -i operations (seamless, no prompts).
        On Windows: Unprotects each file individually.
        
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        if not self.protected_files:
            return 0, []
        
        success_count = 0
        errors = []
        
        # Linux: Use batch unprotection via daemon
        if IS_LINUX and len(self.protected_files) > 1:
            batch_success = self._try_batch_chattr_with_daemon(self.protected_files, set_immutable=False)
            
            if batch_success:
                # Verify and remove from protected list
                for file_path in self.protected_files[:]:
                    filename = os.path.basename(file_path)
                    if not self._verify_immutable_flag(file_path):
                        success_count += 1
                        self.protected_files.remove(file_path)
                        print(f"[FileProtection] ✅ Unprotected: {filename}")
                        
                        # Restore permissions
                        try:
                            if file_path in self.original_attributes:
                                mode = self.original_attributes[file_path]
                                del self.original_attributes[file_path]
                            else:
                                mode = stat.S_IRUSR | stat.S_IWUSR  # 600
                            os.chmod(file_path, mode)
                        except Exception as e:
                            print(f"[FileProtection] ⚠️  chmod failed for {filename}: {e}")
                    else:
                        errors.append(f"{filename}: Still immutable")
                
                print(f"[FileProtection] 🔓 Batch unprotected {success_count} files")
                return success_count, errors
        
        # Fallback or Windows: Unprotect each file individually
        for file_path in self.protected_files[:]:
            success, error = self.unprotect_file(file_path)
            if success:
                success_count += 1
                self.protected_files.remove(file_path)
                print(f"[FileProtection] ✅ Unprotected: {os.path.basename(file_path)}")
            else:
                errors.append(f"{os.path.basename(file_path)}: {error}")
                print(f"[FileProtection] ❌ Failed to unprotect: {os.path.basename(file_path)} - {error}")
        
        return success_count, errors
    
    def _store_original_attributes(self, file_path: str):
        """Store original file attributes for restoration"""
        try:
            if IS_WINDOWS and WINDOWS_AVAILABLE:
                attrs = windll.kernel32.GetFileAttributesW(file_path)
                self.original_attributes[file_path] = attrs
            elif IS_LINUX:
                st = os.stat(file_path)
                self.original_attributes[file_path] = st.st_mode
        except Exception as e:
            print(f"[FileProtection] ⚠️  Could not store original attributes: {e}")
    
    # ========== WINDOWS IMPLEMENTATION ==========
    
    def _protect_file_windows(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Protect file on Windows using elevated service or direct SetFileAttributesW.
        
        Sets attributes: HIDDEN + SYSTEM + READONLY
        This makes the file harder to delete and hidden from normal view.
        
        Tries service first (seamless, no UAC), falls back to direct API.
        """
        # Try elevated service first (seamless, no UAC prompt)
        try:
            from core.windows.elevated_service_client import get_windows_elevated_client
            client = get_windows_elevated_client()
            if client.is_available():
                success, msg = client.protect_files([file_path])
                if success:
                    print(f"[FileProtection] Service: Protected {os.path.basename(file_path)} (no UAC!)")
                    return True, None
                else:
                    print(f"[FileProtection] Service protect failed: {msg}, trying direct method...")
        except Exception as e:
            logger.debug(f"Service not available: {e}")
        
        # Fallback: Direct SetFileAttributesW
        if not WINDOWS_AVAILABLE:
            return False, "Windows ctypes not available"
        
        try:
            # Combine attributes: Hidden + System + ReadOnly
            attributes = (
                self.FILE_ATTRIBUTE_HIDDEN |
                self.FILE_ATTRIBUTE_SYSTEM |
                self.FILE_ATTRIBUTE_READONLY
            )
            
            # Set file attributes
            result = windll.kernel32.SetFileAttributesW(file_path, attributes)
            
            if result == 0:
                error_code = windll.kernel32.GetLastError()
                return False, f"SetFileAttributesW failed with error code: {error_code}"
            
            print(f"[FileProtection] Windows: Set HIDDEN + SYSTEM + READONLY on {os.path.basename(file_path)}")
            return True, None
            
        except Exception as e:
            return False, f"Windows protection failed: {e}"
    
    def _unprotect_file_windows(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove protection from file on Windows.
        
        Tries elevated service first (seamless, no UAC), falls back to direct API.
        Restores original attributes or sets to NORMAL.
        """
        # Try elevated service first (seamless, no UAC prompt)
        try:
            from core.windows.elevated_service_client import get_windows_elevated_client
            client = get_windows_elevated_client()
            if client.is_available():
                success, msg = client.unprotect_files([file_path])
                if success:
                    print(f"[FileProtection] Service: Unprotected {os.path.basename(file_path)} (no UAC!)")
                    return True, None
                else:
                    print(f"[FileProtection] Service unprotect failed: {msg}, trying direct method...")
        except Exception as e:
            logger.debug(f"Service not available: {e}")
        
        # Fallback: Direct SetFileAttributesW
        if not WINDOWS_AVAILABLE:
            return False, "Windows ctypes not available"
        
        try:
            # Restore original attributes if available, otherwise set to NORMAL
            if file_path in self.original_attributes:
                attributes = self.original_attributes[file_path]
                del self.original_attributes[file_path]
            else:
                attributes = self.FILE_ATTRIBUTE_NORMAL
            
            # Set file attributes
            result = windll.kernel32.SetFileAttributesW(file_path, attributes)
            
            if result == 0:
                error_code = windll.kernel32.GetLastError()
                return False, f"SetFileAttributesW failed with error code: {error_code}"
            
            print(f"[FileProtection] Windows: Restored attributes on {os.path.basename(file_path)}")
            return True, None
            
        except Exception as e:
            return False, f"Windows unprotection failed: {e}"
    
    # ========== LINUX IMPLEMENTATION ==========
    
    def _protect_file_linux(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Protect file on Linux using immutable flag (chattr +i).
        
        DAEMON-ONLY APPROACH: Uses elevated daemon running at boot.
        No user prompts needed - daemon has persistent root permissions.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        filename = os.path.basename(file_path)
        
        # Use daemon (persistent root elevation at boot time)
        print(f"[FileProtection] 🔒 Protecting {filename} via daemon...")
        success, error = self._try_chattr_with_daemon([file_path], set_immutable=True)
        
        if success:
            print(f"[FileProtection] ✅ IMMUTABLE: {filename}")
            print(f"[FileProtection] 🔒 File CANNOT be deleted, even by root")
            return True, None
        else:
            # Hard fail if daemon unavailable
            error_msg = f"❌ Daemon elevation failed: {error}"
            print(f"[FileProtection] {error_msg}")
            return False, error_msg
    
    def _unprotect_file_linux(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove protection from file on Linux.
        
        DAEMON-ONLY APPROACH: Uses elevated daemon (no user prompts).
        Daemon has persistent root permissions from boot.
        """
        filename = os.path.basename(file_path)
        
        # Use daemon (seamless, no prompts)
        print(f"[FileProtection] 🔓 Unprotecting {filename} via daemon...")
        success, error = self._try_chattr_with_daemon([file_path], set_immutable=False)
        
        if not success:
            error_msg = f"❌ Daemon unprotection failed: {error}"
            print(f"[FileProtection] {error_msg}")
            return False, error_msg
        
        # Restore original permissions
        try:
            if file_path in self.original_attributes:
                mode = self.original_attributes[file_path]
                del self.original_attributes[file_path]
            else:
                mode = stat.S_IRUSR | stat.S_IWUSR  # 600 (rw-------)
            
            os.chmod(file_path, mode)
            return True, None
            
        except Exception as e:
            return False, f"Permission restore failed: {e}"
    
    def _protect_multiple_files_linux_batch(self, file_paths: List[str]) -> Tuple[int, List[str]]:
        """
        Protect multiple files using elevated daemon.
        
        DAEMON-ONLY: Single solution, no fallbacks.
        One authorization for all files - truly seamless operation.
        
        Args:
            file_paths: List of file paths to protect
            
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        if not file_paths:
            return 0, ["No files to protect"]
        
        success_count = 0
        errors = []
        
        print(f"[FileProtection] � Protecting {len(file_paths)} files via daemon...")
        batch_success = self._try_batch_chattr_with_daemon(file_paths, set_immutable=True)
        
        if not batch_success:
            error_msg = "❌ Daemon elevation failed - monitoring cannot start."
            print(f"[FileProtection] {error_msg}")
            return 0, [error_msg]
        
        # Verify all files got immutable flag
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            if self._verify_immutable_flag(file_path):
                success_count += 1
                self.protected_files.append(file_path)
                print(f"[FileProtection] ✅ IMMUTABLE: {filename}")
            else:
                errors.append(f"{filename}: Immutable flag not set")
                print(f"[FileProtection] ⚠️  Failed verification: {filename}")
        
        if success_count > 0:
            print(f"[FileProtection] 🔒 {success_count}/{len(file_paths)} files CANNOT be deleted, even by root")
            print(f"[FileProtection] ℹ️  Authorization cached for this session - works after reboot too!")
            return success_count, errors
        else:
            error_msg = "❌ File protection verification failed - all files. Monitoring cannot start."
            print(f"[FileProtection] {error_msg}")
            return 0, [error_msg]
    
    def _try_batch_chattr_with_daemon(self, file_paths: List[str], set_immutable: bool) -> bool:
        """
        Try to set/unset immutable flag using elevated daemon.
        
        Daemon runs as root via systemd service.
        No polkit prompts needed - daemon is already elevated.
        Works seamlessly across reboots.
        
        Args:
            file_paths: List of file paths
            set_immutable: True to set +i, False to set -i
            
        Returns:
            True if command succeeded, False otherwise
        """
        try:
            from core.linux.elevated_daemon_client import get_elevated_client, ElevatedClientError
            
            client = get_elevated_client()
            
            # Check if daemon is available
            if not client.is_available():
                print(f"[FileProtection] ⚠️  Elevated daemon not available")
                return False
            
            # Use daemon for file operations
            action = "protecting" if set_immutable else "unprotecting"
            print(f"[FileProtection] Using elevated daemon for {action} {len(file_paths)} files...")
            
            success, message = client.chattr(file_paths, set_immutable=set_immutable)
            
            if success:
                action = "protected" if set_immutable else "unprotected"
                print(f"[FileProtection] ✅ Daemon {action} {len(file_paths)} files (no password prompt!)")
                print(f"[FileProtection] ℹ️  Seamless operation across reboots!")
                return True
            else:
                print(f"[FileProtection] ⚠️  Daemon operation failed: {message}")
                return False
        
        except ImportError:
            print(f"[FileProtection] ⚠️  Elevated daemon client not available")
            return False
        except Exception as e:
            print(f"[FileProtection] ⚠️  Elevated daemon error: {e}")
            return False
    
    def _try_chattr_with_daemon(self, file_paths: List[str], set_immutable: bool) -> Tuple[bool, str]:
        """
        Try to set/unset immutable flag using elevated daemon (single or multiple files).
        
        Args:
            file_paths: List of file paths (or single file)
            set_immutable: True to set +i, False to set -i
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            from core.linux.elevated_daemon_client import get_elevated_client, ElevatedClientError
            
            client = get_elevated_client()
            
            # Check if daemon is available
            if not client.is_available():
                return False, "Daemon not available"
            
            # Use daemon for file operations
            success, message = client.chattr(file_paths, set_immutable=set_immutable)
            
            if success:
                return True, message
            else:
                return False, message
        
        except ImportError:
            return False, "Daemon client not available"
        except Exception as e:
            return False, f"Daemon error: {e}"
    


    def _verify_immutable_flag(self, file_path: str) -> bool:
        """
        Verify that a file has the immutable flag set.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if immutable flag is set, False otherwise
        """
        try:
            import subprocess
            
            result = subprocess.run(
                ['lsattr', file_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # lsattr output format: "----i--------- /path/to/file"
                # Check if 'i' flag is present in first column
                output = result.stdout.strip()
                if output and 'i' in output.split()[0]:
                    return True
            
            return False
            
        except Exception:
            return False
    

    def get_protected_files(self) -> List[str]:
        """
        Get list of currently protected files.
        
        Returns:
            List of file paths
        """
        return self.protected_files.copy()
    
    def is_file_protected(self, file_path: str) -> bool:
        """
        Check if a file is currently protected.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is in protected list
        """
        return file_path in self.protected_files


# Singleton instance
_file_protection_manager: Optional[FileProtectionManager] = None


def get_file_protection_manager() -> FileProtectionManager:
    """
    Get singleton instance of FileProtectionManager.
    
    Returns:
        FileProtectionManager instance
    """
    global _file_protection_manager
    if _file_protection_manager is None:
        _file_protection_manager = FileProtectionManager()
    return _file_protection_manager
