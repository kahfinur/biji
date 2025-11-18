#!/usr/bin/env python3
"""
ENCRYPTION MODULE FOR RAT COMMUNICATION
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryption:
    def __init__(self, password=None):
        self.password = password or "default_rat_password_123"
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)
        
    def _generate_key(self, salt=None):
        """Generate encryption key from password"""
        if salt is None:
            salt = b'fixed_salt_123456'  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return key
    
    def encrypt(self, data):
        """Encrypt data"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            encrypted_data = self.cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode('utf-8')
            encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path, output_path=None):
        """Encrypt a file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.encrypt(file_data)
            
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(output_path, 'w') as f:
                f.write(encrypted_data)
            
            return f"File encrypted: {output_path}"
        except Exception as e:
            return f"File encryption failed: {str(e)}"
    
    def decrypt_file(self, encrypted_file_path, output_path=None):
        """Decrypt a file"""
        try:
            if not os.path.exists(encrypted_file_path):
                raise FileNotFoundError(f"File not found: {encrypted_file_path}")
            
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt(encrypted_data)
            
            if output_path is None:
                if encrypted_file_path.endswith('.encrypted'):
                    output_path = encrypted_file_path[:-10]  # Remove .encrypted
                else:
                    output_path = encrypted_file_path + '.decrypted'
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data.encode('utf-8') if isinstance(decrypted_data, str) else decrypted_data)
            
            return f"File decrypted: {output_path}"
        except Exception as e:
            return f"File decryption failed: {str(e)}"
    
    def generate_key_pair(self):
        """Generate RSA key pair for asymmetric encryption"""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                'private_key': private_pem.decode('utf-8'),
                'public_key': public_pem.decode('utf-8')
            }
        except ImportError:
            return "RSA key generation requires cryptography module"
        except Exception as e:
            return f"Key generation failed: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    # Test encryption
    encryption = Encryption("my_secret_password")
    
    # Test string encryption
    test_string = "Hello, this is a secret message!"
    print(f"Original: {test_string}")
    
    encrypted = encryption.encrypt(test_string)
    print(f"Encrypted: {encrypted}")
    
    decrypted = encryption.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test file encryption
    try:
        # Create a test file
        with open('test_file.txt', 'w') as f:
            f.write("This is test file content for encryption testing.")
        
        # Encrypt the file
        result = encryption.encrypt_file('test_file.txt')
        print(result)
        
        # Decrypt the file
        result = encryption.decrypt_file('test_file.txt.encrypted')
        print(result)
        
        # Cleanup
        os.remove('test_file.txt')
        os.remove('test_file.txt.encrypted')
        os.remove('test_file.txt.encrypted.decrypted')
        
    except Exception as e:
        print(f"File test error: {e}")
    
    # Test RSA key generation
    keys = encryption.generate_key_pair()
    if isinstance(keys, dict):
        print("RSA Keys generated successfully")
        print(f"Private key length: {len(keys['private_key'])}")
        print(f"Public key length: {len(keys['public_key'])}")
    else:
        print(keys)