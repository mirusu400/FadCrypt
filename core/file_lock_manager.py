"""
File and Folder Lock Manager (Base Class)

Abstract base class for platform-specific file/folder locking implementations.
Provides interface for locking files and folders to prevent read/write/delete/rename.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class FileLockManager(ABC):
    """
    Abstract base class for file and folder locking.
    
    Platform-specific implementations must override abstract methods.
    Handles locking, unlocking, permission backup, and metadata management.
    """
    
    def __init__(self, config_folder: str):
        """
        Initialize file lock manager.
        
        Args:
            config_folder: Path to FadCrypt config folder
        """
        self.config_folder = config_folder
        self.locked_items: List[Dict] = []
        self.config_file = os.path.join(config_folder, "locked_files.json")
        self._load_locked_items()
    
    def _load_locked_items(self):
        """Load locked items from config file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.locked_items = json.load(f)
                print(f"📁 Loaded {len(self.locked_items)} locked items from config")
            except Exception as e:
                print(f"⚠️  Error loading locked items: {e}")
                self.locked_items = []
        else:
            self.locked_items = []
    
    def _save_locked_items(self):
        """Save locked items to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.locked_items, f, indent=2)
            print(f"💾 Saved {len(self.locked_items)} locked items to config")
        except Exception as e:
            print(f"❌ Error saving locked items: {e}")
    
    def add_item(self, path: str, item_type: str = "file") -> bool:
        """
        Add file or folder to locked items list.
        
        Args:
            path: Absolute path to file or folder
            item_type: "file" or "folder"
        
        Returns:
            True if added successfully, False otherwise
        """
        if not os.path.exists(path):
            print(f"❌ Path does not exist: {path}")
            return False
        
        # Check if already in list
        if any(item['path'] == path for item in self.locked_items):
            print(f"⚠️  Already in list: {path}")
            return False
        
        # Get metadata
        metadata = self._get_item_metadata(path, item_type)
        if not metadata:
            return False
        
        self.locked_items.append(metadata)
        self._save_locked_items()
        print(f"✅ Added to locked items: {os.path.basename(path)}")
        return True
    
    def remove_item(self, path: str) -> bool:
        """
        Remove file or folder from locked items list.
        
        Args:
            path: Absolute path to file or folder
        
        Returns:
            True if removed successfully, False otherwise
        """
        original_count = len(self.locked_items)
        self.locked_items = [item for item in self.locked_items if item['path'] != path]
        
        if len(self.locked_items) < original_count:
            self._save_locked_items()
            print(f"✅ Removed from locked items: {os.path.basename(path)}")
            return True
        else:
            print(f"⚠️  Not found in locked items: {path}")
            return False
    
    def get_locked_items(self) -> List[Dict]:
        """Get list of all locked items"""
        return self.locked_items.copy()
    
    def lock_all(self) -> Tuple[int, int]:
        """
        Lock all items in the locked items list.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to lock")
            return (0, 0)
        
        print(f"🔒 Locking {len(self.locked_items)} items...")
        success_count = 0
        failure_count = 0
        
        for item in self.locked_items:
            try:
                if self._lock_item(item):
                    success_count += 1
                    print(f"  ✅ Locked: {item['name']}")
                else:
                    failure_count += 1
                    print(f"  ❌ Failed to lock: {item['name']}")
            except Exception as e:
                failure_count += 1
                print(f"  ❌ Error locking {item['name']}: {e}")
        
        print(f"🔒 Lock complete: {success_count} success, {failure_count} failed")
        return (success_count, failure_count)
    
    def unlock_all(self) -> Tuple[int, int]:
        """
        Unlock all items in the locked items list.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.locked_items:
            print("ℹ️  No items to unlock")
            return (0, 0)
        
        print(f"🔓 Unlocking {len(self.locked_items)} items...")
        success_count = 0
        failure_count = 0
        
        for item in self.locked_items:
            try:
                if self._unlock_item(item):
                    success_count += 1
                    print(f"  ✅ Unlocked: {item['name']}")
                else:
                    failure_count += 1
                    print(f"  ❌ Failed to unlock: {item['name']}")
            except Exception as e:
                failure_count += 1
                print(f"  ❌ Error unlocking {item['name']}: {e}")
        
        print(f"🔓 Unlock complete: {success_count} success, {failure_count} failed")
        return (success_count, failure_count)
    
    def lock_fadcrypt_configs(self):
        """
        Lock FadCrypt's own config files to prevent tampering.
        These files remain readable by the app but can't be modified/deleted.
        """
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        
        print("🔒 Locking FadCrypt config files...")
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    self._lock_config_file(file_path)
                    print(f"  ✅ Protected: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"  ⚠️  Failed to protect {os.path.basename(file_path)}: {e}")
    
    def unlock_fadcrypt_configs(self):
        """Unlock FadCrypt's config files"""
        critical_files = [
            os.path.join(self.config_folder, "apps_config.json"),
            os.path.join(self.config_folder, "settings.json"),
            os.path.join(self.config_folder, "encrypted_password.bin"),
            os.path.join(self.config_folder, "monitoring_state.json")
        ]
        
        print("🔓 Unlocking FadCrypt config files...")
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    self._unlock_config_file(file_path)
                    print(f"  ✅ Unprotected: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"  ⚠️  Failed to unprotect {os.path.basename(file_path)}: {e}")
    
    @abstractmethod
    def _get_item_metadata(self, path: str, item_type: str) -> Optional[Dict]:
        """
        Get metadata for file or folder (platform-specific).
        
        Must include: name, path, type, original_permissions, filesystem, lock_method
        """
        pass
    
    @abstractmethod
    def _lock_item(self, item: Dict) -> bool:
        """Lock a file or folder (platform-specific)"""
        pass
    
    @abstractmethod
    def _unlock_item(self, item: Dict) -> bool:
        """Unlock a file or folder (platform-specific)"""
        pass
    
    @abstractmethod
    def _lock_config_file(self, path: str):
        """Lock config file (keep readable, prevent modification)"""
        pass
    
    @abstractmethod
    def _unlock_config_file(self, path: str):
        """Unlock config file"""
        pass
