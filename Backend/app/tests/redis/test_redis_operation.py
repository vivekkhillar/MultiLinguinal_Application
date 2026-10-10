# app/tests/redis/test_redis_operation.py
import sys
import asyncio
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from infrastructure.redis.connection import RedisConnectionManager

@pytest.mark.asyncio
async def test_redis_set_get_delete():
    """Verify writing, reading, and deleting keys in Redis."""
    manager = RedisConnectionManager()
    await manager.connect()
    client = manager.get_client()

    try:
        test_key = "test:key:readwrite"
        test_val = "hello_redis"

        # SET & GET
        await client.set(test_key, test_val)
        val = await client.get(test_key)
        assert val == test_val

        # DELETE
        deleted = await client.delete(test_key)
        assert deleted == 1
        assert await client.get(test_key) is None
    finally:
        await manager.close()

@pytest.mark.asyncio
async def test_redis_ttl_expiration():
    """Verify key automatically expires after TTL."""
    manager = RedisConnectionManager()
    await manager.connect()
    client = manager.get_client()

    try:
        ttl_key = "test:key:ttl"
        # Set 1 second TTL
        await client.set(ttl_key, "expiring_data", ex=1)
        assert await client.get(ttl_key) == "expiring_data"
        print("TTL key created: '{ttl_key}' = 'expiring_data' (TTL-1s)")

        # Wait 1.1s for expiration
        await asyncio.sleep(1.1)
        val_after = await client.get(ttl_key)
        assert val_after is None

        print(f"TTL Expiration Success: Key '{ttl_key}' expired automatically (Value = {val_after})")
    finally:
        await manager.close()

async def main():
    print("---Running Basic Read/Write Test ---")
    await test_redis_set_get_delete()
    print("\n--- Running TTL Expiration Test ---")
    await test_redis_ttl_expiration()

if __name__ == "__main__":
    asyncio.run(main())