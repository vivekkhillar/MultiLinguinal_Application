# app/tests/redis/test_redis.py
import sys
from pathlib import Path
import pytest
import asyncio

# Ensure Backend/app is in import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from infrastructure.redis.connection import RedisConnectionManager

@pytest.mark.asyncio
async def test_redis_connection_lifecycle():
    """Verify connecting, getting client, PING, and closing."""
    manager = RedisConnectionManager()
    
    # 1. Connect
    await manager.connect()
    client = manager.get_client()
    
    # 2. PING
    pong = await client.ping()
    print(pong) # Gives True 
    assert pong is True or pong == "PONG"
    
    # 3. Close
    await manager.close()
    
    # 4. Verify access rejected after close
    with pytest.raises(RuntimeError, match="Redis client is not connected"):
        manager.get_client()


if __name__ == "__main__":
    asyncio.run(test_redis_connection_lifecycle())
    