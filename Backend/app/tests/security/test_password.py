# app/tests/redis/test_health_and_outage.py
import sys
import asyncio
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from security.password import PasswordHashing

def main():

    pass1 = "vivek@12345"
    pass2 = "vivek@11232"
    _PasswordHashing =PasswordHashing()

    print (_PasswordHashing.hash_password(pass1))
    print (_PasswordHashing.hash_password(pass2))

    print(_PasswordHashing.verify_password(pass1,_PasswordHashing.hash_password(pass1)))
    return None
if __name__ == "__main__":
    main()