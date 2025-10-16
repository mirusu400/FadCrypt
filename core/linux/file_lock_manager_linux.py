"""
Linux File Lock Manager

Implements file/folder locking using simple chmod (no sudo required).
- Lock: chmod 000 (remove all permissions) + kill processes with file open
- Unlock: restore original permissions
- Stores original permissions for proper restoration
"""

import os
import subprocess
import stat
from typing import Dict, Optional, Tuple, List
import json
import psutil
from datetime import datetime

from core.file_lock_manager import FileLockManager


class FileLockManagerLinux(FileLockManager):
    """Linux implementation of file/folder locking using chmod (no sudo)"""
    
    def __init__(self, config_folder: str):
        super().__init__(config_folder)
        # Store original permissions for restoration
        self.permissions_file = os.path.join(config_folder, '.file_permissions.json')
        self.original_permissions = self._load_permissions()
        
        # Perform cleanup on initialization (handles crash recovery)
        self._cleanup_on_startup()
    
    def _cleanup_on_startup(self):
        """
        Cleanup any stuck locks from previous sessions (crash recovery).
        Unlocks all files that have stored permissions.
        """
        if not self.original_permissions:
            return  # Nothing to clean up
        
        print("🧹 Performing startup cleanup (crash recovery)...")
        cleaned_count = 0
        
        for path, original_perms in list(self.original_permissions.items()):
            if os.path.exists(path):
                try:
                    # Restore original permissions
                    perms = int(original_perms, 8)
                    os.chmod(path, perms)
                    print(f"  ✅ Restored: {os.path.basename(path)} (chmod {original_perms})")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠️  Could not restore {path}: {e}")
        
        # Clear permissions storage after cleanup
        if cleaned_count > 0:
            self.original_permissions.clear()
            self._save_permissions()
            print(f"✅ Startup cleanup complete: Restored {cleaned_count} items")
    
    def _load_permissions(self) -> Dict:
        """Load stored file permissions"""
        if os.path.exists(self.permissions_file):
            try:
                with open(self.permissions_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_permissions(self):
        """Save file permissions to disk"""
        try:
            with open(self.permissions_file, 'w') as f:
                json.dump(self.original_permissions, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save permissions: {e}")
    
    def _get_processes_using_file(self, file_path: str) -> List[int]:
        """Find process IDs that have the file open"""
        pids = []
        try:
            # Method 1: Use lsof (more reliable)
            result = subprocess.run(
                ['lsof', '-t', file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = [int(pid) for pid in result.stdout.strip().split('\n') if pid.strip()]
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            # Fallback: Use psutil to scan all processes
            try:
                for proc in psutil.process_iter(['pid', 'open_files']):
                    try:
                        if proc.info['open_files']:
                            for file_info in proc.info['open_files']:
                                if file_info.path == file_path:
                                    pids.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass
        
        return pids
    
    def _kill_processes_using_file(self, file_path: str) -> int:
        """Kill processes that have the file open. Returns number of processes killed."""
        pids = self._get_processes_using_file(file_path)
        killed_count = 0
        
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                print(f"   🔪 Killing process {pid} ({proc_name}) using {os.path.basename(file_path)}")
                proc.kill()
                proc.wait(timeout=3)  # Wait for process to die
                killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        return killed_count
    
    def temporarily_unlock_config(self, config_name: str) -> bool:
        """
        Temporarily unlock a config file for writing (chmod 644).
        Returns True if unlocked successfully, False otherwise.
        """
        file_path = os.path.join(self.config_folder, config_name)
        if not os.path.exists(file_path):
            return True  # Doesn't exist, no need to unlock
        
        try:
            # Make writable (chmod 644)
            os.chmod(file_path, 0o644)
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not unlock {config_name}: {e}")
            return False
    
    def relock_config(self, config_name: str) -> bool:
        """
        Re-lock a config file after writing (chmod 444).
        Returns True if locked successfully, False otherwise.
        """
        file_path = os.path.join(self.config_folder, config_name)
        if not os.path.exists(file_path):
            return True
        
        try:
            # Make read-only (chmod 444)
            os.chmod(file_path, 0o444)
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not relock {config_name}: {e}")
            return False
    
    def lock_all_with_configs(self) -> Tuple[int, int]:
        """
        Lock all user items AND config files (no sudo required).
        Uses chmod 000 to make files/folders inaccessible.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        # Get config files
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        existing_config_files = [f for f in critical_files if os.path.exists(f)]
        
        total_items = len(self.locked_items) + len(existing_config_files)
        
        if total_items == 0:
            print("ℹ️  No items to lock")
            return (0, 0)
        
        print(f"🔒 Locking {len(self.locked_items)} items + {len(existing_config_files)} config files...")
        
        success_count = 0
        failure_count = 0
        
        # Lock user files/folders
        for item in self.locked_items:
            path = item['path']
            item_name = item['name']
            
            if not os.path.exists(path):
                print(f"⚠️  Skipping (doesn't exist): {item_name}")
                failure_count += 1
                continue
            
            try:
                # Store original permissions before locking
                original_mode = os.stat(path).st_mode
                self.original_permissions[path] = oct(stat.S_IMODE(original_mode))
                
                # Kill any processes using this file
                killed = self._kill_processes_using_file(path)
                if killed > 0:
                    print(f"   🔪 Killed {killed} process(es) using {item_name}")
                
                # Lock strategy:
                # - Files: Make read-only (chmod 444) so watchdog can monitor modifications
                # - Folders: Make read-only (chmod 555) with active monitoring for access attempts
                #   (chmod 000 would block completely but we couldn't detect access or show password dialog)
                if item['type'] == 'folder':
                    os.chmod(path, 0o555)  # r-xr-xr-x (read + execute, but we monitor access)
                    print(f"✅ Locked: {item_name} (chmod 555 - monitored folder)")
                else:
                    os.chmod(path, 0o444)  # r--r--r-- (read-only file)
                    print(f"✅ Locked: {item_name} (chmod 444 - read-only file)")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed to lock {item_name}: {e}")
                failure_count += 1
        
        # Lock config files (keep them readable but protected)
        for file_path in existing_config_files:
            try:
                # Store original permissions
                original_mode = os.stat(file_path).st_mode
                self.original_permissions[file_path] = oct(stat.S_IMODE(original_mode))
                
                # Make read-only (chmod 444) so config is still readable but not writable
                os.chmod(file_path, 0o444)
                print(f"✅ Protected config: {os.path.basename(file_path)} (chmod 444)")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed to protect {os.path.basename(file_path)}: {e}")
                failure_count += 1
        
        # Save permissions to disk
        self._save_permissions()
        
        if failure_count == 0:
            print(f"✅ Successfully locked {success_count} items")
        else:
            print(f"⚠️  Locked {success_count} items, {failure_count} failed")
        
        return (success_count, failure_count)
    
    def unlock_all_with_configs(self, silent: bool = False) -> Tuple[int, int]:
        """
        Unlock all user items AND config files (restore original permissions).
        Uses stored permissions to restore exact original state.
        
        Args:
            silent: If True, suppress output messages
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        # Reload permissions from disk in case they were updated
        self.original_permissions = self._load_permissions()
        
        # Get config files
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        existing_config_files = [f for f in critical_files if os.path.exists(f)]
        
        total_items = len(self.locked_items) + len(existing_config_files)
        
        if total_items == 0:
            if not silent:
                print("ℹ️  No items to unlock")
            return (0, 0)
        
        if not silent:
            print(f"🔓 Unlocking {len(self.locked_items)} items + {len(existing_config_files)} config files...")
        
        success_count = 0
        failure_count = 0
        
        # Unlock user files/folders
        for item in self.locked_items:
            path = item['path']
            item_name = item['name']
            
            if not os.path.exists(path):
                if not silent:
                    print(f"⚠️  Skipping (doesn't exist): {item_name}")
                failure_count += 1
                continue
            
            try:
                # Get original permissions (default to 644 for files, 755 for folders if not stored)
                if path in self.original_permissions:
                    original_perms = int(self.original_permissions[path], 8)
                else:
                    # Default permissions
                    if item['type'] == 'folder':
                        original_perms = 0o755
                    else:
                        original_perms = 0o644
                
                # Restore permissions
                os.chmod(path, original_perms)
                if not silent:
                    print(f"✅ Unlocked: {item_name} (restored chmod {oct(original_perms)})")
                success_count += 1
                
                # Remove from stored permissions
                if path in self.original_permissions:
                    del self.original_permissions[path]
                
            except Exception as e:
                if not silent:
                    print(f"❌ Failed to unlock {item_name}: {e}")
                failure_count += 1
        
        # Unlock config files
        for file_path in existing_config_files:
            try:
                # Get original permissions (default to 644 if not stored)
                if file_path in self.original_permissions:
                    original_perms = int(self.original_permissions[file_path], 8)
                else:
                    original_perms = 0o644
                
                # Restore permissions
                os.chmod(file_path, original_perms)
                if not silent:
                    print(f"✅ Restored config: {os.path.basename(file_path)} (chmod {oct(original_perms)})")
                success_count += 1
                
                # Remove from stored permissions
                if file_path in self.original_permissions:
                    del self.original_permissions[file_path]
                
            except Exception as e:
                if not silent:
                    print(f"❌ Failed to restore {os.path.basename(file_path)}: {e}")
                failure_count += 1
        
        # Save updated permissions
        self._save_permissions()
        
        if not silent:
            if failure_count == 0:
                print(f"✅ Successfully unlocked {success_count} items")
            else:
                print(f"⚠️  Unlocked {success_count} items, {failure_count} failed")
        
        return (success_count, failure_count)
    
    # Required abstract method implementations (not used in simplified approach)
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """Get metadata for file or folder"""
        try:
            # Get original permissions
            original_mode = os.stat(path).st_mode
            original_perms = oct(stat.S_IMODE(original_mode))
            
            return {
                "name": os.path.basename(path) or path,
                "path": os.path.abspath(path),
                "type": item_type,
                "original_permissions": original_perms,
                "unlock_count": 0,  # Initialize unlock counter
                "added_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """Lock item (stub - use lock_all_with_configs instead)"""
        return False
    
    def _unlock_item(self, item: Dict) -> bool:
        """Unlock item (stub - use unlock_all_with_configs instead)"""
        return False
    
    def _lock_config_file(self, path: str):
        """Lock config file (stub - handled in lock_all_with_configs)"""
        pass
    
    def _unlock_config_file(self, path: str):
        """Unlock config file (stub - handled in unlock_all_with_configs)"""
        pass

