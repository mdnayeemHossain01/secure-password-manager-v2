from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_password(password, key):
    '''
    Encrypt using AES-256-GCM
    
    Args: User Password | 32-byte encryption key
    Returns: Nonce | ciphertext | tag   (all combined in bytes)
    '''
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, password.encode(), None)
    return nonce + ciphertext

def decrypt_password(encrypted_data, key):
    """
    Decrypt using AES-256-GCM

    Args: encrypted_data | key
    Returns: Decrypted password | none (if fails)
    """
    try:
        nonce = encrypted_data[:12] #nonce is first 12 bits
        ciphertext = encrypted_data[12:]

        aesgcm = AESGCM(key)

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext.decode()
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None
