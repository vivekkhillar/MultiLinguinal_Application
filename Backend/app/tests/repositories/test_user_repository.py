import sys
from pathlib import Path
import pytest,pytest_asyncio
from uuid import UUID
from sqlalchemy import text
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.lifespan import lifespan_instance
from repositories.user_repository import UserRepository

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await lifespan_instance.database_manager.connect()
    yield
    await lifespan_instance.database_manager.close()

@pytest_asyncio.fixture
async def user_repo() -> UserRepository:
    async with lifespan_instance.database_manager.get_session() as session:
        yield UserRepository(session=session) 

@pytest.mark.asyncio
async def test_get_by_email_found(user_repo):

    res = await user_repo.get_by_email('testuser001@example.com')
    assert res is not None
    assert res["email"] == "testuser001@example.com"

@pytest.mark.asyncio
async def test_get_by_username_found(user_repo):

    res = await user_repo.get_by_username('testuser001')
    assert res is not None
    assert res["username"] == "testuser001"

@pytest.mark.asyncio
async def test_get_by_username_notfound(user_repo):

    res = await user_repo.get_by_username('testuser002')
    assert res is None


@pytest.mark.asyncio
async def test_get_by_userid_found(user_repo):

    res = await user_repo.get_by_id(UUID("3b4c8756-334c-4904-9222-3974d2cb09fc"))
    assert res is not None
    assert str(res['user_id']) == "3b4c8756-334c-4904-9222-3974d2cb09fc"


@pytest.mark.asyncio
async def test_get_by_userid_notfound(user_repo):

    res = await user_repo.get_by_id(UUID("4b4c8756-334c-4904-9222-3974d2cb09fc"))
    assert res is None


@pytest.mark.asyncio
async def test_create_user(user_repo):

    language_id = await user_repo.session.execute(text("""
            SELECT language_id FROM chat_app.language_configurations LIMIT 1
    """))
    language_id = language_id.scalar_one()
    user_name = "vivek_khillar"

    create_user = await user_repo.create(
        username= user_name,
        email =  "vivekkhillar@gmail.com",
        raw_password = "vivek@12345",
        first_name = "vivek",
        last_name = "khillar",
        preferred_language_id = language_id
    )

    assert create_user is not None
    assert create_user['username'] == user_name


@pytest.mark.asyncio
async def test_create_user_already_exist(user_repo):

    language_id = await user_repo.session.execute(text("""
            SELECT language_id FROM chat_app.language_configurations LIMIT 1
    """))
    language_id = language_id.scalar_one()
    user_name = "vivek_khillar"

    payload = dict(
        username= user_name,
        email =  "vivekkhillar@gmail.com",
        raw_password = "vivek@12345",
        first_name = "vivek",
        last_name = "khillar",
        preferred_language_id = language_id
    )
    create_user = await user_repo.create(**payload)

    assert create_user is not None

    second_same_user = await user_repo.create(**payload)
    assert second_same_user is None
