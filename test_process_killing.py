#!/usr/bin/env python3
"""
Test script to verify process killing functionality
"""

import os
import sys
import time
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent))

from core.linux.file_lock_manager_linux import FileLockManagerLinux
from core.file_access_monitor import FileAccessMonitor

def test_process_killing():
    """Test that processes accessing locked files are killed"""
    
    print("\n" + "="*70)
    print("PROCESS KILLING TEST")
    print("="*70 + "\n")
    
    # Create test file
    test_dir = tempfile.mkdtemp(prefix='fadcrypt_pkill_test_')
    test_file = os.path.join(test_dir, 'locked_test.txt')
    with open(test_file, 'w') as f:
        f.write("This file should be locked and processes killed!\n")
    
    print(f"📁 Test directory: {test_dir}")
    print(f"📄 Test file: {test_file}\n")
    
    # Initialize lock manager
    config_dir = tempfile.mkdtemp(prefix='fadcrypt_config_')
    lock_manager = FileLockManagerLinux(config_dir)
    
    # Add and lock the file
    lock_manager.add_item(test_file, 'file')
    success, failed = lock_manager.lock_all_with_configs()
    
    if success == 0:
        print("❌ Failed to lock file")
        return False
    
    print(f"✅ File locked: {test_file}")
    print(f"   Permissions: {oct(os.stat(test_file).st_mode)}\n")
    
    # Create a password callback that always grants access
    password_callback_triggered = False
    
    def password_callback(file_path):
        nonlocal password_callback_triggered
        password_callback_triggered = True
        print(f"🔐 Password callback triggered for: {file_path}")
        print("   (Auto-granting access for test)\n")
        return True
    
    # Start file access monitor
    monitor = FileAccessMonitor(lock_manager, password_callback)
    monitor.start_monitoring()
    print("✅ File access monitor started\n")
    
    # Test 1: Try to open file with cat (this should be killed)
    print("TEST 1: Opening file with 'cat' command...")
    print("-" * 70)
    
    # Run cat in background
    try:
        proc = subprocess.Popen(['cat', test_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"   Started cat process: PID {proc.pid}")
        
        # Give monitor time to detect and kill
        time.sleep(2)
        
        # Check if process is still alive
        poll = proc.poll()
        if poll is None:
            print("   ⚠️  Process still alive, killing manually...")
            proc.kill()
            proc.wait()
            print("   ⚠️  Warning: Monitor didn't kill the process")
        else:
            print(f"   ✅ Process terminated with code: {poll}")
        
        if password_callback_triggered:
            print("   ✅ Password callback was triggered")
        else:
            print("   ⚠️  Password callback was NOT triggered")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Try to modify file with echo (should trigger modify event)
    print("TEST 2: Modifying file with 'echo' command...")
    print("-" * 70)
    password_callback_triggered = False
    
    try:
        result = subprocess.run(
            ['sh', '-c', f'echo "test" >> {test_file}'],
            capture_output=True,
            timeout=3
        )
        
        print(f"   Command exit code: {result.returncode}")
        if result.stderr:
            print(f"   Stderr: {result.stderr.decode()}")
        
        # Give monitor time to detect
        time.sleep(2)
        
        if password_callback_triggered:
            print("   ✅ Password callback was triggered")
        else:
            print("   ⚠️  Password callback was NOT triggered")
            
    except subprocess.TimeoutExpired:
        print("   ⏱️  Command timed out (expected for locked file)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Cleanup
    print("CLEANUP")
    print("-" * 70)
    monitor.stop_monitoring()
    lock_manager.unlock_all_with_configs()
    
    try:
        os.remove(test_file)
        os.rmdir(test_dir)
        print("✅ Cleanup completed\n")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}\n")
    
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("This test demonstrates the file access monitoring and process killing.")
    print("Note: Some events may not trigger depending on timing and system behavior.")
    print("For full testing, manually try opening locked files with text editors.")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_process_killing()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
