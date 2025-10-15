#!/usr/bin/env python3
"""
Test script for simplified file locking without sudo.
"""

import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.linux.file_lock_manager_linux import FileLockManagerLinux

def test_file_locking():
    """Test that file locking works without sudo"""
    
    # Create temp directory for test
    test_dir = tempfile.mkdtemp(prefix="fadcrypt_test_")
    print(f"📁 Test directory: {test_dir}")
    
    # Create test file
    test_file = os.path.join(test_dir, "test_file.txt")
    with open(test_file, 'w') as f:
        f.write("This is a test file")
    print(f"📄 Created test file: {test_file}")
    
    # Initialize lock manager
    manager = FileLockManagerLinux(test_dir)
    
    # Add file to locked items
    manager.add_item(test_file, "file")
    print(f"➕ Added file to lock manager")
    
    # Test locking
    print("\n🔒 LOCKING FILE...")
    success, failed = manager.lock_all_with_configs()
    
    if success > 0:
        print(f"✅ Lock successful!")
        
        # Try to read locked file
        print("\n📖 Attempting to read locked file...")
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"❌ ERROR: File is still readable! Content: {content}")
            return False
        except PermissionError:
            print("✅ File is properly locked (Permission denied)")
        
        # Test unlocking
        print("\n🔓 UNLOCKING FILE...")
        success, failed = manager.unlock_all_with_configs()
        
        if success > 0:
            print(f"✅ Unlock successful!")
            
            # Try to read unlocked file
            print("\n📖 Attempting to read unlocked file...")
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                print(f"✅ File is readable again! Content: {content}")
                return True
            except PermissionError:
                print("❌ ERROR: File is still locked!")
                return False
        else:
            print(f"❌ Unlock failed!")
            return False
    else:
        print(f"❌ Lock failed!")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Testing Simplified File Locking (No Sudo)")
    print("="*60)
    
    result = test_file_locking()
    
    print("\n" + "="*60)
    if result:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED!")
        sys.exit(1)
