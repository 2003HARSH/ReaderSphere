import os
from cryptography.fernet import Fernet

try:
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
    cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print("CRITICAL: ENCRYPTION_KEY not found or invalid. Message encryption is disabled.")
    print("Please generate a key and add it to your .env file.")
    cipher_suite = None

def encrypt_message(message: str) -> str:
    """Encrypts a plain text message."""
    if not cipher_suite or not message:
        return message # Return plain text if encryption is not configured
    
    encrypted_text = cipher_suite.encrypt(message.encode())
    return encrypted_text.decode()

def decrypt_message(encrypted_message: str) -> str:
    """Decrypts an encrypted message."""
    if not cipher_suite or not encrypted_message:
        return encrypted_message # Return as is if encryption is not configured or message is empty

    try:
        decrypted_text = cipher_suite.decrypt(encrypted_message.encode())
        return decrypted_text.decode()
    except Exception:
        # This can happen if you try to decrypt a message that was never encrypted
        # (e.g., old messages from before you added this feature).
        return encrypted_message
