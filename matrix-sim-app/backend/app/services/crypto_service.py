# Crypto Service - Fernet Encryption/Decryption
from cryptography.fernet import Fernet
from typing import Optional
import base64
import hashlib


class CryptoService:
    def __init__(self, key: str):
        # Derive a valid Fernet key from the provided key
        self.key = self._derive_key(key)
        self.fernet = Fernet(self.key)

    def _derive_key(self, key: str) -> bytes:
        """Derive a 32-byte URL-safe base64-encoded key for Fernet"""
        # Hash the key to get consistent 32 bytes
        key_hash = hashlib.sha256(key.encode()).digest()
        # Base64 encode it (Fernet requires URL-safe base64)
        return base64.urlsafe_b64encode(key_hash)

    def encrypt(self, payload: str) -> str:
        """Encrypt a string payload"""
        encrypted = self.fernet.encrypt(payload.encode("utf-8"))
        return encrypted.decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted payload"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode("utf-8"))
            return decrypted.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def validate_token(self, token: str) -> bool:
        """Validate if a token is a valid Fernet token"""
        try:
            self.fernet.decrypt(token.encode("utf-8"))
            return True
        except Exception:
            return False


# Will be initialized with config key
crypto_service: Optional[CryptoService] = None


def get_crypto_service(key: str) -> CryptoService:
    global crypto_service
    if crypto_service is None:
        crypto_service = CryptoService(key)
    return crypto_service
