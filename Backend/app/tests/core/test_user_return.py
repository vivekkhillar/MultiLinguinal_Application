import sys
import asyncio
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(APP_DIR))

from repositories.user_repository import UserRepository
from core.lifespan import lifespan_instance


async def main():
    # 1. Await database connection pool initialization
    await lifespan_instance.database_manager.connect()

    try:
        up = UserRepository()
        
        # 2. Pass a valid UUID string (or query an existing user ID from seed data)
        # Example dummy UUID: "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
        test_user_id = "3b4c8756-334c-4904-9222-3974d2cb09fc"
        details = await up.get_by_id(test_user_id)
        return details
    finally:
        # 3. Gracefully dispose engine connection pool
        await lifespan_instance.database_manager.close()


if __name__ == "__main__":
    details = asyncio.run(main())
    print("User details:", details)