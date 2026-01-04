"""
Encryption Service
Provides AES-256 encryption for profile data at rest.
"""

import os
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import BASE_DIR
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Key storage
KEYS_DIR = BASE_DIR / ".keys"
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# Salt file for password derivation
SALT_FILE = KEYS_DIR / "salt.key"


class EncryptionService:
    """
    AES-256 encryption service for securing profile data.
    
    Uses Fernet (AES-128-CBC with HMAC) for authenticated encryption.
    Master password is never stored - only a verification hash.
    """
    
    def __init__(self):
        """Initialize encryption service."""
        self._fernet: Optional[Fernet] = None
        self._master_password_hash: Optional[str] = None
        self._salt = self._get_or_create_salt()
        self._load_password_hash()
        logger.info("EncryptionService initialized")
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create a new one."""
        if SALT_FILE.exists():
            return SALT_FILE.read_bytes()
        else:
            salt = secrets.token_bytes(32)
            SALT_FILE.write_bytes(salt)
            return salt
    
    def _load_password_hash(self):
        """Load the master password hash if it exists."""
        hash_file = KEYS_DIR / "master.hash"
        if hash_file.exists():
            self._master_password_hash = hash_file.read_text()
    
    def _save_password_hash(self, password_hash: str):
        """Save the master password hash."""
        hash_file = KEYS_DIR / "master.hash"
        hash_file.write_text(password_hash)
        self._master_password_hash = password_hash
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=480000,  # OWASP recommended minimum
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _hash_password(self, password: str) -> str:
        """Create a secure hash of the password for verification."""
        # Use a separate salt for password hashing
        pw_salt = hashlib.sha256(self._salt + b"password_verify").digest()
        return hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            pw_salt, 
            100000
        ).hex()
    
    def is_master_password_set(self) -> bool:
        """Check if a master password has been set."""
        return self._master_password_hash is not None
    
    def set_master_password(self, password: str) -> bool:
        """
        Set the master password for encryption.
        
        Args:
            password: The master password (min 8 chars)
            
        Returns:
            True if successful
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if self._master_password_hash is not None:
            raise ValueError("Master password already set. Use change_password instead.")
        
        # Generate and save password hash
        password_hash = self._hash_password(password)
        self._save_password_hash(password_hash)
        
        # Initialize Fernet with derived key
        key = self._derive_key(password)
        self._fernet = Fernet(key)
        
        logger.info("Master password set successfully")
        return True
    
    def unlock(self, password: str) -> bool:
        """
        Unlock encryption with the master password.
        
        Args:
            password: The master password
            
        Returns:
            True if password is correct and encryption unlocked
        """
        if not self.is_master_password_set():
            raise ValueError("No master password set. Call set_master_password first.")
        
        # Verify password
        password_hash = self._hash_password(password)
        if password_hash != self._master_password_hash:
            logger.warning("Invalid master password attempt")
            return False
        
        # Initialize Fernet
        key = self._derive_key(password)
        self._fernet = Fernet(key)
        
        logger.info("Encryption unlocked successfully")
        return True
    
    def is_unlocked(self) -> bool:
        """Check if encryption is currently unlocked."""
        return self._fernet is not None
    
    def lock(self):
        """Lock encryption (clear the key from memory)."""
        self._fernet = None
        logger.info("Encryption locked")
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the master password.
        
        Args:
            old_password: Current master password
            new_password: New master password
            
        Returns:
            True if successful
        """
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")
        
        # Verify old password
        if not self.unlock(old_password):
            return False
        
        # Update password hash
        new_hash = self._hash_password(new_password)
        self._save_password_hash(new_hash)
        
        # Re-initialize with new key
        key = self._derive_key(new_password)
        self._fernet = Fernet(key)
        
        logger.info("Master password changed successfully")
        return True
    
    def encrypt(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary to a base64 string.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        if not self._fernet:
            raise ValueError("Encryption not unlocked. Call unlock() first.")
        
        json_data = json.dumps(data, ensure_ascii=False)
        encrypted = self._fernet.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt a base64 string to a dictionary.
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            
        Returns:
            Decrypted dictionary
        """
        if not self._fernet:
            raise ValueError("Encryption not unlocked. Call unlock() first.")
        
        encrypted = base64.b64decode(encrypted_data)
        decrypted = self._fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())
    
    def encrypt_field(self, value: str) -> str:
        """Encrypt a single field value."""
        if not self._fernet:
            raise ValueError("Encryption not unlocked")
        encrypted = self._fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a single field value."""
        if not self._fernet:
            raise ValueError("Encryption not unlocked")
        encrypted = base64.b64decode(encrypted_value)
        return self._fernet.decrypt(encrypted).decode()


# Singleton instance
encryption_service = EncryptionService()

