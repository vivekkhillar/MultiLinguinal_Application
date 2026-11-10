import sys
from pathlib import Path
import pytest,pytest_asyncio
from uuid import UUID
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.lifespan import lifespan_instance
from repositories.user_repository import UserRepository

@pytest.fixture
def user_repo() -> UserRepository:
    return UserRepository()

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await lifespan_instance.database_manager.connect()
    yield
    await lifespan_instance.database_manager.close()

@pytest.mark.asyncio
async def test_get_by_email_found(user_repo):

    res = await user_repo.get_by_email('testuser001@example.com')
    assert res is not None
    assert res["email"] == "testuser001@example.com"
    
@pytest.mark.asyncio
async def test_get_by_email_notfound(user_repo):

    res = await user_repo.get_by_email('testuser002@example.com')
    assert res is None

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

    res = await user_repo.get_by_id('4b4c8756-334c-4904-9222-3974d2cb09fc')
    assert res is None


