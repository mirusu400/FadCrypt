"""
Linux File Lock Manager

Implements file/folder locking using chmod + chattr for complete inaccessibility.
Lock order: chmod 000 (remove all permissions) → chattr +i (make immutable)
Unlock order: chattr -i (remove immutable) → chmod original (restore permissions)
"""

import os
import subprocess
import stat
from typing import Dict, Optional
import time

from core.file_lock_manager import FileLockManager


class FileLockManagerLinux(FileLockManager):
    """Linux implementation of file/folder locking using chmod + chattr"""
    
    def _detect_filesystem(self, path: str) -> str:
        """
        Detect filesystem type for given path.
        
        Returns:
            Filesystem type (e.g., 'ext4', 'ntfs', 'btrfs')
        """
        try:
            result = subprocess.run(
                ['df', '-T', path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output: Filesystem Type Size Used Avail Use% Mounted
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        fs_type = parts[1].lower()
                        print(f"  📂 Detected filesystem: {fs_type} for {path}")
                        return fs_type
        except Exception as e:
            print(f"⚠️  Error detecting filesystem: {e}")
        
        return "unknown"
    
    def _get_file_permissions(self, path: str) -> str:
        """Get file permissions in octal format (e.g., '644')"""
        try:
            st = os.stat(path)
            permissions = oct(st.st_mode)[-3:]
            return permissions
        except Exception as e:
            print(f"⚠️  Error getting permissions for {path}: {e}")
            return "644"  # Safe default
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder.
        
        Returns dict with: name, path, type, original_permissions, filesystem, lock_method
        """
        try:
            filesystem = self._detect_filesystem(path)
            original_permissions = self._get_file_permissions(path)
            
            # Determine lock method based on filesystem
            if 'ntfs' in filesystem:
                lock_method = "chmod_only"  # chattr doesn't work on NTFS
            else:
                lock_method = "chmod_chattr"  # Standard ext4/ext3/ext2
            
            metadata = {
                "name": os.path.basename(path) or path,
                "path": os.path.abspath(path),
                "type": item_type,
                "original_permissions": original_permissions,
                "filesystem": filesystem,
                "lock_method": lock_method,
                "locked_at": int(time.time())
            }
            
            print(f"  📋 Metadata: {metadata['name']} | {original_permissions} | {filesystem} | {lock_method}")
            return metadata
            
        except Exception as e:
            print(f"❌ Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock file or folder completely (no read/write/delete/rename).
        
        Order: chmod 000 → chattr +i (correct order as confirmed by user)
        """
        path = item['path']
        lock_method = item.get('lock_method', 'chmod_chattr')
        
        if not os.path.exists(path):
            print(f"⚠️  Path no longer exists: {path}")
            return False
        
        try:
            # Step 1: Remove all permissions (make unreadable/unwritable)
            print(f"  🔒 Step 1: chmod 000 {path}")
            result = subprocess.run(
                ['pkexec', 'chmod', '000', path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ❌ chmod failed: {result.stderr}")
                return False
            
            # Step 2: Make immutable (only if not NTFS)
            if lock_method == "chmod_chattr":
                print(f"  🔒 Step 2: chattr +i {path}")
                
                # For folders, use recursive flag
                if item['type'] == 'folder':
                    cmd = ['pkexec', 'chattr', '-R', '+i', path]
                else:
                    cmd = ['pkexec', 'chattr', '+i', path]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    print(f"  ⚠️  chattr warning: {result.stderr}")
                    # Don't fail if chattr doesn't work, chmod 000 still provides protection
            
            # Verify lock by attempting to read
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as f:
                        f.read(1)
                    print(f"  ⚠️  Warning: File still readable after lock")
                except PermissionError:
                    print(f"  ✅ Verified: File is now unreadable")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Lock operation timed out for: {path}")
            return False
        except Exception as e:
            print(f"  ❌ Error locking {path}: {e}")
            return False
    
    def _unlock_item(self, item: Dict) -> bool:
        """
        Unlock file or folder and restore original permissions.
        
        Order: chattr -i → chmod original
        """
        path = item['path']
        lock_method = item.get('lock_method', 'chmod_chattr')
        original_permissions = item.get('original_permissions', '644')
        
        if not os.path.exists(path):
            print(f"⚠️  Path no longer exists: {path}")
            return True  # Consider it "unlocked" if it doesn't exist
        
        try:
            # Step 1: Remove immutable flag (only if it was set)
            if lock_method == "chmod_chattr":
                print(f"  🔓 Step 1: chattr -i {path}")
                
                # For folders, use recursive flag
                if item['type'] == 'folder':
                    cmd = ['pkexec', 'chattr', '-R', '-i', path]
                else:
                    cmd = ['pkexec', 'chattr', '-i', path]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    print(f"  ⚠️  chattr warning: {result.stderr}")
                    # Continue anyway, chmod should still work
            
            # Step 2: Restore original permissions
            print(f"  🔓 Step 2: chmod {original_permissions} {path}")
            result = subprocess.run(
                ['pkexec', 'chmod', original_permissions, path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ❌ chmod failed: {result.stderr}")
                return False
            
            # Verify unlock by attempting to read (if it's a file)
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as f:
                        f.read(1)
                    print(f"  ✅ Verified: File is now readable")
                except PermissionError:
                    print(f"  ⚠️  Warning: File still not readable")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Unlock operation timed out for: {path}")
            return False
        except Exception as e:
            print(f"  ❌ Error unlocking {path}: {e}")
            return False
    
    def _lock_config_file(self, path: str):
        """
        Lock config file (keep readable by FadCrypt, prevent modification/deletion).
        Only use chattr +i to prevent modifications while keeping readable.
        """
        if not os.path.exists(path):
            return
        
        try:
            # Only make immutable, don't change permissions
            # This prevents deletion/modification but keeps file readable
            subprocess.run(
                ['pkexec', 'chattr', '+i', path],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            print(f"  ⚠️  Error locking config {path}: {e}")
    
    def _unlock_config_file(self, path: str):
        """Unlock config file"""
        if not os.path.exists(path):
            return
        
        try:
            subprocess.run(
                ['pkexec', 'chattr', '-i', path],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            print(f"  ⚠️  Error unlocking config {path}: {e}")
