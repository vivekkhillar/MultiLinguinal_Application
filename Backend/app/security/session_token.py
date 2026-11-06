import hashlib  # create hash tokens
import secrets  # create secret tokens

class SessionTokenError(ValueError):
    """Raised when an invalid session token is provided for hashing."""
    pass

class SessionToken:

    TOKEN_BYTES: int = 32

    def __init__(self,token_bytes: int = TOKEN_BYTES):

        if not isinstance(token_bytes, int) or isinstance(token_bytes, bool) or token_bytes < 32:
            raise ValueError("Token bytes must be an integer greater than or equal to 32.")
        
        self.token_bytes: int = token_bytes

    def generate_token(self) -> str:
        """
        Generate a cryptographically secure, URL-safe random token.
        Returns:
            str: URL-safe string containing at least 32 bytes of randomness.
        """
        token = secrets.token_urlsafe(self.token_bytes)
        return token
    
    def hash_token(self, token: str) -> str:

        """ 
        Generate a SHA-256 hexadecimal digest of the raw token.
        
        Args:
            token: The raw session token string to hash.

        Returns:
            str: 64-character lowercase hexadecimal SHA-256 digest.

        Raises:
            SessionTokenError: If the token is empty, whitespace-only, or not a string.
        """

        if not isinstance(token, str) or not token.strip():
            raise SessionTokenError("Token must be a non-empty string.")
        encoded_string = token.encode("utf-8")
        return hashlib.sha256(encoded_string).hexdigest()
