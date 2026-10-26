from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class Password_Hashing:

    def __init__(self):

        self.Password_Hasher = PasswordHash((Argon2Hasher,()))
    
    def hash_password(self,password: str) -> str:

        return self.Password_Hasher.hash(password)
    
    def verify_password(self,password: str, password_hash: str) -> bool:

        try:

            return self.Password_Hasher.verify(password,password_hash)
        
        except Exception as e:

            return False