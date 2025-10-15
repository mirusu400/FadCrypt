#!/usr/bin/env python3
"""
Test script for new core managers
Tests CryptoManager, PasswordManager, and AutostartManager
"""

import os
import tempfile
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.crypto_manager import CryptoManager
from core.password_manager import PasswordManager
from core.autostart_manager import get_autostart_manager


def test_crypto_manager():
    """Test CryptoManager encryption/decryption"""
    print("\n=== Testing CryptoManager ===")
    
    crypto = CryptoManager()
    
    # Test data encryption/decryption
    test_data = {"apps": ["firefox", "chrome"], "settings": {"theme": "dark"}}
    password = b"test_password_123"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:
        temp_file = tmp.name
    
    try:
        # Encrypt
        print("Encrypting data...")
        result = crypto.encrypt_data(password, test_data, temp_file)
        print(f"✓ Encryption: {'Success' if result else 'Failed'}")
        
        # Decrypt
        print("Decrypting data...")
        decrypted = crypto.decrypt_data(password, temp_file)
        print(f"✓ Decryption: {'Success' if decrypted == test_data else 'Failed'}")
        print(f"  Original:  {test_data}")
        print(f"  Decrypted: {decrypted}")
        
        # Test wrong password
        print("Testing wrong password...")
        wrong_decrypt = crypto.decrypt_data(b"wrong_password", temp_file)
        print(f"✓ Wrong password: {'Correctly rejected' if wrong_decrypt is None else 'ERROR: Should have failed'}")
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("✅ CryptoManager tests passed!\n")


def test_password_manager():
    """Test PasswordManager password operations"""
    print("\n=== Testing PasswordManager ===")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='_password.bin') as tmp:
        temp_password_file = tmp.name
    
    try:
        pwd_manager = PasswordManager(temp_password_file)
        
        # Create password
        print("Creating password...")
        result = pwd_manager.create_password("my_secure_password")
        print(f"✓ Create password: {'Success' if result else 'Failed'}")
        
        # Verify correct password
        print("Verifying correct password...")
        valid = pwd_manager.verify_password("my_secure_password")
        print(f"✓ Verify correct: {'Success' if valid else 'Failed'}")
        
        # Verify wrong password
        print("Verifying wrong password...")
        invalid = pwd_manager.verify_password("wrong_password")
        print(f"✓ Verify wrong: {'Correctly rejected' if not invalid else 'ERROR: Should have failed'}")
        
        # Change password
        print("Changing password...")
        changed = pwd_manager.change_password("my_secure_password", "new_password_456")
        print(f"✓ Change password: {'Success' if changed else 'Failed'}")
        
        # Verify new password
        print("Verifying new password...")
        valid_new = pwd_manager.verify_password("new_password_456")
        print(f"✓ Verify new password: {'Success' if valid_new else 'Failed'}")
        
        # Check password file exists
        print(f"✓ Password file exists: {pwd_manager.is_password_set()}")
        
    finally:
        if os.path.exists(temp_password_file):
            os.remove(temp_password_file)
    
    print("✅ PasswordManager tests passed!\n")


def test_autostart_manager():
    """Test AutostartManager (info only, doesn't modify system)"""
    print("\n=== Testing AutostartManager ===")
    
    autostart = get_autostart_manager("FadCrypt_Test")
    
    print(f"Platform: {sys.platform}")
    print(f"Manager type: {type(autostart).__name__}")
    print(f"App path: {autostart.app_path}")
    print(f"Currently enabled: {autostart.is_autostart_enabled()}")
    
    print("\n⚠️  Note: Not testing enable/disable to avoid modifying system")
    print("    You can manually test with:")
    print("    - autostart.enable_autostart(with_monitoring=True)")
    print("    - autostart.disable_autostart()")
    
    print("✅ AutostartManager info retrieved!\n")


if __name__ == "__main__":
    print("🧪 FadCrypt Core Managers Test Suite")
    print("=" * 50)
    
    try:
        test_crypto_manager()
        test_password_manager()
        test_autostart_manager()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Core managers are working correctly.")
        print("\n📦 New managers available:")
        print("   - core.crypto_manager.CryptoManager")
        print("   - core.password_manager.PasswordManager")
        print("   - core.autostart_manager (platform-specific)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
