import pytest
import sys
import jwt
from pathlib import Path
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from security.jwt import JWT


@pytest.fixture
def jwt_handler() -> JWT: 
    return JWT()

def test_create_access_token_success(jwt_handler: JWT):
    token = jwt_handler.create_access_token(sub="user-123")
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

def test_decode_access_token_success(jwt_handler: JWT):

    token = jwt_handler.create_access_token(sub = "user-123")
    payload = jwt_handler.decode_access_token(token)

    assert payload['sub'] == "user-123"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload

def test_decode_expired_token(jwt_handler: JWT):

    expired_delta = timedelta(minutes=-5)
    token = jwt_handler.create_access_token(sub="user-123" , expires_delta=expired_delta)

    with pytest.raises(ExpiredSignatureError):
        jwt_handler.decode_access_token(token) 

def test_decode_invalid_signature(jwt_handler: JWT):

    token = jwt_handler.create_access_token(sub="user-123")
    tampered_token = token[:-5] + 'abcde'

    with pytest.raises(InvalidTokenError):
        jwt_handler.decode_access_token(tampered_token)


def test_decode_invalid_token_type(jwt_handler: JWT):
    now = datetime.now(timezone.utc)
    payload = {"sub" : "user-123", "iat": now, "exp" : now + timedelta(minutes=15), "type" : "refresh"}
    raw_token = jwt.encode(payload,jwt_handler.secretKey,algorithm= jwt_handler.algorithm)

    with pytest.raises(InvalidTokenError):
        jwt_handler.decode_access_token(raw_token)

def test_decode_missing_required_claims(jwt_handler: JWT):

    payload = {"type" : "access"}
    raw_token = jwt.encode(payload,jwt_handler.secretKey,algorithm= jwt_handler.algorithm)

    with pytest.raises(InvalidTokenError):
        jwt_handler.decode_access_token(raw_token)