#!/usr/bin/env python3
"""
Test script to debug the monitoring flow and identify where the crash happens
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add repo to path
sys.path.insert(0, '/mnt/linux2/repos/FadCrypt')

def test_file_lock_workflow():
    """Test adding a file and starting monitoring"""
    print("\n" + "="*60)
    print("TEST: File Lock Workflow")
    print("="*60)
    
    # Create a temporary file to test
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("# Test file\nprint('hello')\n")
        test_file = f.name
    
    print(f"✅ Created test file: {test_file}")
    
    # Create FadCrypt config folder
    config_folder = os.path.expanduser('~/.config/FadCrypt_test')
    os.makedirs(config_folder, exist_ok=True)
    print(f"✅ Created config folder: {config_folder}")
    
    # Initialize file lock manager
    from core.linux.file_lock_manager_linux import FileLockManagerLinux
    file_lock_manager = FileLockManagerLinux(config_folder)
    print(f"✅ Initialized file lock manager")
    
    # Add the test file
    print(f"\n📝 Adding file to locked items...")
    result = file_lock_manager.add_item(test_file, "file")
    print(f"   Add result: {result}")
    
    # Check if it was added
    locked_items = file_lock_manager.get_locked_items()
    print(f"   Locked items: {len(locked_items)}")
    for item in locked_items:
        print(f"      - {item['path']}")
    
    # Check if config file was saved
    config_file = os.path.join(config_folder, 'apps_config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            locked_count = len(config.get('locked_files_and_folders', []))
            print(f"   Config file saved: {locked_count} locked items")
    
    # Now try to lock it
    print(f"\n🔒 Locking file...")
    success, failed = file_lock_manager.lock_all()
    print(f"   Lock result: {success} success, {failed} failed")
    
    # Check file permissions
    import stat
    st = os.stat(test_file)
    mode = stat.filemode(st.st_mode)
    print(f"   File permissions: {mode}")
    
    # Try to read the file (should fail if locked with 000)
    print(f"\n📖 Attempting to read locked file...")
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"   ❌ File was readable (should be locked!)")
    except PermissionError as e:
        print(f"   ✅ File is locked (PermissionError: {e})")
    
    # Now unlock it
    print(f"\n🔓 Unlocking file...")
    success, failed = file_lock_manager.unlock_all()
    print(f"   Unlock result: {success} success, {failed} failed")
    
    # Clean up
    os.remove(test_file)
    import shutil
    shutil.rmtree(config_folder)
    print(f"\n✅ Cleanup complete")


def test_config_read_when_locked():
    """Test reading config file when it's locked"""
    print("\n" + "="*60)
    print("TEST: Reading Locked Config File")
    print("="*60)
    
    config_folder = os.path.expanduser('~/.config/FadCrypt_test2')
    os.makedirs(config_folder, exist_ok=True)
    
    config_file = os.path.join(config_folder, 'apps_config.json')
    
    # Create a test config
    test_config = {
        'applications': [],
        'locked_files_and_folders': [
            {'path': '/home/test/file.txt', 'type': 'file', 'added_at': '2025-01-01'}
        ]
    }
    
    with open(config_file, 'w') as f:
        json.dump(test_config, f)
    print(f"✅ Created config file with {len(test_config['locked_files_and_folders'])} items")
    
    # Lock the config file
    from core.linux.file_lock_manager_linux import FileLockManagerLinux
    file_lock_manager = FileLockManagerLinux(config_folder)
    file_lock_manager._lock_single_item({'path': config_file, 'type': 'file'})
    print(f"🔒 Locked config file")
    
    # Check permissions
    import stat
    st = os.stat(config_file)
    mode = stat.filemode(st.st_mode)
    print(f"   Config file permissions: {mode}")
    
    # Try to read it WITHOUT unlocking first (should fail)
    print(f"\n📖 Attempting to read locked config WITHOUT unlock...")
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"   ❌ Config was readable (should be locked!)")
    except PermissionError as e:
        print(f"   ✅ Config is locked (PermissionError)")
    
    # Now try WITH temporary unlock
    print(f"\n📖 Attempting to read locked config WITH temporary unlock...")
    try:
        file_lock_manager.temporarily_unlock_config('apps_config.json')
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"   ✅ Config was readable after unlock: {len(config['locked_files_and_folders'])} items")
        file_lock_manager.relock_config('apps_config.json')
        print(f"   ✅ Re-locked config file")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Clean up
    import shutil
    shutil.rmtree(config_folder)
    print(f"\n✅ Cleanup complete")


if __name__ == '__main__':
    try:
        test_file_lock_workflow()
        test_config_read_when_locked()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
