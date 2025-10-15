#!/usr/bin/env python3
"""
Test read-only file locking strategy (chmod 444/555)
Verifies that files can be monitored but not modified
"""

import os
import sys
import tempfile
import time

def test_readonly_locking():
    """Test read-only file locking"""
    print("=" * 70)
    print("READ-ONLY FILE LOCKING TEST")
    print("=" * 70)
    
    # Create test file
    test_dir = tempfile.mkdtemp(prefix="fadcrypt_readonly_test_")
    test_file = os.path.join(test_dir, "test_file.txt")
    test_folder = os.path.join(test_dir, "test_folder")
    os.makedirs(test_folder)
    
    with open(test_file, 'w') as f:
        f.write("Original content\n")
    
    with open(os.path.join(test_folder, "folder_file.txt"), 'w') as f:
        f.write("File in folder\n")
    
    print(f"\n📁 Test directory: {test_dir}")
    print(f"📄 Test file: {test_file}")
    print(f"📁 Test folder: {test_folder}")
    
    try:
        # Test 1: Lock file with chmod 444
        print("\n" + "=" * 70)
        print("TEST 1: Lock file with chmod 444 (read-only)")
        print("=" * 70)
        
        os.chmod(test_file, 0o444)
        print("✅ File locked with chmod 444")
        
        # Verify we can still read
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"✅ Can still READ file: {content.strip()}")
        except Exception as e:
            print(f"❌ Cannot read file: {e}")
            return False
        
        # Verify we CANNOT write
        try:
            with open(test_file, 'w') as f:
                f.write("Modified content\n")
            print(f"❌ File is NOT locked (write succeeded)")
            return False
        except PermissionError:
            print(f"✅ Cannot WRITE to file (Permission denied) - CORRECT!")
        
        # Test 2: Lock folder with chmod 555
        print("\n" + "=" * 70)
        print("TEST 2: Lock folder with chmod 555 (read-only + executable)")
        print("=" * 70)
        
        os.chmod(test_folder, 0o555)
        print("✅ Folder locked with chmod 555")
        
        # Verify we can still list contents
        try:
            contents = os.listdir(test_folder)
            print(f"✅ Can still LIST folder contents: {contents}")
        except Exception as e:
            print(f"❌ Cannot list folder: {e}")
            return False
        
        # Verify we can still read files inside
        try:
            folder_file = os.path.join(test_folder, "folder_file.txt")
            with open(folder_file, 'r') as f:
                content = f.read()
            print(f"✅ Can still READ files inside folder: {content.strip()}")
        except Exception as e:
            print(f"❌ Cannot read file inside folder: {e}")
            return False
        
        # Verify we CANNOT create new files
        try:
            new_file = os.path.join(test_folder, "new_file.txt")
            with open(new_file, 'w') as f:
                f.write("New file\n")
            print(f"❌ Folder is NOT locked (file creation succeeded)")
            return False
        except PermissionError:
            print(f"✅ Cannot CREATE files in folder (Permission denied) - CORRECT!")
        
        # Test 3: Temporary unlock simulation
        print("\n" + "=" * 70)
        print("TEST 3: Temporary unlock (chmod 644) and re-lock")
        print("=" * 70)
        
        # Unlock file
        os.chmod(test_file, 0o644)
        print("✅ File temporarily unlocked with chmod 644")
        
        # Verify we can now write
        try:
            with open(test_file, 'w') as f:
                f.write("Modified content after unlock\n")
            print(f"✅ Can WRITE to unlocked file")
        except Exception as e:
            print(f"❌ Cannot write to unlocked file: {e}")
            return False
        
        # Re-lock
        print("⏳ Waiting 2 seconds before re-locking...")
        time.sleep(2)
        os.chmod(test_file, 0o444)
        print("✅ File re-locked with chmod 444")
        
        # Verify write blocked again
        try:
            with open(test_file, 'w') as f:
                f.write("Should fail\n")
            print(f"❌ File is NOT re-locked (write succeeded)")
            return False
        except PermissionError:
            print(f"✅ Cannot WRITE after re-lock (Permission denied) - CORRECT!")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nSummary:")
        print("  - chmod 444 allows reading but blocks writing ✅")
        print("  - chmod 555 allows listing/reading but blocks modifications ✅")
        print("  - Temporary unlock (644) allows writing ✅")
        print("  - Re-lock (444) blocks writing again ✅")
        print("\n📝 This locking strategy allows watchdog to monitor files")
        print("   while preventing unauthorized modifications!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            import shutil
            os.system(f"chmod -R 777 {test_dir} 2>/dev/null")
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    print("\n🚀 Starting read-only locking test...\n")
    success = test_readonly_locking()
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
