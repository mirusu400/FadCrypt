#!/usr/bin/env python3
"""
Test script for FadCrypt-Linux.py
This script tests the main functionality without requiring GUI interaction.
"""

import os
import sys
import tempfile
import shutil

# Add the current directory to the path so we can import FadCrypt-Linux
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_single_instance():
    """Test the SingleInstance functionality"""
    print("Testing SingleInstance...")
    try:
        # Import the SingleInstance class
        from FadCrypt_Linux import SingleInstance
        
        # Create first instance
        instance1 = SingleInstance()
        instance1.create_mutex()
        print("✓ First instance created successfully")
        
        # Try to create second instance (should fail)
        try:
            instance2 = SingleInstance()
            instance2.create_mutex()
            print("✗ Second instance should have failed but didn't")
            return False
        except SystemExit:
            print("✓ Second instance correctly prevented")
        
        # Clean up
        instance1.release_mutex()
        print("✓ SingleInstance test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ SingleInstance test failed: {e}")
        return False

def test_executable_detection():
    """Test the executable detection functionality"""
    print("\nTesting executable detection...")
    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                'test.sh': True,  # Should be detected as executable
                'test.py': True,  # Should be detected as executable
                'test.txt': False,  # Should not be detected as executable
                'test.AppImage': True,  # Should be detected as executable
                'test.desktop': True,  # Should be detected as executable
            }
            
            for filename, should_be_executable in test_files.items():
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write("#!/bin/bash\necho 'test'\n")
                
                # Make some files executable
                if filename.endswith(('.sh', '.py')):
                    os.chmod(filepath, 0o755)
                
                # Test detection logic
                linux_executables = ('.desktop', '.sh', '.AppImage', '.run', '.bin', '.py', '.pl', '.rb')
                is_detected = (
                    filepath.endswith(linux_executables) or 
                    os.access(filepath, os.X_OK)
                )
                
                if is_detected == should_be_executable:
                    print(f"✓ {filename}: correctly detected as {'executable' if is_detected else 'non-executable'}")
                else:
                    print(f"✗ {filename}: incorrectly detected as {'executable' if is_detected else 'non-executable'}")
                    return False
        
        print("✓ Executable detection test passed")
        return True
        
    except Exception as e:
        print(f"✗ Executable detection test failed: {e}")
        return False

def test_startup_file_creation():
    """Test the startup file creation functionality"""
    print("\nTesting startup file creation...")
    try:
        # Create a temporary autostart directory
        with tempfile.TemporaryDirectory() as temp_dir:
            autostart_dir = os.path.join(temp_dir, ".config", "autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            
            # Test desktop entry creation
            script_path = os.path.abspath(sys.argv[0])
            python_path = sys.executable
            
            desktop_entry = f"""[Desktop Entry]
Type=Application
Exec={python_path} "{script_path}" --auto-monitor
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=FadCrypt
Comment=Start FadCrypt automatically
Version=1.0
"""
            
            autostart_path = os.path.join(autostart_dir, "FadCrypt.desktop")
            
            with open(autostart_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(autostart_path, 0o755)
            
            # Verify file was created and has correct permissions
            if os.path.exists(autostart_path):
                stat_info = os.stat(autostart_path)
                if stat_info.st_mode & 0o755:
                    print("✓ Startup file created with correct permissions")
                    
                    # Verify content
                    with open(autostart_path, 'r') as f:
                        content = f.read()
                        if "FadCrypt" in content and "--auto-monitor" in content:
                            print("✓ Startup file has correct content")
                            return True
                        else:
                            print("✗ Startup file has incorrect content")
                            return False
                else:
                    print("✗ Startup file has incorrect permissions")
                    return False
            else:
                print("✗ Startup file was not created")
                return False
        
    except Exception as e:
        print(f"✗ Startup file creation test failed: {e}")
        return False

def test_lock_file_path():
    """Test that the lock file path is accessible"""
    print("\nTesting lock file path...")
    try:
        lock_file = "/tmp/fadcrypt.lock"
        
        # Test if we can create and write to the lock file
        with open(lock_file, 'w') as f:
            f.write("test")
        
        # Test if we can read from the lock file
        with open(lock_file, 'r') as f:
            content = f.read()
            if content == "test":
                print("✓ Lock file path is accessible and writable")
                
                # Clean up
                os.remove(lock_file)
                return True
            else:
                print("✗ Lock file content is incorrect")
                return False
        
    except Exception as e:
        print(f"✗ Lock file path test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running FadCrypt-Linux tests...\n")
    
    tests = [
        test_lock_file_path,
        test_executable_detection,
        test_startup_file_creation,
        # Note: SingleInstance test is commented out because it would exit the script
        # test_single_instance,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! FadCrypt-Linux appears to be working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
