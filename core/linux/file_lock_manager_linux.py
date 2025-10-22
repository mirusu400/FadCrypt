"""
Linux File Lock Manager - Uses Fanotify for Kernel-Level File Access Interception

This implementation uses fanotify (via elevated daemon) to intercept file access
at the kernel level, providing true file/folder locking that cannot be bypassed.

Key Features:
- Kernel-level interception (blocks access before file is opened)
- Works for ANY process trying to access the file
- No polling needed - instant detection
- Password dialog shown BEFORE file access is granted
- Seamless integration with existing elevated daemon
"""

import os
import stat
from typing import Dict, List, Optional, Tuple, Callable
from core.file_lock_manager import FileLockManager
from core.linux.elevated_daemon_client import get_elevated_client
from core.linux.fanotify_client import get_fanotify_client


class FileLockManagerLinux(FileLockManager):
    """Linux-specific file lock manager using fanotify"""
    
    def __init__(self, config_folder: str, app_locker=None):
        """
        Initialize Linux file lock manager.
        
        Args:
            config_folder: Path to FadCrypt config folder
            app_locker: Reference to AppLocker instance
        """
        super().__init__(config_folder, app_locker)
        self.daemon_client = get_elevated_client()
        self.password_callback = None  # Set later via set_password_callback
        self.fanotify_client = None
        self.is_monitoring = False
        
        print("[FileLockManagerLinux] Initialized with fanotify support")
    
    def set_password_callback(self, callback: Callable[[str, int], bool]):
        """
        Set the password callback for handling file access requests.
        
        Args:
            callback: Function to call for password verification
                     Signature: callback(file_path, pid) -> bool
        """
        self.password_callback = callback
    
    def start_monitoring(self) -> bool:
        """
        Start fanotify monitoring for locked files/folders.
        
        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            print("⚠️  File monitoring already active")
            return False
        
        if not self.locked_items:
            print("ℹ️  No locked items to monitor")
            return False
        
        if not self.password_callback:
            print("❌ No password callback provided")
            return False
        
        # Check if daemon is available
        if not self.daemon_client.is_available():
            print("❌ Elevated daemon not available")
            return False
        
        # Start fanotify in daemon
        success, msg = self.daemon_client.fanotify_start()
        if not success:
            print(f"❌ Failed to start fanotify: {msg}")
            return False
        
        # Add all locked items to watch
        paths = [item['path'] for item in self.locked_items]
        success, msg = self.daemon_client.fanotify_watch(paths)
        if not success:
            print(f"❌ Failed to add watches: {msg}")
            self.daemon_client.fanotify_stop()
            return False
        
        # Start fanotify client to handle permission requests
        self.fanotify_client = get_fanotify_client(self.password_callback)
        self.fanotify_client.start()
        
        self.is_monitoring = True
        print(f"✅ Fanotify monitoring started for {len(paths)} items")
        return True
    
    def stop_monitoring(self) -> bool:
        """
        Stop fanotify monitoring.
        
        Returns:
            True if monitoring stopped successfully
        """
        if not self.is_monitoring:
            return False
        
        # Stop fanotify client
        if self.fanotify_client:
            self.fanotify_client.stop()
            self.fanotify_client = None
        
        # Stop fanotify in daemon
        self.daemon_client.fanotify_stop()
        
        self.is_monitoring = False
        print("🛑 Fanotify monitoring stopped")
        return True
    
    def update_monitored_items(self):
        """Update the list of monitored items (called when items are added/removed)"""
        if not self.is_monitoring:
            return
        
        # Get current paths
        paths = [item['path'] for item in self.locked_items]
        
        # Remove all watches and re-add
        # (simpler than tracking diffs)
        self.daemon_client.fanotify_stop()
        self.daemon_client.fanotify_start()
        self.daemon_client.fanotify_watch(paths)
        
        print(f"🔄 Updated fanotify watches: {len(paths)} items")
    
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """Get metadata for file or folder"""
        try:
            st = os.stat(path)
            
            return {
                'name': os.path.basename(path),
                'path': path,
                'type': item_type,
                'original_permissions': st.st_mode,
                'filesystem': 'ext4',  # Placeholder
                'lock_method': 'fanotify',
                'unlock_count': 0
            }
        except Exception as e:
            print(f"❌ Error getting metadata for {path}: {e}")
            return None
    
    def _lock_item(self, item: Dict) -> bool:
        """
        Lock a file or folder.
        
        Note: With fanotify, we don't need to change permissions.
        The kernel intercepts access attempts regardless of permissions.
        But we still set read-only as a visual indicator.
        """
        path = item['path']
        item_type = item['type']
        
        try:
            if item_type == 'folder':
                # Set folder to read-only + execute (r-xr-xr-x)
                os.chmod(path, 0o555)
            else:
                # Set file to read-only (r--r--r--)
                os.chmod(path, 0o444)
            
            return True
        except Exception as e:
            print(f"❌ Error locking {path}: {e}")
            return False
    
    def _unlock_item(self, item: Dict) -> bool:
        """Unlock a file or folder"""
        path = item['path']
        
        try:
            # Restore original permissions
            original_mode = item.get('original_permissions', 0o644)
            os.chmod(path, original_mode)
            
            return True
        except Exception as e:
            print(f"❌ Error unlocking {path}: {e}")
            return False
    
    def _lock_config_file(self, path: str):
        """Lock config file (keep readable, prevent modification)"""
        try:
            os.chmod(path, 0o444)  # r--r--r--
        except Exception as e:
            print(f"⚠️  Error locking config {path}: {e}")
    
    def _unlock_config_file(self, path: str):
        """Unlock config file"""
        try:
            os.chmod(path, 0o644)  # rw-r--r--
        except Exception as e:
            print(f"⚠️  Error unlocking config {path}: {e}")
