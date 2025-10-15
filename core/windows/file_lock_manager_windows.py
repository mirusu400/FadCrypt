"""
Windows File Lock Manager

Implements file/folder locking using icacls to deny all access.
Backs up and restores ACLs for proper permission recovery.
"""

import os
import subprocess
import tempfile
from typing import Dict, Optional
import time

from core.file_lock_manager import FileLockManager


class FileLockManagerWindows(FileLockManager):
    """Windows implementation of file/folder locking using icacls"""
    
    def __init__(self, config_folder: str):
        super().__init__(config_folder)
        self.acl_backup_folder = os.path.join(config_folder, "acl_backups")
        os.makedirs(self.acl_backup_folder, exist_ok=True)
    
    def _get_acl_backup_path(self, item_path: str) -> str:
        """Get path for ACL backup file"""
        # Create safe filename from path
        safe_name = item_path.replace(':', '').replace('\\', '_').replace('/', '_')
        return os.path.join(self.acl_backup_folder, f"{safe_name}.acl")
    
    def _backup_acl(self, path: str) -> bool:
        """Backup ACL for path"""
        backup_path = self._get_acl_backup_path(path)
        
        try:
            # Use icacls to save ACL
            result = subprocess.run(
                ['icacls', path, '/save', backup_path, '/T'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  💾 ACL backed up to: {os.path.basename(backup_path)}")
                return True
            else:
                print(f"  ⚠️  ACL backup warning: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error backing up ACL: {e}")
            return False
    
    def _restore_acl(self, path: str) -> bool:
        """Restore ACL from backup"""
        backup_path = self._get_acl_backup_path(path)
        
        if not os.path.exists(backup_path):
            print(f"  ⚠️  No ACL backup found, using default restore")
            # Fallback: Grant full control to Everyone
            try:
                subprocess.run(
                    ['icacls', path, '/grant', 'Everyone:(F)'],
                    capture_output=True,
                    timeout=10
                )
                return True
            except:
                return False
        
        try:
            # Restore ACL from backup
            result = subprocess.run(
                ['icacls', os.path.dirname(path), '/restore', backup_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  ✅ ACL restored from backup")
                # Clean up backup file
                try:
                    os.remove(backup_path)
                except:
                    pass
                return True
            else:
                print(f"  ⚠️  ACL restore warning: {result.stderr}")
                # Try fallback
                subprocess.run(['icacls', path, '/grant', 'Everyone:(F)'], timeout=10)
                return False
                
        except Exception as e:
            print(f"  ❌ Error restoring ACL: {e}")
            return False
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder.
        
        Returns dict with: name, path, type, original_permissions (ACL backup path), filesystem, lock_method
        """
        try:
            # Backup ACL first
            backup_path = self._get_acl_backup_path(path)
            if self._backup_acl(path):
                original_permissions = backup_path
            else:
                original_permissions = "default"  # Will use fallback restore
            
            metadata = {
                "name": os.path.basename(path) or path,
                "path": os.path.abspath(path),
                "type": item_type,
                "original_permissions": original_permissions,
                "filesystem": "ntfs",  # Windows is typically NTFS
                "lock_method": "icacls",
                "locked_at": int(time.time())
            }
            
            print(f"  📋 Metadata: {metadata['name']} | ACL backed up | icacls")
            return metadata
            
        except Exception as e:
            print(f"❌ Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock file or folder by denying all permissions.
        
        Denies: Read, Write, Execute, Delete, Delete Child, Change Permissions
        """
        path = item['path']
        
        if not os.path.exists(path):
            print(f"⚠️  Path no longer exists: {path}")
            return False
        
        try:
            # Deny all permissions to Everyone
            # F=Full Control, R=Read, W=Write, D=Delete, DC=Delete Child, X=Execute
            # WD=Write Data, AD=Append Data, REA=Read Extended Attributes, WEA=Write Extended Attributes
            print(f"  🔒 Denying all access with icacls: {path}")
            
            result = subprocess.run(
                ['icacls', path, '/deny', 'Everyone:(F,R,W,D,DC,WD,AD,X,REA,WEA)'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ❌ icacls deny failed: {result.stderr}")
                return False
            
            # For folders, also deny inheritance
            if item['type'] == 'folder':
                subprocess.run(
                    ['icacls', path, '/inheritance:r'],
                    capture_output=True,
                    timeout=10
                )
            
            print(f"  ✅ Access denied successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Lock operation timed out for: {path}")
            return False
        except Exception as e:
            print(f"  ❌ Error locking {path}: {e}")
            return False
    
    def _unlock_item(self, item: Dict) -> bool:
        """
        Unlock file or folder and restore original ACL.
        """
        path = item['path']
        
        if not os.path.exists(path):
            print(f"⚠️  Path no longer exists: {path}")
            return True  # Consider it "unlocked" if it doesn't exist
        
        try:
            # Step 1: Remove deny rules
            print(f"  🔓 Removing deny rules: {path}")
            subprocess.run(
                ['icacls', path, '/remove:d', 'Everyone'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Step 2: Restore ACL from backup
            print(f"  🔓 Restoring original ACL: {path}")
            if self._restore_acl(path):
                print(f"  ✅ Access restored successfully")
                return True
            else:
                print(f"  ⚠️  ACL restore had issues, but deny rules removed")
                return True  # Partial success
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Unlock operation timed out for: {path}")
            return False
        except Exception as e:
            print(f"  ❌ Error unlocking {path}: {e}")
            return False
    
    def _lock_config_file(self, path: str):
        """
        Lock config file (deny delete/write but allow read).
        """
        if not os.path.exists(path):
            return
        
        try:
            # Deny only delete and write, keep read permission
            subprocess.run(
                ['icacls', path, '/deny', 'Everyone:(D,DC,WD,AD)'],
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
            # Remove deny rules
            subprocess.run(
                ['icacls', path, '/remove:d', 'Everyone'],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            print(f"  ⚠️  Error unlocking config {path}: {e}")
