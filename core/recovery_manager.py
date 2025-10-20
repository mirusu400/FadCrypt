"""
Recovery Manager - Password Recovery Code Operations
Handles generation, storage, verification, and consumption of recovery codes
Provides secure password reset functionality when master password is forgotten
"""

import os
import json
import secrets
import string
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .crypto_manager import CryptoManager


class RecoveryCodeManager:
    """
    Manages password recovery codes for FadCrypt.
    
    Features:
    - Generate 10 unique recovery codes per password setup
    - Store codes securely (encrypted)
    - Verify codes against stored codes
    - Track used/unused codes
    - Support password recovery without original password
    - One-time use enforcement (non-bypassable)
    
    Attributes:
        recovery_codes_file: Path to encrypted recovery codes file
        crypto: CryptoManager instance for encryption
    """
    
    # Recovery code format: 4 groups of 4 alphanumeric chars (case-insensitive)
    # Example: ABCD-EFGH-IJKL-MNOP
    CODE_CHARS = string.ascii_uppercase + string.digits
    CODES_PER_GROUP = 4
    GROUPS_PER_CODE = 4
    TOTAL_CODES = 10
    
    def __init__(self, recovery_codes_file_path: str, crypto_manager: Optional[CryptoManager] = None):
        """
        Initialize the RecoveryCodeManager.
        
        Args:
            recovery_codes_file_path: Full path to recovery_codes.json file
            crypto_manager: Optional CryptoManager instance
        """
        self.recovery_codes_file = recovery_codes_file_path
        self.crypto = crypto_manager or CryptoManager()
        print(f"[RecoveryCodeManager] Initialized with codes file: {recovery_codes_file_path}")
    
    @staticmethod
    def generate_code() -> str:
        """
        Generate a single recovery code in format XXXX-XXXX-XXXX-XXXX.
        
        Returns:
            Generated recovery code (uppercase alphanumeric)
        """
        code_parts = []
        for _ in range(RecoveryCodeManager.GROUPS_PER_CODE):
            part = ''.join(secrets.choice(RecoveryCodeManager.CODE_CHARS) 
                          for _ in range(RecoveryCodeManager.CODES_PER_GROUP))
            code_parts.append(part)
        return '-'.join(code_parts)
    
    @staticmethod
    def generate_codes(count: int = TOTAL_CODES) -> List[str]:
        """
        Generate multiple unique recovery codes.
        
        Args:
            count: Number of codes to generate (default: 10)
            
        Returns:
            List of unique recovery codes
        """
        codes = set()
        while len(codes) < count:
            codes.add(RecoveryCodeManager.generate_code())
        return sorted(list(codes))
    
    def create_recovery_codes(self, password: str) -> Tuple[bool, Optional[List[str]]]:
        """
        Generate and store recovery codes for the given password.
        
        Creates 10 unique recovery codes and stores them encrypted with the password.
        Each code can be used exactly once to recover access.
        
        Args:
            password: Master password to encrypt codes with
            
        Returns:
            Tuple of (success: bool, codes: List[str] or None)
        """
        try:
            # Generate 10 unique codes
            codes = self.generate_codes(self.TOTAL_CODES)
            
            # Create recovery data structure
            recovery_data = {
                'created_at': datetime.now().isoformat(),
                'codes': [
                    {
                        'code': code,
                        'used': False,
                        'used_at': None,
                        'attempts': 0,
                        'created_at': datetime.now().isoformat()
                    }
                    for code in codes
                ]
            }
            
            # Encrypt with password
            password_bytes = password.encode('utf-8')
            success = self.crypto.encrypt_data(
                password=password_bytes,
                data=recovery_data,
                file_path=self.recovery_codes_file
            )
            
            if success:
                print(f"[RecoveryCodeManager] ✅ Created {len(codes)} recovery codes")
                print(f"[RecoveryCodeManager] File now exists: {os.path.exists(self.recovery_codes_file)}")
                return True, codes
            else:
                print("[RecoveryCodeManager] ❌ Failed to create recovery codes")
                return False, None
                
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error creating recovery codes: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def verify_recovery_code(self, password: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if a recovery code is valid and unused.
        
        Args:
            password: Master password to decrypt codes
            code: Recovery code to verify (will be normalized to uppercase)
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
            - (True, None) if code is valid and unused
            - (False, error_msg) if code is invalid/used/incorrect password
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, "Recovery codes not found"
            
            # Normalize code (remove dashes, convert to uppercase)
            normalized_input = code.upper().replace('-', '').replace(' ', '')
            if len(normalized_input) != self.GROUPS_PER_CODE * self.CODES_PER_GROUP:
                return False, "Invalid recovery code format"
            
            # Decrypt recovery data
            password_bytes = password.encode('utf-8')
            recovery_data = self.crypto.decrypt_data(
                password=password_bytes,
                file_path=self.recovery_codes_file,
                suppress_errors=False
            )
            
            if recovery_data is None:
                return False, "Incorrect password or corrupted recovery codes"
            
            # Find and verify code
            for code_entry in recovery_data.get('codes', []):
                stored_code = code_entry['code'].upper().replace('-', '')
                
                if stored_code == normalized_input:
                    # Check if already used
                    if code_entry['used']:
                        return False, "This recovery code has already been used"
                    
                    # Code is valid and unused
                    print(f"[RecoveryCodeManager] ✅ Recovery code verified")
                    return True, None
            
            return False, "Recovery code not found"
            
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error verifying recovery code: {e}")
            return False, f"Error verifying code: {str(e)}"
    
    def consume_recovery_code(self, password: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Mark a recovery code as used (one-time consumption).
        
        CRITICAL: This marks the code as used in the encrypted file.
        This is non-bypassable because:
        1. The used flag is encrypted with the password
        2. Modifying the encrypted file requires knowing the password
        3. Even if file is deleted, all codes become invalid
        
        Args:
            password: Master password
            code: Recovery code to consume
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, "Recovery codes not found"
            
            # Normalize code
            normalized_input = code.upper().replace('-', '').replace(' ', '')
            
            # Decrypt current data
            password_bytes = password.encode('utf-8')
            recovery_data = self.crypto.decrypt_data(
                password=password_bytes,
                file_path=self.recovery_codes_file,
                suppress_errors=False
            )
            
            if recovery_data is None:
                return False, "Incorrect password or corrupted recovery codes"
            
            # Find code and mark as used
            code_found = False
            for code_entry in recovery_data.get('codes', []):
                stored_code = code_entry['code'].upper().replace('-', '')
                
                if stored_code == normalized_input:
                    code_found = True
                    code_entry['used'] = True
                    code_entry['used_at'] = datetime.now().isoformat()
                    break
            
            if not code_found:
                return False, "Recovery code not found"
            
            # Re-encrypt with updated data
            success = self.crypto.encrypt_data(
                password=password_bytes,
                data=recovery_data,
                file_path=self.recovery_codes_file
            )
            
            if success:
                print(f"[RecoveryCodeManager] ✅ Recovery code consumed and marked as used")
                return True, None
            else:
                return False, "Failed to update recovery codes"
                
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error consuming recovery code: {e}")
            return False, f"Error consuming code: {str(e)}"
    
    def delete_recovery_codes(self) -> bool:
        """
        Delete recovery codes file (used during password reset).
        
        This is part of cleanup process when resetting password via recovery code.
        New codes will be generated with the new password.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(self.recovery_codes_file):
                os.remove(self.recovery_codes_file)
                print(f"[RecoveryCodeManager] ✅ Recovery codes deleted")
                return True
            return True  # Already deleted
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error deleting recovery codes: {e}")
            return False
    
    def has_recovery_codes(self) -> bool:
        """
        Check if recovery codes have been set.
        
        Returns:
            True if recovery codes file exists, False otherwise
        """
        return os.path.exists(self.recovery_codes_file)
    
    def get_remaining_codes_count(self, password: str) -> Tuple[bool, Optional[int]]:
        """
        Get count of unused recovery codes.
        
        Args:
            password: Master password to decrypt codes
            
        Returns:
            Tuple of (success: bool, count: Optional[int])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, None
            
            password_bytes = password.encode('utf-8')
            recovery_data = self.crypto.decrypt_data(
                password=password_bytes,
                file_path=self.recovery_codes_file,
                suppress_errors=True
            )
            
            if recovery_data is None:
                return False, None
            
            unused_count = sum(
                1 for code_entry in recovery_data.get('codes', [])
                if not code_entry['used']
            )
            
            return True, unused_count
            
        except:
            return False, None
    
    def list_recovery_codes(self, password: str) -> Tuple[bool, Optional[List[Dict]]]:
        """
        List all recovery codes (for backup/export purposes).
        
        SECURITY: Should only be called immediately after generation.
        Never show this to user after initial creation.
        
        Args:
            password: Master password to decrypt codes
            
        Returns:
            Tuple of (success: bool, codes_list: Optional[List[Dict]])
        """
        try:
            if not os.path.exists(self.recovery_codes_file):
                return False, None
            
            password_bytes = password.encode('utf-8')
            recovery_data = self.crypto.decrypt_data(
                password=password_bytes,
                file_path=self.recovery_codes_file,
                suppress_errors=False
            )
            
            if recovery_data is None:
                return False, None
            
            codes = []
            for entry in recovery_data.get('codes', []):
                codes.append({
                    'code': entry['code'],
                    'used': entry['used'],
                    'used_at': entry.get('used_at'),
                    'created_at': entry.get('created_at')
                })
            
            return True, codes
            
        except Exception as e:
            print(f"[RecoveryCodeManager] ❌ Error listing recovery codes: {e}")
            return False, None

