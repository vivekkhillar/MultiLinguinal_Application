import sys
from pathlib import Path
import pytest,pytest_asyncio
from uuid import UUID
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.lifespan import lifespan_instance
from repositories.session_repository import SessionRepository

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await lifespan_instance.database_manager.connect()
    yield
    await lifespan_instance.database_manager.close()


@pytest_asyncio.fixture
async def session_repo() -> SessionRepository:
    async with lifespan_instance.database_manager.get_session() as session:
        yield SessionRepository(session=session)

@pytest.mark.asyncio
async def test_get_by_token_hash(session_repo):
    res = await session_repo.get_by_token_hash("test-session-token-001")
    assert res is not None
