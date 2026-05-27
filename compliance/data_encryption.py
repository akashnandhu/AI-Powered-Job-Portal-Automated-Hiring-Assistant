import os
import base64
from cryptography.fernet import Fernet

class DataEncryptionManager:
    """
    Handles AES encryption and decryption for sensitive candidate data 
    (e.g., storing PII or interview transcripts securely at rest).
    """
    def __init__(self, key_file="compliance/secret.key"):
        self.key_file = key_file
        self._key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self._key)

    def _load_or_generate_key(self) -> bytes:
        """Loads an existing key or generates a new one if it doesn't exist."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            # Generate a new AES key (in production, use a secure Key Management Service)
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def encrypt_data(self, plaintext: str) -> str:
        """Encrypts sensitive plaintext data."""
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt_data(self, encrypted_text: str) -> str:
        """Decrypts AES-encrypted data back to plaintext."""
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt data. Invalid key or corrupted data: {str(e)}")

# Example Usage
if __name__ == "__main__":
    encryption_manager = DataEncryptionManager()
    
    # 1. We have sensitive transcript data
    sensitive_transcript = "Candidate phone number is +1-555-0198 and email is candidate@example.com."
    print("Original Data:", sensitive_transcript)
    
    # 2. Encrypt it before saving to the database or file system
    encrypted_data = encryption_manager.encrypt_data(sensitive_transcript)
    print("\nEncrypted Data (Saved to DB/Storage):\n", encrypted_data)
    
    # 3. Decrypt it when an authorized user (e.g., Recruiter) requests access
    decrypted_data = encryption_manager.decrypt_data(encrypted_data)
    print("\nDecrypted Data (For Authorized View):\n", decrypted_data)
