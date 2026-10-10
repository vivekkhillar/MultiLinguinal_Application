# app/tests/redis/test_health_and_outage.py
import sys
import asyncio
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from main import app
from core.lifespan import lifespan_instance

@pytest.mark.asyncio
async def test_health_endpoint_success():
    """Verify GET /health returns HTTP 200 when services are healthy."""
    # 1. Connect Database & Redis on lifespan_instance
    await lifespan_instance.database_manager.connect()
    await lifespan_instance.redis_manager.connect()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        
        # Useful debug print if something fails
        print(f"Response ({response.status_code}): {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["database"] == "healthy"
        assert data["services"]["redis"] == "healthy"
        print(f"Health Check Passed (200 OK): {data}")

@pytest.mark.asyncio
async def test_health_endpoint_redis_outage():
    """Verify GET /health returns HTTP 503 when Redis is disconnected."""
    # Ensure database is connected
    await lifespan_instance.database_manager.connect()

    # Simulate Redis Outage by closing Redis client
    await lifespan_instance.redis_manager.close()
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "unhealthy"
            assert data["detail"]["services"]["redis"] == "unhealthy"
            print(f"Redis Outage Check Passed (503 Service Unavailable): {data}")
    finally:
        # Recovery: Reconnect Redis & Database after test
        await lifespan_instance.redis_manager.connect()
        await lifespan_instance.database_manager.close()

async def main():
    print("--- Running Health Endpoint Test ---")
    await test_health_endpoint_success()
    print("\n--- Running Redis Outage & Recovery Test ---")
    await test_health_endpoint_redis_outage()

if __name__ == "__main__":
    asyncio.run(main())
