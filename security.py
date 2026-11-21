import os
from cryptography.fernet import Fernet, InvalidToken

def _fernet():
    key = os.getenv("CREDENTIAL_ENCRYPTION_KEY", "").strip()
    if not key:
        raise RuntimeError("CREDENTIAL_ENCRYPTION_KEY is not configured. Set it before saving credentials.")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise RuntimeError("CREDENTIAL_ENCRYPTION_KEY must be a valid Fernet key.") from exc

def encrypt_secret(value):
    return _fernet().encrypt(value.encode()).decode()

def decrypt_secret(value):
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("Could not decrypt saved credential. Check the encryption key.") from exc

def mask_secret(value):
    if not value:
        return ""
    return "••••••••" + value[-4:]
