# pytest Backend/app/tests/security/test_password.py -v
import sys
import asyncio
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from security.password import PasswordHashing

@pytest.fixture
def hasher():
    return PasswordHashing()
    
def test_hash_password(hasher):

    password = "vivek@12345"
    hashed = hasher.hash_password(password)
    assert hashed is not None
    assert len(hashed) > 0 
    assert hashed != password

def test_verify_correct_password(hasher):

    password = "vivek@12345"
    hashed = hasher.hash_password(password)
    assert hasher.verify_password(password, hashed) is True

def test_verify_incorrect_password(hasher):

    pass1 = "vivek@12334"
    wrong_pass = "Vivek"

    hash_pass1 = hasher.hash_password(pass1)
    assert hasher.verify_password(wrong_pass, hash_pass1) is False

def test_salting_same_password_produces_different_hashes(hasher):

    password = "vivek@12345"

    hash1 = hasher.hash_password(password)
    hash2 = hasher.hash_password(password)

    assert hash1 != hash2 

    assert hasher.verify_password(password,hash1) is True
    assert hasher.verify_password(password,hash2) is True
