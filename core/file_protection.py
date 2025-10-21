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
        
        Args:
            file_paths: List of file paths to protect
            
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        success_count = 0
        errors = []
        
        for file_path in file_paths:
            success, error = self.protect_file(file_path)
            if success:
                success_count += 1
                self.protected_files.append(file_path)
                print(f"[FileProtection] ✅ Protected: {os.path.basename(file_path)}")
            else:
                errors.append(f"{os.path.basename(file_path)}: {error}")
                print(f"[FileProtection] ❌ Failed to protect: {os.path.basename(file_path)} - {error}")
        
        return success_count, errors
    
    def unprotect_all_files(self) -> Tuple[int, List[str]]:
        """
        Remove protection from all previously protected files.
        
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        success_count = 0
        errors = []
        
        for file_path in self.protected_files[:]:  # Copy list to avoid modification during iteration
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
        Protect file on Windows using SetFileAttributesW.
        
        Sets attributes: HIDDEN + SYSTEM + READONLY
        This makes the file harder to delete and hidden from normal view.
        """
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
        
        Restores original attributes or sets to NORMAL.
        """
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
        
        Protection hierarchy:
        1. chattr +i with pkexec (PolicyKit GUI prompt - BEST)
        2. chattr +i with sudo (terminal prompt - GOOD)
        3. chattr +i without elevation (will likely fail - WEAK)
        4. chmod 400 + fcntl lock (detectable but bypassable - LAST RESORT)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        filename = os.path.basename(file_path)
        
        # Primary method: chattr +i with pkexec (GUI prompt)
        success, error = self._try_chattr_with_pkexec(file_path, set_immutable=True)
        if success:
            print(f"[FileProtection] ✅ IMMUTABLE: {filename} (chattr +i via pkexec)")
            print(f"[FileProtection] 🔒 File CANNOT be deleted, even by root")
            return True, None
        else:
            print(f"[FileProtection] ⚠️  pkexec chattr failed: {error}")
        
        # Fallback 1: chattr +i with sudo (terminal prompt)
        success, error = self._try_chattr_with_sudo(file_path, set_immutable=True)
        if success:
            print(f"[FileProtection] ✅ IMMUTABLE: {filename} (chattr +i via sudo)")
            print(f"[FileProtection] 🔒 File CANNOT be deleted, even by root")
            return True, None
        else:
            print(f"[FileProtection] ⚠️  sudo chattr failed: {error}")
        
        # Fallback 2: chattr +i without elevation (will likely fail)
        success, error = self._try_chattr_immutable(file_path, set_immutable=True)
        if success:
            print(f"[FileProtection] ✅ IMMUTABLE: {filename} (chattr +i)")
            print(f"[FileProtection] 🔒 File CANNOT be deleted, even by root")
            return True, None
        else:
            print(f"[FileProtection] ⚠️  chattr without elevation failed: {error}")
        
        # Last resort: chmod 400 + fcntl lock (WEAK - only detectable by file monitor)
        print(f"[FileProtection] ⚠️  CRITICAL: Could not set immutable flag!")
        print(f"[FileProtection] ⚠️  Falling back to chmod 400 + file lock (WEAK protection)")
        
        try:
            # Set restrictive permissions
            os.chmod(file_path, stat.S_IRUSR)  # 400 - read-only for owner
            print(f"[FileProtection] 📝 Permissions: 400 (read-only) on {filename}")
        except Exception as e:
            print(f"[FileProtection] ❌ chmod 400 failed: {e}")
        
        # Keep file descriptor open with lock (advisory only)
        try:
            import fcntl
            fd = open(file_path, 'r')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.file_locks[file_path] = fd
            print(f"[FileProtection] 🔓 Advisory lock acquired on {filename}")
        except Exception as e:
            print(f"[FileProtection] ⚠️  File lock failed: {e}")
        
        print(f"[FileProtection] ⚠️  File CAN be deleted with rm/sudo - monitor will auto-restore")
        return True, None  # Still return success to not block monitoring
    
    def _unprotect_file_linux(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove protection from file on Linux.
        
        Removes immutable flag and restores permissions.
        """
        filename = os.path.basename(file_path)
        
        # Release file lock if held (advisory lock from fallback)
        if file_path in self.file_locks:
            try:
                import fcntl
                fd = self.file_locks[file_path]
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
                del self.file_locks[file_path]
                print(f"[FileProtection] 🔓 Released advisory lock on {filename}")
            except Exception as e:
                print(f"[FileProtection] ⚠️  Failed to release lock: {e}")
        
        # Remove immutable flag (try all methods)
        immutable_removed = False
        
        # Try pkexec first (GUI prompt)
        success, error = self._try_chattr_with_pkexec(file_path, set_immutable=False)
        if success:
            print(f"[FileProtection] ✅ Immutable flag removed: {filename} (pkexec)")
            immutable_removed = True
        else:
            # Try sudo (terminal prompt)
            success, error = self._try_chattr_with_sudo(file_path, set_immutable=False)
            if success:
                print(f"[FileProtection] ✅ Immutable flag removed: {filename} (sudo)")
                immutable_removed = True
            else:
                # Try without elevation
                success, error = self._try_chattr_immutable(file_path, set_immutable=False)
                if success:
                    print(f"[FileProtection] ✅ Immutable flag removed: {filename}")
                    immutable_removed = True
                else:
                    print(f"[FileProtection] ⚠️  Could not remove immutable flag: {error}")
        
        # Restore original permissions
        try:
            if file_path in self.original_attributes:
                mode = self.original_attributes[file_path]
                del self.original_attributes[file_path]
            else:
                mode = stat.S_IRUSR | stat.S_IWUSR  # 600 (rw-------)
            
            os.chmod(file_path, mode)
            print(f"[FileProtection] 📝 Restored permissions on {filename}")
            return True, None
            
        except Exception as e:
            if immutable_removed:
                # Immutable flag removed but chmod failed - still partially successful
                print(f"[FileProtection] ⚠️  Immutable removed but chmod failed: {e}")
                return True, None
            else:
                return False, f"Unprotection failed: {e}"
    
    def _try_chattr_with_pkexec(self, file_path: str, set_immutable: bool) -> Tuple[bool, Optional[str]]:
        """
        Try to set/unset immutable flag using pkexec (PolicyKit GUI prompt).
        
        Args:
            file_path: Path to file
            set_immutable: True to set +i, False to set -i
            
        Returns:
            Tuple of (success: bool, error: Optional[str])
        """
        try:
            import subprocess
            
            flag = "+i" if set_immutable else "-i"
            result = subprocess.run(
                ['pkexec', 'chattr', flag, file_path],
                capture_output=True,
                text=True,
                timeout=30  # Longer timeout for user to respond to GUI
            )
            
            if result.returncode == 0:
                return True, None
            else:
                stderr = result.stderr.strip()
                # Check if user cancelled
                if "dismissed" in stderr.lower() or "cancelled" in stderr.lower():
                    return False, "User cancelled authorization"
                return False, f"pkexec chattr failed: {stderr}"
                
        except FileNotFoundError:
            return False, "pkexec command not found"
        except subprocess.TimeoutExpired:
            return False, "pkexec timeout (user did not respond)"
        except Exception as e:
            return False, f"pkexec exception: {e}"
    
    def _try_chattr_with_sudo(self, file_path: str, set_immutable: bool) -> Tuple[bool, Optional[str]]:
        """
        Try to set/unset immutable flag using sudo (terminal password prompt).
        
        Args:
            file_path: Path to file
            set_immutable: True to set +i, False to set -i
            
        Returns:
            Tuple of (success: bool, error: Optional[str])
        """
        try:
            import subprocess
            
            flag = "+i" if set_immutable else "-i"
            result = subprocess.run(
                ['sudo', '-n', 'chattr', flag, file_path],  # -n = non-interactive (fail if password needed)
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, None
            else:
                stderr = result.stderr.strip()
                # Check if password required
                if "password is required" in stderr.lower() or "sudo: a password" in stderr.lower():
                    return False, "Sudo requires password (run FadCrypt from terminal with sudo)"
                return False, f"sudo chattr failed: {stderr}"
                
        except FileNotFoundError:
            return False, "sudo command not found"
        except subprocess.TimeoutExpired:
            return False, "sudo timeout"
        except Exception as e:
            return False, f"sudo exception: {e}"
    
    def _try_chattr_immutable(self, file_path: str, set_immutable: bool) -> Tuple[bool, Optional[str]]:
        """
        Try to set/unset immutable flag using chattr (without elevation).
        
        Args:
            file_path: Path to file
            set_immutable: True to set +i, False to set -i
            
        Returns:
            Tuple of (success: bool, error: Optional[str])
        """
        try:
            import subprocess
            
            flag = "+i" if set_immutable else "-i"
            result = subprocess.run(
                ['chattr', flag, file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, f"chattr failed: {result.stderr}"
                
        except FileNotFoundError:
            return False, "chattr command not found"
        except Exception as e:
            return False, f"chattr exception: {e}"
    
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
