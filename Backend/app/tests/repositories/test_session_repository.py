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
    assert res["token_hash"] == "test-session-token-001"

@pytest.mark.asyncio
async def test_get_by_token_hash_notfound(session_repo):
    res = await session_repo.get_by_token_hash("non-existent-token-hash")
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
    
    token_hash = f"test-token-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=7)
    # expires = now + timedelta(days=1)

    res = await session_repo.create(

                    user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
                    token_hash= token_hash,
                    device_info= "Test Device",
                    user_agent= "Test Browser",
                    ip_address= "127.0.0.1",
                    expires_at = expires,

                )

    assert res is not None
    assert str(res['token_hash']) == token_hash
    assert res["session_id"] is not None


@pytest.mark.asyncio
async def test_update_last_activity(session_repo):

    token_hash = f"test-token-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=1)


    res = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,

        )

    session_id = str(res['session_id'])
    res = await session_repo.update_activity(
                session_id= session_id)
    assert res is not None
    assert str(res['session_id']) == session_id


@pytest.mark.asyncio
async def test_update_last_activity_not_found(session_repo):

    session_id = uuid.uuid4()
    res = await session_repo.update_activity(session_id= session_id)
    assert res is None

@pytest.mark.asyncio
async def test_revoke_session(session_repo):

    token_hash = f"test-token-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=1)


    res = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,

        )

    session_id = str(res['session_id'])
    res = await session_repo.revoke(session_id= session_id)
    assert res is not None
    assert str(res['session_id']) == session_id
    assert str(res['session_status']) == "REVOKED"

@pytest.mark.asyncio
async def test_revoke_session_not_found(session_repo):

    session_id = uuid.uuid4()
    res = await session_repo.revoke(session_id= session_id)
    assert res is None

@pytest.mark.asyncio
async def test_revoke_already_revoked_session(session_repo):

    token_hash = f"test-token-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=1)


    res = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,

        )

    session_id = str(res['session_id'])
    first_res = await session_repo.revoke(session_id= session_id)
    assert first_res is not None
    assert str(first_res['session_status']) == "REVOKED"

    second_res = await session_repo.revoke(session_id= session_id)
    assert second_res is None


@pytest.mark.asyncio
async def test_update_token(session_repo):
    
    old_token_hash = f"old-hash-{uuid.uuid4()}"
    new_token_hash = f"new-hash-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days= 7)

    create_session = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= old_token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,
            
        )
    
    assert create_session is not None


    session_id = create_session['session_id']
    update_token = await session_repo.update_token(session_id = session_id,old_token_hash = old_token_hash, new_token_hash=new_token_hash)

    assert update_token["session_id"] == create_session["session_id"]
    assert update_token["token_hash"] == new_token_hash
    assert update_token["last_activity_at"] is not None
    assert update_token["expires_at"] == create_session["expires_at"]


@pytest.mark.asyncio
async def test_update_token_wrong_old_hash_fails(session_repo):

    old_token_hash = f"old-hash-{uuid.uuid4()}"
    expires = datetime.now(timezone.utc) + timedelta(days= 7)

    create_session = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= old_token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,
            
        )
    
    assert create_session is not None
 
    update_token = await session_repo.update_token(session_id = create_session['session_id'],
                                                    old_token_hash = "wrong-token-hash",
                                                    new_token_hash=f"new-hash-{uuid.uuid4()}")

    assert update_token is None



@pytest.mark.asyncio
async def test_update_token_session_revoked(session_repo):

    old_token_hash = f"old-hash-{uuid.uuid4()}"
    expires = datetime.now(timezone.utc) + timedelta(days= 7)

    create_session = await session_repo.create(

            user_id="3b4c8756-334c-4904-9222-3974d2cb09fc",
            token_hash= old_token_hash,
            device_info= "Test Device",
            user_agent= "Test Browser",
            ip_address= "127.0.0.1",
            expires_at = expires,
            
        )
    
    
    assert create_session is not None
    update_session = await session_repo.revoke(session_id = create_session['session_id'])
    update_token = await session_repo.update_token(session_id = create_session['session_id'],
                                                    old_token_hash = "wrong-token-hash",
                                                    new_token_hash=f"new-hash-{uuid.uuid4()}")
    assert update_token is None


