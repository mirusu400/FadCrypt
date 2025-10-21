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
        
        On Linux: Uses batch chattr +i with single pkexec prompt for all files.
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
        
        # Linux: Use batch protection with single pkexec prompt
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
        
        On Linux: Uses batch chattr -i with single authorization for all files.
        On Windows: Unprotects each file individually.
        
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        if not self.protected_files:
            return 0, []
        
        success_count = 0
        errors = []
        
        # Linux: Use batch unprotection with single authorization
        if IS_LINUX and len(self.protected_files) > 1:
            batch_success = self._try_batch_chattr_with_pkexec(self.protected_files, set_immutable=False)
            
            if not batch_success:
                batch_success = self._try_batch_chattr_with_sudo(self.protected_files, set_immutable=False)
            
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
        
        POLKIT-ONLY APPROACH: No fallbacks.
        Requires PolicyKit authorization via pkexec - this is the ONLY supported method.
        If polkit fails, file protection fails completely.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        filename = os.path.basename(file_path)
        
        # ENFORCE: Use ONLY pkexec (NO FALLBACKS)
        print(f"[FileProtection] � Requesting polkit authorization for {filename}...")
        success, error = self._try_chattr_with_pkexec(file_path, set_immutable=True)
        
        if success:
            print(f"[FileProtection] ✅ IMMUTABLE: {filename}")
            print(f"[FileProtection] 🔒 File CANNOT be deleted, even by root")
            return True, None
        else:
            # HARD FAIL - no fallbacks allowed
            error_msg = f"❌ Polkit authorization failed: {error}"
            print(f"[FileProtection] {error_msg}")
            return False, error_msg
        print(f"[FileProtection] ⚠️  File CAN be deleted with rm/sudo - monitor will auto-restore")
        return True, None  # Still return success to not block monitoring
    
    def _unprotect_file_linux(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove protection from file on Linux.
        
        POLKIT-ONLY APPROACH: No fallbacks.
        Removes immutable flag and restores permissions via pkexec only.
        """
        filename = os.path.basename(file_path)
        
        # ENFORCE: Use ONLY pkexec (NO FALLBACKS)
        print(f"[FileProtection] � Requesting polkit authorization to unprotect {filename}...")
        success, error = self._try_chattr_with_pkexec(file_path, set_immutable=False)
        
        if not success:
            error_msg = f"❌ Polkit authorization failed: {error}"
            print(f"[FileProtection] {error_msg}")
            return False, error_msg
        
        print(f"[FileProtection] ✅ Immutable flag removed: {filename}")
        
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
            error_msg = f"Unprotection failed: {e}"
            print(f"[FileProtection] ❌ {error_msg}")
            return False, error_msg
    
    def _protect_multiple_files_linux_batch(self, file_paths: List[str]) -> Tuple[int, List[str]]:
        """
        Protect multiple files with single pkexec authorization (Linux only).
        
        POLKIT-ONLY APPROACH: No fallbacks. User must authenticate via polkit.
        Uses batch chattr +i command to set immutable flag on all files at once.
        
        Args:
            file_paths: List of file paths to protect
            
        Returns:
            Tuple of (success_count: int, errors: List[str])
        """
        if not file_paths:
            return 0, ["No files to protect"]
        
        success_count = 0
        errors = []
        
        # ENFORCE: Use ONLY polkit (no fallbacks)
        print(f"[FileProtection] 🔐 Requesting polkit authorization to protect {len(file_paths)} files...")
        batch_success = self._try_batch_chattr_with_pkexec(file_paths, set_immutable=True)
        
        if not batch_success:
            # Polkit failed - NO FALLBACK, HARD FAIL
            error_msg = "❌ Polkit authorization required. File protection failed - monitoring cannot start."
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
    
    def _try_batch_chattr_with_pkexec(self, file_paths: List[str], set_immutable: bool) -> bool:
        """
        Try to set/unset immutable flag on multiple files with single pkexec prompt.
        Uses polkit policy for persistent authorization - no repeated prompts after first grant.
        
        Args:
            file_paths: List of file paths
            set_immutable: True to set +i, False to set -i
            
        Returns:
            True if command succeeded, False otherwise
        """
        try:
            import subprocess
            
            # Try helper script first (uses polkit policy for persistence)
            helper_script = "/usr/libexec/fadcrypt/fadcrypt-file-protection-helper.sh"
            if os.path.exists(helper_script):
                action = "protect" if set_immutable else "unprotect"
                cmd = ['pkexec', helper_script, action] + file_paths
                
                print(f"[FileProtection] Using polkit policy helper for persistent authorization...")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    action_text = "protected" if set_immutable else "unprotected"
                    print(f"[FileProtection] ✅ Batch {action_text} {len(file_paths)} files (polkit)")
                    print(f"[FileProtection] ℹ️  Authorization persists - no more prompts needed!")
                    return True
                else:
                    stderr = result.stderr.strip()
                    if "dismissed" in stderr.lower() or "cancelled" in stderr.lower():
                        print(f"[FileProtection] ⚠️  User cancelled authorization")
                    else:
                        print(f"[FileProtection] ⚠️  Helper script failed: {stderr}")
                    return False
            
            # Fallback: direct chattr with pkexec (standard method)
            print(f"[FileProtection] Helper script not found, using direct pkexec...")
            flag = "+i" if set_immutable else "-i"
            cmd = ['pkexec', 'chattr', flag] + file_paths
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                action = "protected" if set_immutable else "unprotected"
                print(f"[FileProtection] ✅ Batch {action} {len(file_paths)} files")
                return True
            else:
                stderr = result.stderr.strip()
                if "dismissed" in stderr.lower() or "cancelled" in stderr.lower():
                    print(f"[FileProtection] ⚠️  User cancelled batch authorization")
                else:
                    print(f"[FileProtection] ⚠️  Batch pkexec failed: {stderr}")
                return False
                
        except FileNotFoundError:
            print(f"[FileProtection] ⚠️  pkexec not found")
            return False
        except subprocess.TimeoutExpired:
            print(f"[FileProtection] ⚠️  pkexec timeout")
            return False
        except Exception as e:
            print(f"[FileProtection] ⚠️  Batch pkexec exception: {e}")
            return False
    
    def _try_batch_chattr_with_sudo(self, file_paths: List[str], set_immutable: bool) -> bool:
        """
        Try to set/unset immutable flag on multiple files with sudo.
        
        Args:
            file_paths: List of file paths
            set_immutable: True to set +i, False to set -i
            
        Returns:
            True if command succeeded, False otherwise
        """
        try:
            import subprocess
            
            flag = "+i" if set_immutable else "-i"
            
            # Build command: sudo -n chattr +i file1 file2 file3...
            cmd = ['sudo', '-n', 'chattr', flag] + file_paths
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                action = "protected" if set_immutable else "unprotected"
                print(f"[FileProtection] ✅ Batch {action} {len(file_paths)} files with sudo")
                return True
            else:
                stderr = result.stderr.strip()
                print(f"[FileProtection] ⚠️  Batch sudo failed: {stderr}")
                return False
                
        except Exception as e:
            print(f"[FileProtection] ⚠️  Batch sudo exception: {e}")
            return False
    
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
