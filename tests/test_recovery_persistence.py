#!/usr/bin/env python3
"""
Recovery Code Persistence Test Suite
Tests the new recovery code persistence logic after password reset.

Test Cases:
1. Recovery codes persist after password reset
2. Used code is marked as consumed
3. Remaining codes are still valid after one is used
4. has_recovery_codes() returns correct status
5. Error messages are specific (used vs invalid vs not found)
6. Multiple password resets with different codes
7. Code file not deleted during password reset
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crypto_manager import CryptoManager
from core.recovery_manager import RecoveryCodeManager
from core.password_manager import PasswordManager


class RecoveryCodePersistenceTest:
    """Test suite for recovery code persistence after password reset"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp(prefix="fadcrypt_persistence_test_")
        self.crypto = CryptoManager()
        self.password = "TestPassword123!@#"
        self.new_password1 = "NewPassword456$%^"
        self.new_password2 = "AnotherPassword789&*()"
        self.recovery_codes_file = os.path.join(self.test_dir, "recovery_codes.json")
        self.password_file = os.path.join(self.test_dir, "encrypted_password.bin")
        self.tests_passed = 0
        self.tests_failed = 0
        print(f"🧪 Recovery Code Persistence Test Suite")
        print(f"📁 Test directory: {self.test_dir}\n")
    
    def cleanup(self):
        """Clean up test directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🗑️  Cleaned up test directory")
    
    def log_pass(self, test_name):
        """Log successful test"""
        self.tests_passed += 1
        print(f"✅ PASS: {test_name}")
    
    def log_fail(self, test_name, reason):
        """Log failed test"""
        self.tests_failed += 1
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")
    
    def test_1_setup_password_and_codes(self):
        """Test 1: Setup - Create password and recovery codes"""
        print("\n" + "="*70)
        print("Test 1: Setup Password and Recovery Codes")
        print("="*70)
        
        try:
            # Create password manager with full file paths
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Create master password
            if not pwd_mgr.create_password(self.password):
                self.log_fail("Setup password creation", "Failed to create password")
                return None
            
            # Generate recovery codes
            success, codes = pwd_mgr.create_recovery_codes()
            if not success or not codes:
                self.log_fail("Setup recovery code generation", "Failed to generate codes")
                return None
            
            print(f"📝 Generated {len(codes)} recovery codes")
            
            # Verify all codes are valid
            for i, code in enumerate(codes):
                is_valid, error = pwd_mgr.verify_recovery_code(code)
                if not is_valid:
                    self.log_fail("Setup code verification", f"Code {i+1} is invalid: {error}")
                    return None
            
            self.log_pass("Setup - Password and recovery codes created")
            return codes
            
        except Exception as e:
            self.log_fail("Setup", f"Exception: {e}")
            return None
    
    def test_2_recovery_file_exists(self):
        """Test 2: Verify recovery codes file exists"""
        print("\n" + "="*70)
        print("Test 2: Recovery Codes File Exists")
        print("="*70)
        
        try:
            if not os.path.exists(self.recovery_codes_file):
                self.log_fail("File existence check", "Recovery codes file not found")
                return False
            
            # Check file contents
            with open(self.recovery_codes_file, 'r') as f:
                data = json.load(f)
            
            if 'version' not in data or data['version'] != '2.0':
                self.log_fail("File format check", f"Invalid version: {data.get('version')}")
                return False
            
            if 'codes' not in data:
                self.log_fail("File format check", "No 'codes' key in file")
                return False
            
            codes_count = len(data['codes'])
            print(f"📄 File contains {codes_count} codes")
            
            self.log_pass("Recovery codes file exists with correct format")
            return True
            
        except Exception as e:
            self.log_fail("File existence check", f"Exception: {e}")
            return False
    
    def test_3_password_reset_with_code(self, codes):
        """Test 3: Reset password using first recovery code"""
        print("\n" + "="*70)
        print("Test 3: Password Reset with Recovery Code")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Use first code to reset password
            first_code = codes[0]
            print(f"🔑 Using code: {first_code[:8]}...")
            
            success, error = pwd_mgr.recover_password_with_code(first_code, self.new_password1)
            if not success:
                self.log_fail("Password reset", f"Reset failed: {error}")
                return False
            
            # Verify new password works
            if not pwd_mgr.verify_password(self.new_password1):
                self.log_fail("Password verification", "New password doesn't work")
                return False
            
            self.log_pass("Password reset with recovery code successful")
            return True
            
        except Exception as e:
            self.log_fail("Password reset", f"Exception: {e}")
            return False
    
    def test_4_recovery_file_still_exists(self):
        """Test 4: CRITICAL - Verify recovery codes file still exists after reset"""
        print("\n" + "="*70)
        print("Test 4: Recovery Codes File Persists After Reset")
        print("="*70)
        
        try:
            if not os.path.exists(self.recovery_codes_file):
                self.log_fail("File persistence check", "❌ Recovery codes file was DELETED after password reset!")
                return False
            
            print("✅ Recovery codes file still exists")
            
            # Check file contents
            with open(self.recovery_codes_file, 'r') as f:
                data = json.load(f)
            
            codes_count = len(data['codes'])
            print(f"📄 File still contains {codes_count} codes")
            
            self.log_pass("Recovery codes file persisted after password reset")
            return True
            
        except Exception as e:
            self.log_fail("File persistence check", f"Exception: {e}")
            return False
    
    def test_5_used_code_marked_consumed(self, codes):
        """Test 5: Verify first code is marked as used"""
        print("\n" + "="*70)
        print("Test 5: Used Code Marked as Consumed")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Try to verify the used code - should fail
            first_code = codes[0]
            is_valid, error = pwd_mgr.verify_recovery_code(first_code)
            
            if is_valid:
                self.log_fail("Used code check", "Used code still shows as valid!")
                return False
            
            # Check error message
            if not error or "already been used" not in error.lower():
                self.log_fail("Error message check", f"Wrong error for used code: {error}")
                return False
            
            print(f"✅ Used code correctly marked as consumed")
            print(f"📝 Error message: {error}")
            
            self.log_pass("Used code marked as consumed with correct error message")
            return True
            
        except Exception as e:
            self.log_fail("Used code check", f"Exception: {e}")
            return False
    
    def test_6_remaining_codes_valid(self, codes):
        """Test 6: CRITICAL - Verify remaining codes are still valid"""
        print("\n" + "="*70)
        print("Test 6: Remaining Codes Still Valid")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Test codes 2-5 (index 1-4)
            remaining_codes = codes[1:]
            valid_count = 0
            
            for i, code in enumerate(remaining_codes):
                is_valid, error = pwd_mgr.verify_recovery_code(code)
                if is_valid:
                    valid_count += 1
                    print(f"✅ Code {i+2}: Valid")
                else:
                    print(f"❌ Code {i+2}: INVALID - {error}")
                    self.log_fail("Remaining codes check", f"Code {i+2} is invalid: {error}")
                    return False
            
            print(f"\n✅ All {valid_count} remaining codes are valid")
            self.log_pass(f"All {valid_count} remaining codes valid after one was used")
            return True
            
        except Exception as e:
            self.log_fail("Remaining codes check", f"Exception: {e}")
            return False
    
    def test_7_has_recovery_codes_accuracy(self):
        """Test 7: Verify has_recovery_codes() returns correct status"""
        print("\n" + "="*70)
        print("Test 7: has_recovery_codes() Accuracy")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Should return True since codes still exist
            has_codes = pwd_mgr.has_recovery_codes()
            if not has_codes:
                self.log_fail("has_recovery_codes check", "Returns False but codes exist!")
                return False
            
            print("✅ has_recovery_codes() correctly returns True")
            
            # Get remaining count
            success, count = pwd_mgr.get_remaining_recovery_codes_count()
            if success:
                print(f"📊 Remaining unused codes: {count}")
            
            self.log_pass("has_recovery_codes() returns correct status")
            return True
            
        except Exception as e:
            self.log_fail("has_recovery_codes check", f"Exception: {e}")
            return False
    
    def test_8_second_password_reset(self, codes):
        """Test 8: Reset password again with second code"""
        print("\n" + "="*70)
        print("Test 8: Second Password Reset with Different Code")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Use second code to reset password again
            second_code = codes[1]
            print(f"🔑 Using code: {second_code[:8]}...")
            
            success, error = pwd_mgr.recover_password_with_code(second_code, self.new_password2)
            if not success:
                self.log_fail("Second password reset", f"Reset failed: {error}")
                return False
            
            # Verify new password works
            if not pwd_mgr.verify_password(self.new_password2):
                self.log_fail("Password verification", "New password doesn't work")
                return False
            
            self.log_pass("Second password reset successful")
            return True
            
        except Exception as e:
            self.log_fail("Second password reset", f"Exception: {e}")
            return False
    
    def test_9_both_codes_marked_used(self, codes):
        """Test 9: Verify both used codes are marked as consumed"""
        print("\n" + "="*70)
        print("Test 9: Both Used Codes Marked as Consumed")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Check first code (used in test 3)
            is_valid1, error1 = pwd_mgr.verify_recovery_code(codes[0])
            if is_valid1:
                self.log_fail("First code status", "First code still shows as valid!")
                return False
            
            # Check second code (used in test 8)
            is_valid2, error2 = pwd_mgr.verify_recovery_code(codes[1])
            if is_valid2:
                self.log_fail("Second code status", "Second code still shows as valid!")
                return False
            
            print("✅ Both used codes correctly marked as consumed")
            print(f"📝 Code 1 error: {error1}")
            print(f"📝 Code 2 error: {error2}")
            
            self.log_pass("Both used codes correctly marked as consumed")
            return True
            
        except Exception as e:
            self.log_fail("Both codes status", f"Exception: {e}")
            return False
    
    def test_10_remaining_codes_still_valid(self, codes):
        """Test 10: Verify codes 3-5 are still valid after two password resets"""
        print("\n" + "="*70)
        print("Test 10: Remaining Codes Valid After Two Resets")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Test codes 3-5 (index 2-4)
            remaining_codes = codes[2:]
            valid_count = 0
            
            for i, code in enumerate(remaining_codes):
                is_valid, error = pwd_mgr.verify_recovery_code(code)
                if is_valid:
                    valid_count += 1
                    print(f"✅ Code {i+3}: Valid")
                else:
                    print(f"❌ Code {i+3}: INVALID - {error}")
                    self.log_fail("Remaining codes check", f"Code {i+3} is invalid: {error}")
                    return False
            
            print(f"\n✅ All {valid_count} remaining codes are valid after TWO password resets")
            self.log_pass(f"All {valid_count} codes valid after two password resets")
            return True
            
        except Exception as e:
            self.log_fail("Remaining codes check", f"Exception: {e}")
            return False
    
    def test_11_error_message_specificity(self, codes):
        """Test 11: Verify error messages are specific and accurate"""
        print("\n" + "="*70)
        print("Test 11: Error Message Specificity")
        print("="*70)
        
        try:
            pwd_mgr = PasswordManager(
                self.password_file,
                recovery_codes_file_path=self.recovery_codes_file
            )
            
            # Test used code error
            _, used_error = pwd_mgr.verify_recovery_code(codes[0])
            if not used_error or "already been used" not in used_error.lower():
                self.log_fail("Used code error message", f"Wrong message: {used_error}")
                return False
            print(f"✅ Used code error: {used_error}")
            
            # Test invalid code error (correct format but wrong code)
            _, invalid_error = pwd_mgr.verify_recovery_code("1234-5678-9ABC-DEFG")
            if not invalid_error or ("not found" not in invalid_error.lower() and "incorrect" not in invalid_error.lower()):
                self.log_fail("Invalid code error message", f"Wrong message: {invalid_error}")
                return False
            print(f"✅ Invalid code error: {invalid_error}")
            
            # Test wrong format error
            _, format_error = pwd_mgr.verify_recovery_code("ABC")
            if not format_error or "format" not in format_error.lower():
                self.log_fail("Format error message", f"Wrong message: {format_error}")
                return False
            print(f"✅ Format error: {format_error}")
            
            self.log_pass("All error messages are specific and accurate")
            return True
            
        except Exception as e:
            self.log_fail("Error message check", f"Exception: {e}")
            return False
    
    def test_12_file_integrity_check(self):
        """Test 12: Verify recovery codes file structure integrity"""
        print("\n" + "="*70)
        print("Test 12: File Structure Integrity")
        print("="*70)
        
        try:
            with open(self.recovery_codes_file, 'r') as f:
                data = json.load(f)
            
            # Check version
            if data.get('version') != '2.0':
                self.log_fail("File integrity", f"Wrong version: {data.get('version')}")
                return False
            
            # Check codes array
            codes = data.get('codes', [])
            if not codes:
                self.log_fail("File integrity", "No codes in file")
                return False
            
            print(f"📄 File contains {len(codes)} codes")
            
            # Check each code entry structure
            for i, code_entry in enumerate(codes):
                required_keys = ['hash', 'salt', 'used']
                for key in required_keys:
                    if key not in code_entry:
                        self.log_fail("File integrity", f"Code {i+1} missing '{key}' field")
                        return False
                
                # Check if used flag is boolean
                if not isinstance(code_entry['used'], bool):
                    self.log_fail("File integrity", f"Code {i+1} 'used' is not boolean")
                    return False
            
            # Count used vs unused
            used_count = sum(1 for c in codes if c.get('used'))
            unused_count = len(codes) - used_count
            
            print(f"📊 Used codes: {used_count}")
            print(f"📊 Unused codes: {unused_count}")
            
            if used_count != 2:
                self.log_fail("File integrity", f"Expected 2 used codes, got {used_count}")
                return False
            
            self.log_pass("File structure integrity verified")
            return True
            
        except Exception as e:
            self.log_fail("File integrity check", f"Exception: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*70)
        print("🚀 STARTING RECOVERY CODE PERSISTENCE TEST SUITE")
        print("="*70)
        
        # Test 1: Setup
        codes = self.test_1_setup_password_and_codes()
        if not codes:
            print("\n❌ Setup failed - cannot continue")
            return
        
        # Test 2: File exists
        if not self.test_2_recovery_file_exists():
            print("\n❌ File existence check failed - cannot continue")
            return
        
        # Test 3: Password reset
        if not self.test_3_password_reset_with_code(codes):
            print("\n❌ Password reset failed - cannot continue")
            return
        
        # Test 4: CRITICAL - File still exists
        if not self.test_4_recovery_file_still_exists():
            print("\n❌ CRITICAL FAILURE: File was deleted!")
            return
        
        # Test 5: Used code marked
        self.test_5_used_code_marked_consumed(codes)
        
        # Test 6: CRITICAL - Remaining codes valid
        if not self.test_6_remaining_codes_valid(codes):
            print("\n❌ CRITICAL FAILURE: Remaining codes invalid!")
            return
        
        # Test 7: has_recovery_codes() accuracy
        self.test_7_has_recovery_codes_accuracy()
        
        # Test 8: Second reset
        if not self.test_8_second_password_reset(codes):
            print("\n❌ Second password reset failed")
            return
        
        # Test 9: Both codes marked used
        self.test_9_both_codes_marked_used(codes)
        
        # Test 10: Remaining codes still valid
        self.test_10_remaining_codes_still_valid(codes)
        
        # Test 11: Error message specificity
        self.test_11_error_message_specificity(codes)
        
        # Test 12: File integrity
        self.test_12_file_integrity_check()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Tests passed: {self.tests_passed}")
        print(f"❌ Tests failed: {self.tests_failed}")
        print(f"📈 Success rate: {self.tests_passed}/{self.tests_passed + self.tests_failed} " +
              f"({100 * self.tests_passed / (self.tests_passed + self.tests_failed):.1f}%)")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! Recovery code persistence is working correctly.")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please review the failures above.")
        
        print("="*70)


def main():
    """Main test runner"""
    test_suite = RecoveryCodePersistenceTest()
    try:
        test_suite.run_all_tests()
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    main()
