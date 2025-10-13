"""
Password Manager - Master Password Operations
Handles master password creation, verification, and changes
"""

import os
from typing import Optional, Callable
from .crypto_manager import CryptoManager


class PasswordManager:
    """
    Manages the master password for FadCrypt.
    
    The master password is used to encrypt/decrypt all application
    configurations and settings. The password itself is stored as an
    encrypted hash in encrypted_password.bin.
    
    Attributes:
        crypto: CryptoManager instance for encryption operations
        password_file: Path to encrypted password file
        cached_password: In-memory cache of password (bytes)
    """
    
    def __init__(self, password_file_path: str, crypto_manager: Optional[CryptoManager] = None):
        """
        Initialize the PasswordManager.
        
        Args:
            password_file_path: Full path to encrypted_password.bin file
            crypto_manager: Optional CryptoManager instance (creates new if None)
        """
        self.password_file = password_file_path
        self.crypto = crypto_manager or CryptoManager()
        self.cached_password: Optional[bytes] = None
    
    def create_password(self, password: str) -> bool:
        """
        Create/update the master password.
        
        Encrypts the password with itself and stores in password_file.
        This allows verification without storing plaintext.
        
        Args:
            password: New master password (as string)
            
        Returns:
            True if password created successfully, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            
            # Encrypt the password with itself
            success = self.crypto.encrypt_password_hash(
                password=password_bytes,
                password_hash=password_bytes,
                file_path=self.password_file
            )
            
            if success:
                self.cached_password = password_bytes
                print("[PasswordManager] Master password created successfully")
                return True
            else:
                print("[PasswordManager] Failed to create master password")
                return False
                
        except Exception as e:
            print(f"[PasswordManager] Error creating password: {e}")
            return False
    
    def verify_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the master password.
        
        Args:
            password: Password to verify (as string)
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            if not os.path.exists(self.password_file):
                print("[PasswordManager] Password file not found")
                return False
            
            password_bytes = password.encode('utf-8')
            
            # Try to decrypt the password hash
            decrypted_hash = self.crypto.decrypt_password_hash(
                password=password_bytes,
                file_path=self.password_file
            )
            
            if decrypted_hash is None:
                return False
            
            # Compare with original password
            is_valid = (password_bytes == decrypted_hash)
            
            if is_valid:
                self.cached_password = password_bytes
                print("[PasswordManager] Password verified successfully")
            else:
                print("[PasswordManager] Password verification failed")
            
            return is_valid
            
        except Exception as e:
            print(f"[PasswordManager] Error verifying password: {e}")
            return False
    
    def change_password(
        self,
        old_password: str,
        new_password: str,
        re_encrypt_callback: Optional[Callable[[bytes], bool]] = None
    ) -> bool:
        """
        Change the master password.
        
        Args:
            old_password: Current master password
            new_password: New master password
            re_encrypt_callback: Optional callback to re-encrypt configs with new password.
                                Should accept new password (bytes) and return success bool.
            
        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            # Verify old password
            if not self.verify_password(old_password):
                print("[PasswordManager] Old password is incorrect")
                return False
            
            # Create new password
            if not self.create_password(new_password):
                print("[PasswordManager] Failed to create new password")
                return False
            
            # Re-encrypt all configs with new password (if callback provided)
            if re_encrypt_callback:
                new_password_bytes = new_password.encode('utf-8')
                if not re_encrypt_callback(new_password_bytes):
                    print("[PasswordManager] Warning: Failed to re-encrypt some configs")
                    # Don't revert password change - user can manually re-encrypt
            
            print("[PasswordManager] Password changed successfully")
            return True
            
        except Exception as e:
            print(f"[PasswordManager] Error changing password: {e}")
            return False
    
    def load_password(self) -> Optional[bytes]:
        """
        Load the cached password or prompt for it.
        
        Note: In GUI apps, this should prompt the user via a dialog.
        For now, returns cached password if available.
        
        Returns:
            Cached password as bytes, or None if not cached
        """
        return self.cached_password
    
    def is_password_set(self) -> bool:
        """
        Check if a master password has been set.
        
        Returns:
            True if password file exists, False otherwise
        """
        return os.path.exists(self.password_file)
    
    def clear_cache(self):
        """Clear the cached password from memory."""
        self.cached_password = None
        print("[PasswordManager] Password cache cleared")
    
    def get_password_bytes(self) -> Optional[bytes]:
        """
        Get the cached password in bytes format.
        
        Returns:
            Cached password as bytes, or None if not cached
        """
        return self.cached_password
