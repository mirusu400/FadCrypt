"""
Linux File Lock Manager

Implements file/folder locking using chmod + chattr for complete inaccessibility.
Lock order: chmod 000 (remove all permissions) → chattr +i (make immutable)
Unlock order: chattr -i (remove immutable) → chmod original (restore permissions)
"""

import os
import subprocess
import stat
import tempfile
from typing import Dict, Optional, Tuple, List
import time

from core.file_lock_manager import FileLockManager


class FileLockManagerLinux(FileLockManager):
    """Linux implementation of file/folder locking using chmod + chattr"""
    
    def lock_all_with_configs(self) -> Tuple[int, int]:
        """
        Lock all user items AND config files with a single pkexec prompt.
        This combines lock_all() and lock_fadcrypt_configs() into one operation.
        
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
        
        print(f"🔒 Locking {len(self.locked_items)} items + {len(existing_config_files)} config files with single password prompt...")
        
        # Create unified batch script
        script_content = "#!/bin/bash\nset -e\n\n"
        
        # Add user files/folders
        for item in self.locked_items:
            path = item['path']
            lock_method = item.get('lock_method', 'chmod_chattr')
            item_type = item['type']
            
            if not os.path.exists(path):
                print(f"⚠️  Skipping (doesn't exist): {item['name']}")
                continue
            
            script_content += f"# Locking user item: {item['name']}\n"
            script_content += f"chmod 000 '{path}'\n"
            
            if lock_method == "chmod_chattr":
                if item_type == 'folder':
                    script_content += f"chattr -R +i '{path}'\n"
                else:
                    script_content += f"chattr +i '{path}'\n"
            
            script_content += "\n"
        
        # Add config files (chattr +i only, keep readable)
        for file_path in existing_config_files:
            script_content += f"# Locking config: {os.path.basename(file_path)}\n"
            script_content += f"chattr +i '{file_path}'\n\n"
        
        # Write script to temp file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            # Execute with single pkexec prompt
            print("  🔑 Requesting elevated privileges (enter password once)...")
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up script
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                print(f"✅ Successfully locked {len(self.locked_items)} items + {len(existing_config_files)} config files")
                return (total_items, 0)
            elif result.returncode == 126 or result.returncode == 127:
                print(f"⚠️  Authentication cancelled - nothing locked")
                return (0, total_items)
            else:
                print(f"❌ Batch lock failed: {result.stderr}")
                return (0, total_items)
                
        except Exception as e:
            print(f"❌ Error creating unified batch lock script: {e}")
            return (0, total_items)
    
    def unlock_all_with_configs(self) -> Tuple[int, int]:
        """
        Unlock all user items AND config files with a single pkexec prompt.
        This combines unlock_all() and unlock_fadcrypt_configs() into one operation.
        
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
            print("ℹ️  No items to unlock")
            return (0, 0)
        
        print(f"🔓 Unlocking {len(self.locked_items)} items + {len(existing_config_files)} config files with single password prompt...")
        
        # Create unified batch script
        script_content = "#!/bin/bash\n\n"
        
        # Add user files/folders
        for item in self.locked_items:
            path = item['path']
            lock_method = item.get('lock_method', 'chmod_chattr')
            original_permissions = item.get('original_permissions', '644')
            item_type = item['type']
            
            if not os.path.exists(path):
                print(f"⚠️  Skipping (doesn't exist): {item['name']}")
                continue
            
            script_content += f"# Unlocking user item: {item['name']}\n"
            if lock_method == "chmod_chattr":
                if item_type == 'folder':
                    script_content += f"chattr -R -i '{path}' 2>/dev/null || true\n"
                else:
                    script_content += f"chattr -i '{path}' 2>/dev/null || true\n"
            
            script_content += f"chmod {original_permissions} '{path}'\n\n"
        
        # Add config files
        for file_path in existing_config_files:
            script_content += f"# Unlocking config: {os.path.basename(file_path)}\n"
            script_content += f"chattr -i '{file_path}' 2>/dev/null || true\n\n"
        
        # Write script to temp file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            # Execute with single pkexec prompt
            print("  🔑 Requesting elevated privileges (enter password once)...")
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up script
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                print(f"✅ Successfully unlocked {len(self.locked_items)} items + {len(existing_config_files)} config files")
                return (total_items, 0)
            elif result.returncode == 126 or result.returncode == 127:
                print(f"⚠️  Authentication cancelled - items remain locked")
                return (0, total_items)
            else:
                print(f"❌ Batch unlock failed: {result.stderr}")
                return (0, total_items)
                
        except Exception as e:
            print(f"❌ Error creating unified batch unlock script: {e}")
            return (0, total_items)
    
    def lock_all(self) -> Tuple[int, int]:
        """
        Lock all items using a single pkexec prompt (batch operation).
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to lock")
            return (0, 0)
        
        print(f"🔒 Locking {len(self.locked_items)} items with single password prompt...")
        
        # Create batch script
        script_content = "#!/bin/bash\nset -e\n\n"
        
        for item in self.locked_items:
            path = item['path']
            lock_method = item.get('lock_method', 'chmod_chattr')
            item_type = item['type']
            
            if not os.path.exists(path):
                print(f"⚠️  Skipping (doesn't exist): {item['name']}")
                continue
            
            # Add chmod command
            script_content += f"# Locking: {item['name']}\n"
            script_content += f"chmod 000 '{path}'\n"
            
            # Add chattr command if applicable
            if lock_method == "chmod_chattr":
                if item_type == 'folder':
                    script_content += f"chattr -R +i '{path}'\n"
                else:
                    script_content += f"chattr +i '{path}'\n"
            
            script_content += "\n"
        
        # Write script to temp file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Execute with single pkexec prompt
            print("  🔑 Requesting elevated privileges (enter password once)...")
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up script
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                print(f"✅ Successfully locked {len(self.locked_items)} items")
                return (len(self.locked_items), 0)
            elif result.returncode == 126 or result.returncode == 127:
                # User cancelled pkexec or authentication failed
                print(f"⚠️  Authentication cancelled - items NOT locked")
                return (0, len(self.locked_items))
            else:
                print(f"❌ Batch lock failed: {result.stderr}")
                return (0, len(self.locked_items))
                
        except Exception as e:
            print(f"❌ Error creating batch lock script: {e}")
            # Fallback to individual locking
            return super().lock_all()
    
    def unlock_all(self) -> Tuple[int, int]:
        """
        Unlock all items using a single pkexec prompt (batch operation).
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to unlock")
            return (0, 0)
        
        print(f"🔓 Unlocking {len(self.locked_items)} items with single password prompt...")
        
        # Create batch script
        script_content = "#!/bin/bash\n\n"
        
        for item in self.locked_items:
            path = item['path']
            lock_method = item.get('lock_method', 'chmod_chattr')
            original_permissions = item.get('original_permissions', '644')
            item_type = item['type']
            
            if not os.path.exists(path):
                print(f"⚠️  Skipping (doesn't exist): {item['name']}")
                continue
            
            # Add chattr removal if applicable
            script_content += f"# Unlocking: {item['name']}\n"
            if lock_method == "chmod_chattr":
                if item_type == 'folder':
                    script_content += f"chattr -R -i '{path}' 2>/dev/null || true\n"
                else:
                    script_content += f"chattr -i '{path}' 2>/dev/null || true\n"
            
            # Add chmod restoration
            script_content += f"chmod {original_permissions} '{path}'\n"
            script_content += "\n"
        
        # Write script to temp file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Execute with single pkexec prompt
            print("  🔑 Requesting elevated privileges (enter password once)...")
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up script
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                print(f"✅ Successfully unlocked {len(self.locked_items)} items")
                return (len(self.locked_items), 0)
            elif result.returncode == 126 or result.returncode == 127:
                # User cancelled pkexec or authentication failed
                print(f"⚠️  Authentication cancelled - items remain locked")
                return (0, len(self.locked_items))
            else:
                print(f"❌ Batch unlock failed: {result.stderr}")
                return (0, len(self.locked_items))
                
        except Exception as e:
            print(f"❌ Error creating batch unlock script: {e}")
            # Fallback to individual unlocking
            return super().unlock_all()
    
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
    
    def lock_fadcrypt_configs(self):
        """Lock FadCrypt's config files using batch operation (single password prompt)"""
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        
        # Filter to existing files
        existing_files = [f for f in critical_files if os.path.exists(f)]
        
        if not existing_files:
            print("ℹ️  No config files to lock")
            return
        
        print(f"🔒 Locking {len(existing_files)} FadCrypt config files...")
        
        # Create batch script for all config files
        script_content = "#!/bin/bash\nset -e\n\n"
        
        for file_path in existing_files:
            script_content += f"# Locking config: {os.path.basename(file_path)}\n"
            script_content += f"chattr +i '{file_path}'\n\n"
        
        # Execute batch script
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                for file_path in existing_files:
                    print(f"  ✅ Protected: {os.path.basename(file_path)}")
            elif result.returncode == 126 or result.returncode == 127:
                # User cancelled pkexec or authentication failed
                print(f"  ⚠️  Authentication cancelled - config files NOT protected")
            else:
                print(f"  ⚠️  Batch config lock failed: {result.stderr}")
                
        except Exception as e:
            print(f"  ⚠️  Error locking configs: {e}")
    
    def unlock_fadcrypt_configs(self):
        """Unlock FadCrypt's config files using batch operation (single password prompt)"""
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        
        # Filter to existing files
        existing_files = [f for f in critical_files if os.path.exists(f)]
        
        if not existing_files:
            print("ℹ️  No config files to unlock")
            return
        
        print(f"🔓 Unlocking {len(existing_files)} FadCrypt config files...")
        
        # Create batch script for all config files
        script_content = "#!/bin/bash\n\n"
        
        for file_path in existing_files:
            script_content += f"# Unlocking config: {os.path.basename(file_path)}\n"
            script_content += f"chattr -i '{file_path}' 2>/dev/null || true\n\n"
        
        # Execute batch script
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                script_path = f.name
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            result = subprocess.run(
                ['pkexec', 'bash', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                for file_path in existing_files:
                    print(f"  ✅ Unprotected: {os.path.basename(file_path)}")
            elif result.returncode == 126 or result.returncode == 127:
                # User cancelled pkexec or authentication failed
                print(f"  ⚠️  Authentication cancelled - config files remain protected")
            else:
                print(f"  ⚠️  Batch config unlock failed: {result.stderr}")
                
        except Exception as e:
            print(f"  ⚠️  Error unlocking configs: {e}")
    
    def _lock_config_file(self, path: str):
        """
        Lock config file (keep readable by FadCrypt, prevent modification/deletion).
        Only use chattr +i to prevent modifications while keeping readable.
        Note: This is kept for compatibility but lock_fadcrypt_configs() should be used instead.
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
        """
        Unlock config file.
        Note: This is kept for compatibility but unlock_fadcrypt_configs() should be used instead.
        """
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
