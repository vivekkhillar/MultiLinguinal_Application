import sys
import asyncio
from pathlib import Path

# Fix import path to point to 'Backend/app' (3 levels up from tests/redis/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest 
from core.lifespan import lifespan_instance

@pytest.mark.asyncio
async def test_redis_client_singleton():
    await lifespan_instance.redis_manager.connect()

    try:
        client1 = lifespan_instance.redis_manager.get_client()
        client2 = lifespan_instance.redis_manager.get_client()

        # Print memory IDs of both client objects
        print(f"Client 1 Memory Address: {id(client1)}")
        print(f"Client 2 Memory Address: {id(client2)}")

        # Checks that client1 and client2 are the EXACT SAME object in memory
        assert client1 is client2
        print("SUCCESS: Both clients share the exact same Redis connection instance!")
    finally:
        # Guaranteed cleanup even if assertion fails
        await lifespan_instance.redis_manager.close()

# Execute the test when running the file directly with python
if __name__ == "__main__":
    asyncio.run(test_redis_client_singleton())
