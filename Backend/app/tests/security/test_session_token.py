import pytest
# pytest Backend/app/tests/security/test_password.py -v
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from security.session_token import SessionToken, SessionTokenError

@pytest.fixture
def session_token_handler():
    return SessionToken()

# Generation token 

def test_generate_token(session_token_handler: SessionToken):

    token = session_token_handler.generate_token()
    assert isinstance(token, str)
    assert len(token) >= 43

#Token uniqueness
def test_generate_token_uniqueness(session_token_handler: SessionToken):
    token1 = session_token_handler.generate_token()
    token2 = session_token_handler.generate_token()
    assert token1 != token2

# Test the hashed token
def test_hash_token_returns_64_char_hex(session_token_handler: SessionToken):

    token = session_token_handler.generate_token()
    hashed_token = session_token_handler.hash_token(token)
    assert isinstance(hashed_token, str)
    assert len(hashed_token) == 64   
    assert all(c in "0123456789abcdef" for c in hashed_token)


# Hashing the same token twice returns the same hash
def test_hash_token_is_deterministic(session_token_handler: SessionToken):

    token = session_token_handler.generate_token()
    hash1 = session_token_handler.hash_token(token)
    hash2 = session_token_handler.hash_token(token)

    assert hash1 == hash2


# Hashing the defferent token twice returns the different hash
def test_different_tokens_produce_different_hashes(session_token_handler: SessionToken):

    token1 = session_token_handler.generate_token()
    token2 = session_token_handler.generate_token()
    
    hash1 = session_token_handler.hash_token(token1)
    hash2 = session_token_handler.hash_token(token2)

    assert hash1 != hash2

@pytest.mark.parametrize("invalid_token", ["", "   ", None, 12345, [], {}])
def test_hash_token_rejects_invalid_input(session_token_handler: SessionToken, invalid_token):
    with pytest.raises(SessionTokenError):
        session_token_handler.hash_token(invalid_token)

@pytest.mark.parametrize("invalid_bytes", [0, 16, 31, -1, "32", True, None])
def test_init_invalid_token_bytes(invalid_bytes):
    with pytest.raises(ValueError):
        SessionToken(token_bytes=invalid_bytes)