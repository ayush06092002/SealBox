# encryption/encryptor.py
from cryptography.fernet import Fernet
from backend.core.config import settings # Import your settings
import os # Keep os import for potential future uses, though not directly used for key here now

# Load the encryption key from settings
# Ensure it's decoded from string to bytes, as Fernet expects bytes
try:
    key = settings.ENCRYPTION_KEY.encode('utf-8')
except AttributeError:
    # This might happen if settings.ENCRYPTION_KEY is None or not a string.
    # Pydantic Settings should typically enforce str if not optional, but good to be defensive.
    raise ValueError("ENCRYPTION_KEY is not set or invalid in environment/config.")

# Initialize the Fernet cipher with the loaded key
cipher = Fernet(key)

def encrypt_file(file_bytes: bytes) -> bytes:
    return cipher.encrypt(file_bytes)

def decrypt_file(file_bytes: bytes) -> bytes:
    return cipher.decrypt(file_bytes)