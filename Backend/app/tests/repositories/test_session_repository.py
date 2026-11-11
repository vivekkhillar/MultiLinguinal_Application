import sys,uuid
from pathlib import Path
import pytest,pytest_asyncio
from uuid import UUID
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.lifespan import lifespan_instance
from repositories.session_repository import SessionRepository
from datetime import datetime,timezone,timedelta

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
    assert res['token_hash'] == "test-session-token-001"


@pytest.mark.asyncio
async def test_get_by_token_hash_notfound(session_repo):
    res = await session_repo.get_by_token_hash("test-session-token-002")
    assert res is None

@pytest.mark.asyncio
async def test_get_by_id(session_repo):
    res = await session_repo.get_by_id("952418ed-b598-4b20-84f1-8f01bfbf176c")
    assert res is not None
    assert str(res['session_id']) == "952418ed-b598-4b20-84f1-8f01bfbf176c"

@pytest.mark.asyncio
async def test_get_by_id_notfound(session_repo):
    res = await session_repo.get_by_id("952418ed-b598-4b20-84f1-8f01bfbf176A")
    assert res is None


@pytest.mark.asyncio
async def test_create_session(session_repo):
    
    session_id = str(uuid.uuid4())
    token_hash = f"test-token-{uuid.uuid4()}"
    tz = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(tz)
    expires = now + timedelta(hours=1)
    res = await session_repo.create(
                session_id= session_id,
                user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
                token_hash= token_hash,
                device_info= "Test Device",
                user_agent= "Test Browser",
                ip_address= "127.0.0.1",
                created_at = now,
                last_activity_at= now,
                expires_at = expires,
                revoked_at = None, 
                session_status = "ACTIVE")

    assert res is not None
    assert str(res['session_id']) == session_id


@pytest.mark.asyncio
async def test_update_last_activity(session_repo):
    session_id = "a3192c8e-c7a0-4198-b417-87c1665c39ae"
    tz = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(tz)
    last_activity_at = now + timedelta(hours=1)
    res = await session_repo.update_activity(
                session_id= session_id,
                last_activity = last_activity_at)
    assert res is not None
    assert str(res['session_id']) == session_id