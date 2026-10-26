from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class PasswordHashing:

    def __init__(self):

        self.password_hasher = PasswordHash((Argon2Hasher(),))
    
    def hash_password(self,password: str) -> str:

        return self.password_hasher.hash(password)
    
    def verify_password(self,password: str, password_hash: str) -> bool:

        try:

            return self.password_hasher.verify(password,password_hash)
        
        except Exception: 

            return False
