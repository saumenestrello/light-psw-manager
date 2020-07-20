import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password_provided):
    #print('Inserisci la password:')
    #password_provided = input() 
    password = password_provided.encode() # Convert to type bytes
    salt = b'\xdaUT\xac\xed\x9e6\xd2f\xd5\x01}\xe89T\xcf' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
    return key
